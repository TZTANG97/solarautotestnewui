"""DEWETRON 数据采集模块（SQLite 版本）。

提供 DewetronDataCollector 类，用于实时采集 DEWETRON 测量数据并存储到 SQLite。
支持闪变、谐波等多测试项目复用，支持版本回溯。

数据库路径: database/db.sqlite（固定）
初始化脚本: database/init.sql（启动时自动检查）

用法:
    from devices.dewetron_data_collector import DewetronDataCollector, init_database

    # 项目启动时初始化数据库
    init_database()

    collector = DewetronDataCollector(dewetron_controller, logger)
    collector.start()  # 启动守护线程

    # 测试开始时
    collector.prepare(fields=['U1_tRMS@AC', ...], rate_text='Default',
                      test_type='flicker', save_path='D:/data/test.csv')
    collector.start_gathering()  # 配置设备

    # :ACQUISITION:START 发送后
    collector.on_acquisition_started()  # 正式开始采集

    # 测试结束时
    collector.stop_gathering()  # 停止采集，更新 de_test_runs

    # 导出 CSV（可选）
    collector.export_to_csv()

    collector.stop()  # 程序退出时
"""

import csv
import json
import os
import sqlite3
import time
import threading
import re
from dataclasses import dataclass, field


# 数据库固定路径
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
DB_PATH = os.path.join(DB_DIR, 'db.sqlite')
INIT_SQL_PATH = os.path.join(DB_DIR, 'init.sql')


def _table_exists(conn, table_name):
    """Return whether an SQLite table already exists."""
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone() is not None


def _ensure_column(conn, table_name, column_name, definition):
    """Add a missing SQLite column without rewriting or dropping existing data."""
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})")}
    if column_name not in existing:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def init_database(db_path=None, init_sql_path=None):
    """初始化或非破坏性迁移 SQLite 数据库。"""
    db_path = db_path or DB_PATH
    init_sql_path = init_sql_path or INIT_SQL_PATH
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)

    if not os.path.exists(init_sql_path):
        print(f"[DB] 错误: {init_sql_path} 不存在")
        return False

    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute('PRAGMA busy_timeout=5000')
            with open(init_sql_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())

            # 仅添加缺失列；不删除、不重命名，也不重建现有表。
            migration_columns = {
                'de_test_batch': {
                    'total_versions': 'INTEGER DEFAULT 0',
                    'start_time': 'TEXT',
                    'end_time': 'TEXT',
                    'save_path': 'TEXT',
                },
                'de_test_runs': {
                    'start_time': 'TEXT',
                    'end_time': 'TEXT',
                    'total_rows': 'INTEGER DEFAULT 0',
                    'csv_header': 'TEXT',
                },
                'de_commands': {
                    'raw_row': 'TEXT',
                },
                'de_data': {
                    'seq': 'INTEGER',
                    'time': 'REAL',
                    'channel_values': 'TEXT',
                },
            }
            for table_name, columns in migration_columns.items():
                if not _table_exists(conn, table_name):
                    continue
                for column_name, definition in columns.items():
                    _ensure_column(conn, table_name, column_name, definition)
            conn.commit()
    except (OSError, sqlite3.Error) as exc:
        print(f"[DB] 初始化失败: {exc}")
        return False

    print(f"[DB] 数据库已初始化: {db_path}")
    return True


# MaxUpdateRate 文本 -> 毫秒数
RATE_MAP = {
    'Default': 100,
    'SYNC to HARMONIC': 200,
    'SYNC_TO_HARMONIC': 200,
}


def parse_rate_ms(rate_text):
    """将 MaxUpdateRate 文本转换为毫秒数。"""
    rate_text = str(rate_text or '').strip()
    if rate_text in RATE_MAP:
        result = RATE_MAP[rate_text]
        print(f"[parse_rate_ms] '{rate_text}' -> {result}ms (from RATE_MAP)")
        return result
    try:
        result = int(rate_text)
        print(f"[parse_rate_ms] '{rate_text}' -> {result}ms (parsed as int)")
        return result
    except ValueError:
        pass
    m = re.search(r'(\d+)', rate_text)
    if m:
        result = int(m.group(1))
        print(f"[parse_rate_ms] '{rate_text}' -> {result}ms (extracted from regex)")
        return result
    print(f"[parse_rate_ms] '{rate_text}' -> 100ms (default)")
    return 100


@dataclass
class PrepareResult:
    """Structured prepare outcome that remains unpackable by legacy callers."""

    success: bool
    valid_fields: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    error: str = ''

    def __iter__(self):
        """Preserve ``valid_fields, warnings = collector.prepare(...)``."""
        yield self.valid_fields
        yield self.warnings

    def __bool__(self):
        """Allow direct success checks without losing structured details."""
        return self.success


class DewetronDataCollector:
    """DEWETRON 数据采集器，SQLite 存储版本。

    特点：
    - 单个守护线程负责采集
    - 数据实时写入 SQLite，无缓冲区死锁问题
    - 支持 test_type + version 回溯
    - 程序崩溃不丢数据
    """

    # CSV 表头映射（ShortId -> 带单位的列名）
    # 注意：第二个元素仅用于参考，实际使用时会从设备动态获取电力组后缀
    CSV_HEADER_MAP = {
        'U1_tRMS': ('U1_tRMS [V]',),
        'U2_tRMS': ('U2_tRMS [V]',),
        'U3_tRMS': ('U3_tRMS [V]',),
        'U_tRMS':  ('U_tRMS [V]',),
        'I1_tRMS': ('I1_tRMS [A]',),
        'I2_tRMS': ('I2_tRMS [A]',),
        'I3_tRMS': ('I3_tRMS [A]',),
        'I_tRMS':  ('I_tRMS [A]',),
        'P1_t':    ('P1_t [W]',),
        'P2_t':    ('P2_t [W]',),
        'P3_t':    ('P3_t [W]',),
        'P_t':     ('P_t [W]',),
        'Q1_fund': ('Q1_fund [var]',),
        'Q2_fund': ('Q2_fund [var]',),
        'Q3_fund': ('Q3_fund [var]',),
        'Q_fund':  ('Q_fund [var]',),
        'S1_t':    ('S1_t [VA]',),
        'S2_t':    ('S2_t [VA]',),
        'S3_t':    ('S3_t [VA]',),
        'S_t':     ('S_t [VA]',),
        'PF1_t':   ('PF1_t []',),
        'PF2_t':   ('PF2_t []',),
        'PF3_t':   ('PF3_t []',),
        'PF_t':    ('PF_t []',),
        'F_fund':  ('F_fund [Hz]',),
    }

    def __init__(self, controller, logger, db_path=None):
        """初始化采集器。

        Args:
            controller: DewetronController 实例（已连接）
            logger: 日志对象，需有 info() 方法
            db_path: 可选数据库路径；默认使用项目 database/db.sqlite
        """
        self._ctrl = controller
        self._log = logger
        self._db_path = db_path or DB_PATH
        self._thread = None
        self._stop_event = threading.Event()

        # 采集状态
        self.is_gather = threading.Event()

        # 采集配置
        self._fields = []
        self._scpi_channels = []
        self._csv_header = []
        self._rate_ms = 100
        self._save_path = ''
        self._test_type = ''

        # SQLite
        self._conn = None
        self._db_lock = threading.Lock()  # 数据库操作锁
        self._batch_id = None    # 当前批次 ID (de_test_batch.id)
        self._batch_uid = None   # 当前批次唯一标识
        self._run_id = None      # 当前追加 ID (de_test_runs.id)
        self._last_run_id = None # 最近完成的追加 ID，供旧导出接口使用
        self._seq = 0
        self._total_rows = 0
        self._no_data_backoff_s = 0.0

        # 时间追踪
        self._gather_start_time = 0

        # 采集准备状态
        self._ready_to_gather = False

    def start(self):
        """启动守护线程。"""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()
        self._log.info("[Collector] 守护线程已启动")

    def stop(self):
        """停止守护线程，并幂等完成活动 run 后关闭数据库。"""
        self._stop_event.set()
        self.is_gather.clear()
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        if self._run_id is not None:
            self.finish_run()
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
        self._log.info("[Collector] 守护线程已停止")

    def _prepare_failure(self, error, warnings=None):
        """Clear readiness and return a consistent failed preparation result."""
        self._ready_to_gather = False
        self._fields = []
        self._scpi_channels = []
        self._csv_header = []
        return PrepareResult(False, [], list(warnings or []), error)

    def _controller_connected(self):
        """Return whether a usable, connected controller is available."""
        if self._ctrl is None:
            return False
        if hasattr(self._ctrl, 'connected'):
            return bool(self._ctrl.connected)
        return getattr(self._ctrl, 'handle', None) is not None

    def _query_controller(self, command, timeout_ms=30000):
        """Use the controller public query API with old-controller fallback."""
        query = getattr(self._ctrl, 'query_command', None) or getattr(self._ctrl, 'query', None)
        if query is None:
            query = getattr(self._ctrl, '_query', None)
        if query is None:
            return None
        try:
            return query(command, timeout_ms=timeout_ms)
        except TypeError:
            return query(command)

    def _send_controller(self, command, success_log, error_prefix, timeout_ms=None):
        """Use the controller public send API with old-controller fallback."""
        sender = getattr(self._ctrl, 'send_command', None) or getattr(self._ctrl, '_send', None)
        if sender is None:
            return False
        try:
            return bool(sender(command, success_log, error_prefix, timeout_ms=timeout_ms))
        except TypeError:
            try:
                return bool(sender(command, success_log, error_prefix))
            except TypeError:
                return bool(sender(command))

    def prepare(self, fields, rate_text, test_type, save_path):
        """校验采集配置并返回结构化、可兼容解包的结果。"""
        self._ready_to_gather = False
        warnings = []
        fields = list(fields or [])
        print(f"[Collector][prepare] fields={fields}, rate={rate_text}, "
              f"test_type={test_type}, save_path={save_path}")

        if self._ctrl is None:
            return self._prepare_failure("DEWETRON 控制器不可用")
        if not self._controller_connected():
            return self._prepare_failure("DEWETRON 未连接")
        if not fields:
            return self._prepare_failure("未选择采集字段")

        raw = self._query_controller(":CHANNELLIST:NAMES?", timeout_ms=30000)
        device_channels = {
            match.group(2)
            for match in re.finditer(r'"(\d+)","([^"]+)"', raw or '')
        }
        if not device_channels:
            return self._prepare_failure("无法查询设备通道列表")

        power_suffixes = {
            channel[channel.index('@'):]
            for channel in device_channels
            if '@' in channel
        }
        print(f"[Collector][prepare] 设备电力组后缀: {power_suffixes}")

        def suffix_priority(suffix):
            return 0 if '_AVG' not in suffix else len(suffix)

        sorted_suffixes = sorted(power_suffixes, key=suffix_priority)
        valid = []
        for selected_field in fields:
            if selected_field in device_channels:
                valid.append(selected_field)
                continue

            matched = next(
                (f"{selected_field}{suffix}" for suffix in sorted_suffixes
                 if f"{selected_field}{suffix}" in device_channels),
                None,
            )
            if matched is None:
                matched = next(
                    (channel for channel in sorted(device_channels)
                     if channel.startswith(selected_field)),
                    None,
                )
            if matched:
                valid.append(matched)
            else:
                warnings.append(f"字段 '{selected_field}' 在设备上不存在，已跳过")

        if not valid:
            return self._prepare_failure("没有可用的设备采集字段", warnings)

        self._fields = valid
        self._scpi_channels = list(valid)
        self._csv_header = ['Time [s]']
        for channel in valid:
            short_id = channel.split('@')[0]
            suffix = channel[channel.index('@'):] if '@' in channel else ''
            mapped_header = self.CSV_HEADER_MAP.get(short_id)
            self._csv_header.append(
                mapped_header[0] + suffix if mapped_header else channel
            )

        self._rate_ms = parse_rate_ms(rate_text)
        self._save_path = save_path or ''
        self._test_type = test_type or 'dewetron'
        try:
            self._connect_database()
        except sqlite3.Error as exc:
            return self._prepare_failure(f"数据库连接失败: {exc}", warnings)

        print(f"[Collector][prepare] 完成: {len(valid)} 个有效字段, "
              f"间隔 {self._rate_ms}ms, test_type={self._test_type}")
        return PrepareResult(True, list(valid), warnings)

    @staticmethod
    def _normalize_state(state):
        """Normalize SCPI-prefixed state responses for exact validation."""
        if state is None:
            return ''
        value = str(state).strip().strip('"')
        match = re.search(r'(Started|Stopped)\s*$', value, re.IGNORECASE)
        return match.group(1).casefold() if match else value.casefold()

    def _setup_rate(self):
        """Set and verify the device numeric update rate."""
        if not self._send_controller(
            f":RATE {self._rate_ms}ms",
            f"设置采集间隔 {self._rate_ms}ms",
            "RATE",
        ):
            return False
        rate_val = self._query_controller(":RATE?")
        if not rate_val:
            return False
        actual_ms = parse_rate_ms(str(rate_val).replace(':RATE', '').strip())
        print(f"[Collector][start_gathering] RATE 验证: 设置={self._rate_ms}ms, 实际={rate_val}")
        return actual_ms == self._rate_ms

    def start_gathering(self):
        """配置采集并创建当前 run；成功返回 True。"""
        print("[Collector][start_gathering] === 开始采集准备 ===")
        if not self._controller_connected() or not self._conn or not self._fields:
            self._ready_to_gather = False
            return False
        run_exists = self._run_id is not None
        if run_exists and (self._ready_to_gather or self.is_gather.is_set()):
            return True

        acq_state = self._query_controller(":ACQUISITION:STATE?")
        if not acq_state:
            return False
        print(f"[Collector][start_gathering] 当前采集状态: {acq_state}")
        if self._normalize_state(acq_state) == 'started':
            stop_acquisition = getattr(self._ctrl, 'stop_acquisition', None)
            stopped = bool(stop_acquisition()) if stop_acquisition else self._send_controller(
                ":ACQUISITION:STOP", "停止采集", "ACQUISITION STOP"
            )
            if not stopped:
                return False
            time.sleep(0.5)

        if not self._setup_numeric() or not self._setup_rate():
            self._ready_to_gather = False
            return False

        self._total_rows = 0
        self._seq = 0
        self._no_data_backoff_s = 0.0
        self._gather_start_time = time.time()
        if not run_exists and not self.begin_run():
            return False

        self._ready_to_gather = True
        print("[Collector][start_gathering] 准备完成，等待 :ACQUISITION:START")
        return True

    def on_acquisition_started(self):
        """验证设备确实 Started 后启动采集查询，成功返回 True。"""
        if not self._ready_to_gather or self._run_id is None:
            return False

        time.sleep(1.0)
        acq_state = self._query_controller(":ACQUISITION:STATE?", timeout_ms=5000)
        print(f"[Collector][on_acquisition_started] 采集状态: {acq_state}")
        if self._normalize_state(acq_state) != 'started':
            self.is_gather.clear()
            return False

        items = self._query_controller(":NUM:NORM:ITEMs?", timeout_ms=5000)
        print(f"[Collector][on_acquisition_started] NUMERIC 通道: {items[:100] if items else '空'}")

        self.is_gather.set()
        self._ready_to_gather = False
        print("[Collector][on_acquisition_started] 采集线程开始工作")
        return True

    def stop_gathering(self):
        """幂等停止当前采集并完成当前 run。"""
        was_active = self.is_gather.is_set() or self._ready_to_gather or self._run_id is not None
        self.is_gather.clear()
        self._ready_to_gather = False
        if self._run_id is not None:
            self.finish_run()
        if was_active:
            self._log.info(f"[Collector] 停止采集，共 {self._total_rows} 行数据")
        return was_active

    def finish_batch(self):
        """结束当前批次，更新批次结束时间；重复调用安全。"""
        if not self._conn or not self._batch_id:
            return False
        if self._run_id is not None:
            self.finish_run()
        end_time = time.strftime('%Y-%m-%d %H:%M:%S')
        batch_uid = self._batch_uid
        with self._db_lock:
            self._conn.execute(
                "UPDATE de_test_batch SET end_time = ? WHERE id = ?",
                (end_time, self._batch_id),
            )
            self._conn.commit()
        print(f"[Collector][finish_batch] 批次结束: {batch_uid}")
        self._batch_id = None
        self._batch_uid = None
        return True

    def end_batch(self):
        """兼容旧接口，结束当前批次。"""
        return self.finish_batch()

    def export_run_to_csv(self, run_id, csv_path):
        """将指定 run 的数据导出到 CSV。"""
        if not self.has_database() or not run_id or not csv_path:
            return None
        try:
            header = self.get_run_header(run_id)
            if not header:
                return None
            rows = self.get_run_rows(run_id)
            csv_dir = os.path.dirname(csv_path)
            if csv_dir:
                os.makedirs(csv_dir, exist_ok=True)
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as output:
                writer = csv.writer(output)
                writer.writerow(header)
                for time_val, values in rows:
                    writer.writerow(
                        [f"{time_val:.4f}"] + [f"{value:.7f}" for value in values]
                    )
            print(f"[Collector][export_run_to_csv] 导出完成: {csv_path} ({len(rows)} 行)")
            return csv_path
        except (OSError, ValueError, TypeError, sqlite3.Error) as exc:
            print(f"[Collector][export_run_to_csv] 导出异常: {exc}")
            return None

    def export_to_csv(self, csv_path=None):
        """兼容旧接口，导出当前或最近完成的 run 数据。"""
        run_id = self._run_id if self._run_id is not None else self._last_run_id
        return self.export_run_to_csv(run_id, csv_path or self._save_path)

    def get_save_path(self):
        """获取当前保存路径。"""
        return self._save_path

    def get_total_rows(self):
        """获取已采集的总行数。"""
        return self._total_rows

    def get_run_id(self):
        """获取当前 de_test_runs.id。"""
        return self._run_id

    def has_database(self):
        """Return whether the collector currently has an open database connection."""
        return self._conn is not None

    def current_batch(self):
        """Return public state for the current batch, or None."""
        if self._batch_id is None:
            return None
        return {'id': self._batch_id, 'batch_uid': self._batch_uid,
                'test_type': self._test_type}

    def current_run(self):
        """Return public state for the current run, or None."""
        if self._run_id is None:
            return None
        return {'id': self._run_id, 'batch_id': self._batch_id,
                'total_rows': self._total_rows}

    def get_state(self):
        """Return a public snapshot of database, batch, run, and gathering state."""
        return {
            'has_database': self.has_database(),
            'batch': self.current_batch(),
            'run': self.current_run(),
            'state': self.get_run_state(),
        }

    def get_run_header(self, run_id):
        """Return the decoded CSV header for a run."""
        if not self.has_database() or not run_id:
            return []
        with self._db_lock:
            row = self._conn.execute(
                "SELECT csv_header FROM de_test_runs WHERE id = ?", (run_id,)
            ).fetchone()
        if not row or not row[0]:
            return []
        try:
            return json.loads(row[0])
        except (TypeError, ValueError):
            return []

    def get_run_rows(self, run_id):
        """Return ``[(time, values), ...]`` for a run using decoded values."""
        if not self.has_database() or not run_id:
            return []
        with self._db_lock:
            rows = self._conn.execute(
                "SELECT time, channel_values FROM de_data WHERE run_id = ? ORDER BY seq",
                (run_id,),
            ).fetchall()
        decoded = []
        for time_val, values_json in rows:
            try:
                decoded.append((time_val, json.loads(values_json)))
            except (TypeError, ValueError):
                continue
        return decoded

    def get_run_state(self):
        """Return acquisition lifecycle state without exposing internals."""
        if self.is_gather.is_set():
            return 'gathering'
        if self._ready_to_gather:
            return 'ready'
        if self._run_id is not None:
            return 'running'
        return 'idle'

    def list_de_test_runs(self, test_type=None):
        """列出所有测试记录（兼容旧接口）。"""
        if not self._conn:
            return []
        if test_type:
            rows = self._conn.execute(
                "SELECT tr.id, tb.test_type, tr.version, tr.start_time, tr.end_time, tr.total_rows "
                "FROM de_test_runs tr JOIN de_test_batch tb ON tr.batch_id = tb.id "
                "WHERE tb.test_type = ? ORDER BY tr.version",
                (test_type,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT tr.id, tb.test_type, tr.version, tr.start_time, tr.end_time, tr.total_rows "
                "FROM de_test_runs tr JOIN de_test_batch tb ON tr.batch_id = tb.id "
                "ORDER BY tb.test_type, tr.version"
            ).fetchall()
        return rows

    def list_batches(self, test_type=None):
        """列出所有测试批次。

        Returns:
            list: [(id, batch_uid, test_type, total_versions, start_time, end_time), ...]
        """
        if not self._conn:
            return []
        if test_type:
            rows = self._conn.execute(
                "SELECT id, batch_uid, test_type, total_versions, start_time, end_time "
                "FROM de_test_batch WHERE test_type = ? ORDER BY id DESC",
                (test_type,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id, batch_uid, test_type, total_versions, start_time, end_time "
                "FROM de_test_batch ORDER BY id DESC"
            ).fetchall()
        return rows

    def get_batch_runs(self, batch_id):
        """获取某个批次的所有追加记录。

        Returns:
            list: [(id, version, start_time, end_time, total_rows), ...]
        """
        if not self._conn:
            return []
        rows = self._conn.execute(
            "SELECT id, version, start_time, end_time, total_rows "
            "FROM de_test_runs WHERE batch_id = ? ORDER BY version",
            (batch_id,)
        ).fetchall()
        return rows

    def get_batch_uid(self):
        """获取当前批次唯一标识。"""
        return self._batch_uid

    # --- 命令管理方法 ---

    def save_commands(self, commands):
        """保存命令列表到数据库。

        Args:
            commands: 命令列表，每个元素是 list[str]，格式与 strArrayTest 一致
                      [device, operation, command, p1, p2, p3, p4, p5, p6, p7, wait_time]
        """
        if not self._conn or not self._run_id:
            print("[Collector][save_commands] 无数据库连接或 run_id")
            return

        with self._db_lock:
            self._conn.execute("DELETE FROM de_commands WHERE run_id = ?", (self._run_id,))
            self._conn.commit()

        for i, cmd in enumerate(commands):
            if len(cmd) < 3:
                continue
            raw_row = list(cmd[:10])
            if len(raw_row) < 10:
                raw_row.extend([''] * (10 - len(raw_row)))
            raw_row_json = json.dumps(raw_row, ensure_ascii=False, default=str)
            # 解析命令数组
            device = cmd[0] if len(cmd) > 0 else ''
            operation = cmd[1] if len(cmd) > 1 else ''
            command = cmd[2] if len(cmd) > 2 else ''
            params = [cmd[j] if len(cmd) > j else '' for j in range(3, 10)]
            # wait_time 在索引8或9
            wait_time = 0
            for idx in (8, 9):
                if len(cmd) > idx and cmd[idx] != '':
                    try:
                        wait_time = int(cmd[idx])
                    except (ValueError, TypeError):
                        pass

            with self._db_lock:
                self._conn.execute(
                    "INSERT INTO de_commands (run_id, seq, device, operation, command, "
                    "param1, param2, param3, param4, param5, param6, param7, raw_row, wait_time) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (self._run_id, i + 1, device, operation, command,
                     params[0], params[1], params[2], params[3], params[4], params[5], params[6],
                     raw_row_json, wait_time)
                )

            self._conn.commit()
        print(f"[Collector][save_commands] 保存 {len(commands)} 条命令到 run_id={self._run_id}")

    def load_commands(self, run_id=None):
        """从数据库加载命令列表。

        Args:
            run_id: 指定 run_id，如果为 None 则使用当前 run_id

        Returns:
            list: 命令列表，格式与 strArrayTest 一致
        """
        if not self._conn:
            return []

        target_run_id = run_id or self._run_id
        if not target_run_id:
            return []

        rows = self._conn.execute(
            "SELECT device, operation, command, param1, param2, param3, "
            "param4, param5, param6, param7, raw_row, wait_time "
            "FROM de_commands WHERE run_id = ? ORDER BY seq",
            (target_run_id,)
        ).fetchall()

        commands = []
        for row in rows:
            raw_row = row[10]
            if raw_row:
                try:
                    cmd = json.loads(raw_row)
                    if isinstance(cmd, list) and len(cmd) == 10:
                        commands.append(cmd)
                        continue
                except (TypeError, ValueError):
                    pass

            device, operation, command = row[0], row[1], row[2]
            params = list(row[3:10])
            wait_time = row[11]

            # 兼容旧记录：缺少 raw_row 时按历史字段重建。
            cmd = ['' for _ in range(10)]
            cmd[0] = device
            cmd[1] = operation
            cmd[2] = command
            for j, p in enumerate(params):
                if j + 3 < len(cmd):
                    cmd[j + 3] = p or ''
            if wait_time:
                cmd[8] = wait_time
            commands.append(cmd)

        print(f"[Collector][load_commands] 加载 {len(commands)} 条命令 from run_id={target_run_id}")
        return commands

    def mark_command_executed(self, seq, result="OK"):
        """标记命令为已执行。

        Args:
            seq: 命令序号
            result: 执行结果
        """
        if not self._conn or not self._run_id:
            return

        execute_time = time.strftime('%Y-%m-%d %H:%M:%S')
        with self._db_lock:
            self._conn.execute(
                "UPDATE de_commands SET executed = 1, execute_time = ?, execute_result = ? "
                "WHERE run_id = ? AND seq = ?",
                (execute_time, result, self._run_id, seq)
            )
            self._conn.commit()

    def get_commands_status(self, run_id=None):
        """获取命令执行状态统计。

        Returns:
            dict: {'total': N, 'executed': N, 'pending': N}
        """
        if not self._conn:
            return {'total': 0, 'executed': 0, 'pending': 0}

        target_run_id = run_id or self._run_id
        if not target_run_id:
            return {'total': 0, 'executed': 0, 'pending': 0}

        total = self._conn.execute(
            "SELECT COUNT(*) FROM de_commands WHERE run_id = ?",
            (target_run_id,)
        ).fetchone()[0]

        executed = self._conn.execute(
            "SELECT COUNT(*) FROM de_commands WHERE run_id = ? AND executed = 1",
            (target_run_id,)
        ).fetchone()[0]

        return {'total': total, 'executed': executed, 'pending': total - executed}

    def get_commands_list(self, run_id=None):
        """获取命令列表（用于显示）。

        Returns:
            list: [(seq, device, operation, command, executed, execute_time), ...]
        """
        if not self._conn:
            return []

        target_run_id = run_id or self._run_id
        if not target_run_id:
            return []

        rows = self._conn.execute(
            "SELECT seq, device, operation, command, executed, execute_time "
            "FROM de_commands WHERE run_id = ? ORDER BY seq",
            (target_run_id,)
        ).fetchall()

        return rows

    # --- 内部方法 ---

    def _connect_database(self):
        """连接 SQLite 数据库并配置并发等待策略。"""
        if self._conn is not None:
            return True
        if not init_database(self._db_path, INIT_SQL_PATH):
            raise sqlite3.OperationalError("database initialization failed")
        print(f"[Collector][_connect_database] 连接数据库: {self._db_path}")
        self._conn = sqlite3.connect(
            self._db_path, timeout=5.0, check_same_thread=False
        )
        self._conn.execute('PRAGMA busy_timeout=5000')
        self._conn.execute('PRAGMA journal_mode=WAL')
        return True

    def begin_batch(self, test_type=None, save_path=None):
        """开始新批次；已有当前批次时返回其 ID，避免重复插入。"""
        if test_type is not None:
            self._test_type = test_type
        if save_path is not None:
            self._save_path = save_path
        if self._batch_id is not None:
            return self._batch_id
        if not self._test_type:
            return None
        if not self._conn:
            try:
                self._connect_database()
            except sqlite3.Error:
                return None

        timestamp = time.strftime('%Y%m%d_%H%M%S')
        base_uid = f"{self._test_type}_{timestamp}"
        start_time = time.strftime('%Y-%m-%d %H:%M:%S')
        with self._db_lock:
            batch_uid = base_uid
            suffix = 1
            while self._conn.execute(
                "SELECT 1 FROM de_test_batch WHERE batch_uid = ?", (batch_uid,)
            ).fetchone():
                suffix += 1
                batch_uid = f"{base_uid}_{suffix}"
            cursor = self._conn.execute(
                "INSERT INTO de_test_batch (batch_uid, test_type, start_time, save_path) "
                "VALUES (?, ?, ?, ?)",
                (batch_uid, self._test_type, start_time, self._save_path),
            )
            self._batch_id = cursor.lastrowid
            self._batch_uid = batch_uid
            self._conn.commit()
        print(f"[Collector][begin_batch] 新批次: {batch_uid} (batch_id={self._batch_id})")
        return self._batch_id

    def start_batch(self, test_type=None, save_path=None):
        """兼容旧接口，开始新批次。"""
        return self.begin_batch(test_type, save_path)

    def _get_next_version(self):
        """获取当前批次内的下一个版本号。"""
        if not self._batch_id:
            return 1
        row = self._conn.execute(
            "SELECT MAX(version) FROM de_test_runs WHERE batch_id = ?",
            (self._batch_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def begin_run(self, batch_id=None, csv_header=None):
        """在批次内创建 run；已有当前 run 时幂等返回其 ID。"""
        if self._run_id is not None:
            return self._run_id
        if batch_id is not None:
            if not self._conn:
                try:
                    self._connect_database()
                except sqlite3.Error:
                    return None
            row = self._conn.execute(
                "SELECT batch_uid, test_type FROM de_test_batch WHERE id = ?",
                (batch_id,),
            ).fetchone()
            if not row:
                return None
            self._batch_id = batch_id
            self._batch_uid, self._test_type = row
        if csv_header is not None:
            self._csv_header = list(csv_header)
        if not self._conn or not self._csv_header:
            return None
        if not self._batch_id and not self.begin_batch():
            return None

        version = self._get_next_version()
        start_time = time.strftime('%Y-%m-%d %H:%M:%S')
        csv_header_json = json.dumps(self._csv_header)
        with self._db_lock:
            cursor = self._conn.execute(
                "INSERT INTO de_test_runs (batch_id, version, start_time, csv_header) "
                "VALUES (?, ?, ?, ?)",
                (self._batch_id, version, start_time, csv_header_json),
            )
            self._run_id = cursor.lastrowid
            self._conn.execute(
                "UPDATE de_test_batch SET total_versions = ? WHERE id = ?",
                (version, self._batch_id),
            )
            self._conn.commit()
        print(f"[Collector][begin_run] {self._batch_uid} v{version} (run_id={self._run_id})")
        return self._run_id

    def _insert_test_run(self):
        """兼容旧内部接口，创建当前 run。"""
        return self.begin_run()

    def finish_run(self, run_id=None):
        """完成当前 run 并清除其活动状态；重复调用安全。"""
        target_run_id = self._run_id if run_id is None else run_id
        if not self._conn or target_run_id is None:
            return False
        if run_id is not None and self._run_id not in (None, run_id):
            return False
        run_id = target_run_id
        end_time = time.strftime('%Y-%m-%d %H:%M:%S')
        with self._db_lock:
            self._conn.execute(
                "UPDATE de_test_runs SET end_time = ?, total_rows = ? WHERE id = ?",
                (end_time, self._total_rows, run_id),
            )
            self._conn.commit()
        self._last_run_id = run_id
        if self._run_id == run_id:
            self._run_id = None
            self.is_gather.clear()
            self._ready_to_gather = False
        return True

    def _update_test_run_end(self):
        """兼容旧内部接口，完成当前 run。"""
        return self.finish_run()

    def _setup_numeric(self):
        """配置并验证设备 NUMERIC 输出通道。"""
        if not self._scpi_channels:
            return False
        if not self._send_controller(
            ":NUM:NORM:CLEar ALL", "清除旧配置", "NUM CLEAR"
        ):
            return False

        all_channels = ['ABS-TIME'] + self._scpi_channels
        items_str = ','.join(f'"{channel}"' for channel in all_channels)
        if not self._send_controller(
            f":NUM:NORM:ITEMs {items_str}", "设置 NUMERIC 输出通道", "NUM ITEMS"
        ):
            return False
        if not self._send_controller(
            f":NUM:NORM:NUMber {len(all_channels)}", "设置传输数量", "NUM NUMBER"
        ):
            return False

        query_items = self._query_controller(":NUM:NORM:ITEMs?")
        print(f"[Collector] NUMERIC 配置确认: {query_items}")
        if not query_items:
            return False
        return all(channel in query_items for channel in all_channels)

    def _collect_loop(self):
        """守护线程主循环。"""
        print("[Collector][_collect_loop] 守护线程已启动")
        loop_count = 0
        first_gather = True  # 标记首次进入采集模式

        while not self._stop_event.is_set():
            if self.is_gather.is_set():
                # 首次进入采集模式时等待设备稳定
                if first_gather:
                    print("[Collector][_collect_loop] 首次采集，等待 1s 设备稳定...")
                    time.sleep(1.0)
                    first_gather = False

                # 每次循环重新计算 interval，确保使用最新的 _rate_ms
                interval_s = self._rate_ms / 1000.0
                self._collect_one_point(interval_s)
                loop_count += 1
                if loop_count % 50 == 0:
                    print(f"[Collector][_collect_loop] 已采集 {self._total_rows} 行")
            else:
                first_gather = True  # 重置标记
                time.sleep(0.1)

    def _next_no_data_delay(self, interval_s):
        """Advance and return bounded retry backoff for empty/failed queries."""
        minimum = max(float(interval_s), 0.01)
        maximum = max(minimum, min(max(float(interval_s) * 8, 0.5), 5.0))
        if self._no_data_backoff_s <= 0:
            self._no_data_backoff_s = minimum
        else:
            self._no_data_backoff_s = min(self._no_data_backoff_s * 2, maximum)
        return self._no_data_backoff_s

    def _collect_one_point(self, interval_s):
        """采集一个数据点；所有路径均节流，失败使用有界退避。"""
        t_start = time.time()
        success = False
        try:
            raw_val = self._query_controller(":NUM:NORM:VALue?", timeout_ms=5000)
            if raw_val:
                if self._total_rows == 0:
                    print(f"[Collector][_collect_one_point] 首次响应: {repr(raw_val[:500])}")
                    if ',' not in raw_val:
                        print("[Collector][_collect_one_point] 警告：响应中没有逗号，可能只有时间戳")

                row = self._parse_value(raw_val)
                if row and self._conn and self._run_id is not None:
                    elapsed = time.time() - self._gather_start_time
                    values_json = json.dumps(row)
                    with self._db_lock:
                        self._conn.execute(
                            "INSERT INTO de_data (run_id, seq, time, channel_values) "
                            "VALUES (?, ?, ?, ?)",
                            (self._run_id, self._seq, round(elapsed, 4), values_json),
                        )
                        self._conn.commit()
                    self._seq += 1
                    self._total_rows += 1
                    self._no_data_backoff_s = 0.0
                    success = True
        except Exception as exc:
            print(f"[Collector][_collect_one_point] 异常: {exc}")

        operation_elapsed = time.time() - t_start
        if success:
            sleep_time = max(float(interval_s) - operation_elapsed, 0.001)
        else:
            sleep_time = self._next_no_data_delay(interval_s)
        time.sleep(sleep_time)
        return success

    def _parse_value(self, raw_val):
        """解析 :NUM:NORM:VAL? 返回值，返回数值列表。"""
        if not raw_val:
            return None

        clean = raw_val
        sp = clean.find(' ')
        if sp >= 0:
            clean = clean[sp+1:].strip()

        if not clean:
            return None

        values = [v.strip() for v in clean.split(',')]

        # 第一个值是 ABS-TIME（字符串），跳过
        nums = []
        for v in values[1:]:
            v_clean = v.strip('"').strip("'")
            try:
                nums.append(float(v_clean))
            except ValueError:
                try:
                    nums.append(float(int(v_clean)))
                except (ValueError, TypeError):
                    nums.append(0.0)

        return nums if nums else None
