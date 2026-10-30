"""DEWETRON 数据采集模块（SQLite 版本）。

提供 DewetronDataCollector 类，用于实时采集 DEWETRON 测量数据并存储到 SQLite。
支持闪变、谐波等多测试项目复用，支持版本回溯。

数据库路径: database/db.sqlite（固定）
初始化脚本: database/init.sql；安装包未带该文件时使用本模块内置建表语句

用法:
    from devices.dewetron_data_collector import DewetronDataCollector, init_database

    # 项目启动时初始化数据库
    init_database()

    collector = DewetronDataCollector(dewetron_controller, logger)
    collector.start()  # 启动守护线程

    # 测试开始时
    collector.prepare(fields=['U1_tRMS@AC', ...], rate_text='Default',
                      test_type='flicker', save_path='D:/data/test.csv',
                      decimal_places=4)
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
import math
import os
import sqlite3
import time
import threading
import re
from dataclasses import dataclass, field
from typing import Optional


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


# 与 database/init.sql 保持一致。发布包排除整个 database 目录，
# 增量更新只同步 stage 里已有的文件，不会补上 init.sql。
_EMBEDDED_INIT_SQL = """
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS de_test_batch (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_uid TEXT UNIQUE NOT NULL,
    test_type TEXT NOT NULL,
    total_versions INTEGER DEFAULT 0,
    start_time TEXT,
    end_time TEXT,
    save_path TEXT
);

CREATE TABLE IF NOT EXISTS de_test_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    start_time TEXT,
    end_time TEXT,
    total_rows INTEGER DEFAULT 0,
    csv_header TEXT,
    UNIQUE(batch_id, version)
);

CREATE TABLE IF NOT EXISTS de_commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    seq INTEGER NOT NULL,
    device TEXT NOT NULL,
    operation TEXT NOT NULL,
    command TEXT NOT NULL,
    param1 TEXT,
    param2 TEXT,
    param3 TEXT,
    param4 TEXT,
    param5 TEXT,
    param6 TEXT,
    param7 TEXT,
    raw_row TEXT,
    wait_time INTEGER DEFAULT 0,
    executed INTEGER DEFAULT 0,
    execute_time TEXT,
    execute_result TEXT,
    FOREIGN KEY (run_id) REFERENCES de_test_runs(id)
);

CREATE TABLE IF NOT EXISTS de_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    seq INTEGER,
    time REAL,
    channel_values TEXT,
    FOREIGN KEY (run_id) REFERENCES de_test_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_de_test_runs_batch_id ON de_test_runs(batch_id);
CREATE INDEX IF NOT EXISTS idx_de_data_run_id ON de_data(run_id);
CREATE INDEX IF NOT EXISTS idx_de_test_batch_uid ON de_test_batch(batch_uid);
CREATE INDEX IF NOT EXISTS idx_de_commands_run_id ON de_commands(run_id);
CREATE INDEX IF NOT EXISTS idx_de_commands_executed ON de_commands(executed);
"""


def _load_init_script(init_sql_path):
    """读取 init.sql；文件不在安装目录时使用内置建表语句。"""
    if init_sql_path and os.path.isfile(init_sql_path):
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            return f.read()
    print(f"[DB] {init_sql_path} 不存在，使用内置建表语句")
    return _EMBEDDED_INIT_SQL


def init_database(db_path=None, init_sql_path=None):
    """初始化或非破坏性迁移 SQLite 数据库。

    缺少 database/init.sql 时仍建库。安装包排除 database 目录，
    增量更新不会把 init.sql 同步到已安装的工控机。
    """
    db_path = db_path or DB_PATH
    init_sql_path = init_sql_path or INIT_SQL_PATH
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)

    try:
        script = _load_init_script(init_sql_path)
        with sqlite3.connect(db_path) as conn:
            conn.execute('PRAGMA busy_timeout=5000')
            conn.executescript(script)

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
    """将 MaxUpdateRate 文本转换为毫秒数。

    UI 侧多为 ``Default`` / ``100`` / ``100ms``（毫秒）。
    设备 ``:RATE?`` 常回 ``1.0E-1`` / ``0.1``（秒）。勿对科学计数法只取首段数字，
    否则 ``1.0E-1`` 会被误判成 1ms。
    """
    rate_text = str(rate_text or '').strip()
    rate_text = re.sub(r'^:RATE\s*', '', rate_text, flags=re.IGNORECASE).strip().strip('"')
    if rate_text in RATE_MAP:
        result = RATE_MAP[rate_text]
        print(f"[parse_rate_ms] '{rate_text}' -> {result}ms (from RATE_MAP)")
        return result

    ms_match = re.match(
        r'^([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*ms$',
        rate_text,
        re.IGNORECASE,
    )
    if ms_match:
        result = int(round(float(ms_match.group(1))))
        print(f"[parse_rate_ms] '{rate_text}' -> {result}ms (explicit ms)")
        return result

    sec_match = re.match(
        r'^([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*s(?:ec(?:onds?)?)?$',
        rate_text,
        re.IGNORECASE,
    )
    if sec_match:
        result = int(round(float(sec_match.group(1)) * 1000.0))
        print(f"[parse_rate_ms] '{rate_text}' -> {result}ms (explicit seconds)")
        return result

    try:
        value = float(rate_text)
    except ValueError:
        value = None
    if value is not None:
        # Device replies are seconds (0.1, 1.0E-1). Plain UI integers like 100
        # stay in milliseconds. Threshold: values below 10 are treated as seconds.
        if abs(value) < 10:
            result = int(round(value * 1000.0))
            print(f"[parse_rate_ms] '{rate_text}' -> {result}ms (seconds→ms)")
        else:
            result = int(round(value))
            print(f"[parse_rate_ms] '{rate_text}' -> {result}ms (parsed as ms)")
        return result

    m = re.search(r'(\d+)', rate_text)
    if m:
        result = int(m.group(1))
        print(f"[parse_rate_ms] '{rate_text}' -> {result}ms (extracted from regex)")
        return result
    print(f"[parse_rate_ms] '{rate_text}' -> 100ms (default)")
    return 100


def scpi_poll_interval_s(rate_ms):
    """SCPI 抽点周期：与界面设定的设备刷新率一致（200ms → 约每 200ms 一行 CSV）。"""
    try:
        rate = int(rate_ms or 0)
    except (TypeError, ValueError):
        rate = 0
    if rate <= 0:
        rate = 100
    return rate / 1000.0


def rates_match_ms(expected_ms, actual_ms, tolerance_ms=1):
    """Compare configured vs device-reported rates with a small tolerance."""
    try:
        return abs(int(actual_ms) - int(expected_ms)) <= int(tolerance_ms)
    except (TypeError, ValueError):
        return False


def dumps_channel_values(values):
    """Serialize channel values for SQLite. NaN/Inf → null（标准 JSON，可读回）。"""
    cleaned = []
    for value in list(values or []):
        try:
            number = float(value)
        except (TypeError, ValueError):
            cleaned.append(None)
            continue
        if math.isnan(number) or math.isinf(number):
            cleaned.append(None)
        else:
            cleaned.append(number)
    return json.dumps(cleaned, ensure_ascii=False)


def loads_channel_values(raw):
    """Deserialize channel_values；兼容历史 json.dumps(nan) 写出的非标准 NaN。"""
    text = str(raw or "").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        fixed = re.sub(r"\b-?Infinity\b", "null", text)
        fixed = re.sub(r"\bNaN\b", "null", fixed)
        try:
            data = json.loads(fixed)
        except json.JSONDecodeError:
            return []
    if not isinstance(data, list):
        return []
    out = []
    for value in data:
        if value is None:
            out.append(float("nan"))
            continue
        try:
            out.append(float(value))
        except (TypeError, ValueError):
            out.append(float("nan"))
    return out


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
        # CSV 通道值小数位；与面板 spinBox_DEW_DecimalPlaces（0–6）一致，默认 4
        self._csv_decimal_places = 4

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
        self._sample_deadline = 0.0

        # 采集准备状态
        self._ready_to_gather = False

        # 跳脱值自动抓取：默认关闭（10min 电压保护等试验也会断流，易误报）
        self._trip_screenshot_enabled = False
        self._trip_monitor = None
        self._trip_shot_count = 0
        self._trip_event_count = 0
        self._trip_last_warn = ""
        self._trip_pre_s = 2.0
        self._trip_post_s = 1.0
        self._trip_render_period_png = False
        self._trip_capture_oxygen = False
        self._trip_startup_ignore_s = 8.0
        self._trip_arm_hold_s = 2.0
        self._trip_sample_buf = []
        self._trip_buf_max = 400
        self._trip_pending = None
        self._trip_events = []
        self._oxygen_store_enabled = False
        self._oxygen_store_path = ""
        self._oxygen_store_active = False
        self._ui_notify = None


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
        try:
            self._stop_oxygen_store()
        except Exception:
            pass
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

    def set_ui_notify(self, callback):
        """设置操作日志回调（线程内调用，回调需自行切回 UI 线程）。"""
        self._ui_notify = callback if callable(callback) else None

    def _emit_ui(self, message: str):
        line = str(message or "").strip()
        if not line:
            return
        print(line)
        try:
            self._log.info(line)
        except Exception:
            pass
        cb = self._ui_notify
        if cb is None:
            return
        try:
            cb(line)
        except Exception as exc:
            print(f"[Collector] ui_notify 失败: {exc}")

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

    @staticmethod
    def _clamp_csv_decimal_places(value, default=4):
        """Clamp CSV decimal places to the panel range 0–6."""
        try:
            places = int(value)
        except (TypeError, ValueError):
            places = int(default)
        return max(0, min(6, places))

    def set_csv_decimal_places(self, decimal_places):
        """Set CSV channel-value decimal places used by export_run_to_csv."""
        self._csv_decimal_places = self._clamp_csv_decimal_places(decimal_places)
        return self._csv_decimal_places

    def prepare(self, fields, rate_text, test_type, save_path, decimal_places=None):
        """校验采集配置并返回结构化、可兼容解包的结果。"""
        self._ready_to_gather = False
        warnings = []
        fields = list(fields or [])
        if decimal_places is not None:
            self.set_csv_decimal_places(decimal_places)
        print(f"[Collector][prepare] fields={fields}, rate={rate_text}, "
              f"test_type={test_type}, save_path={save_path}, "
              f"decimal_places={self._csv_decimal_places}")

        if self._ctrl is None:
            return self._prepare_failure("DEWETRON 控制器不可用")
        if not self._controller_connected():
            return self._prepare_failure("DEWETRON 未连接")
        if not fields:
            return self._prepare_failure("未选择采集字段")

        raw = ""
        device_channels = set()
        waiter = getattr(self._ctrl, "wait_scpi_ready", None)
        attempts = 8 if callable(waiter) else 2
        for attempt in range(attempts):
            raw = self._query_controller(":CHANNELLIST:NAMES?", timeout_ms=8000)
            device_channels = {
                match.group(2)
                for match in re.finditer(r'"(\d+)","([^"]+)"', raw or '')
            }
            if device_channels:
                break
            if attempt + 1 >= attempts:
                break
            time.sleep(1.0)
            print(f"[Collector][prepare] CHANNELLIST 空，重试 {attempt + 2}/{attempts}")
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

        # 跳脱值需要实时电流；未勾选时尽量从设备补 I1/I2/I3
        if self._trip_screenshot_enabled:
            injected = self._inject_current_channels_for_trip(valid, device_channels, warnings)
            if injected:
                valid = injected
            valid = self._inject_uf_channels_for_trip_value(valid, device_channels)

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
        self._setup_trip_monitor_from_fields()
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
        print(
            f"[Collector][start_gathering] RATE 验证: "
            f"设置={self._rate_ms}ms, 实际={rate_val} (解析={actual_ms}ms)"
        )
        if rates_match_ms(self._rate_ms, actual_ms, tolerance_ms=5):
            return True
        # 设备可能把 200ms 量化到邻近档；按实读取样，避免硬失败或软件节拍与设备不一致
        if actual_ms > 0:
            print(
                f"[Collector][start_gathering] RATE 不完全匹配，"
                f"改用设备回报 {actual_ms}ms 作为采样节拍（目标 {self._rate_ms}ms）"
            )
            self._rate_ms = int(actual_ms)
            self._emit_ui(
                f"[DEWETRON] 刷新率设备回报为 {actual_ms}ms（设定 {rate_val}），已按实际值采样"
            )
            return True
        return False
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
        # Time[s] 以首点采样为零点；此处先清零，真正开采时再对齐
        self._gather_start_time = 0.0
        self._sample_deadline = 0.0
        if not run_exists and not self.begin_run():
            return False

        self._ready_to_gather = True
        print("[Collector][start_gathering] 准备完成，等待 :ACQUISITION:START")
        return True

    def on_acquisition_started(self):
        """验证设备确实 Started 后启动采集查询，成功返回 True。"""
        if not self._ready_to_gather or self._run_id is None:
            return False

        # 短稳定即可；过长会导致 Time[s] 与真实录波起点错位
        time.sleep(0.2)
        acq_state = self._query_controller(":ACQUISITION:STATE?", timeout_ms=5000)
        print(f"[Collector][on_acquisition_started] 采集状态: {acq_state}")
        if self._normalize_state(acq_state) != 'started':
            self.is_gather.clear()
            return False

        items = self._query_controller(":NUM:NORM:ITEMs?", timeout_ms=5000)
        print(f"[Collector][on_acquisition_started] NUMERIC 通道: {items[:100] if items else '空'}")

        now = time.time()
        self._gather_start_time = now
        self._sample_deadline = now
        poll_s = scpi_poll_interval_s(self._rate_ms)
        self._emit_ui(f"[DEWETRON] 采集抽点 {int(poll_s * 1000)}ms（与设备刷新率一致）")
        self.is_gather.set()
        self._ready_to_gather = False
        if self._trip_screenshot_enabled and self._trip_monitor is not None:
            self._trip_monitor.reset()
            self._trip_shot_count = 0
            self._trip_event_count = 0
            self._trip_events = []
            self._trip_sample_buf = []
            self._trip_pending = None
            rate = max(int(self._rate_ms or 100), 20)
            need = int((self._trip_pre_s + self._trip_post_s + 1.0) * 1000 / rate) + 10
            self._trip_buf_max = max(50, min(2000, need))
        print("[Collector][on_acquisition_started] 采集线程开始工作")
        return True

    def stop_gathering(self):
        """幂等停止当前采集并完成当前 run。"""
        try:
            self._flush_pending_trip_shot(force=True)
        except Exception:
            pass
        try:
            self._stop_oxygen_store()
        except Exception:
            pass
        was_active = self.is_gather.is_set() or self._ready_to_gather or self._run_id is not None
        self.is_gather.clear()
        self._ready_to_gather = False
        if self._run_id is not None:
            self.finish_run()
        if was_active:
            self._log.info(f"[Collector] 停止采集，共 {self._total_rows} 行数据")
            if self._trip_screenshot_enabled and self._trip_event_count:
                summaries = []
                for ev in (self._trip_events or [])[-5:]:
                    tv = ev.get("trip_values") or {}
                    bits = []
                    if tv.get("u_v") is not None:
                        bits.append(f"U={float(tv['u_v']):.3f}V")
                    if tv.get("f_hz") is not None:
                        bits.append(f"F={float(tv['f_hz']):.3f}Hz")
                    if bits:
                        summaries.append(
                            f"{ev.get('wall_clock', '?')}({' '.join(bits)})"
                        )
                    else:
                        summaries.append(str(ev.get("wall_clock") or "?"))
                detail = "；".join(summaries)
                self._emit_ui(
                    f"[DEWETRON] 本段跳脱 {self._trip_event_count} 次：{detail}"
                )
        return was_active

    def _start_oxygen_store(self):
        """启动 Oxygen :STORE 录波（失败只告警，不阻断 NUMERIC）。"""
        self._oxygen_store_active = False
        self._oxygen_store_path = ""
        if not self._oxygen_store_enabled:
            return False
        try:
            from utils.dewetron_oxygen_store import (
                oxygen_store_path_candidates,
                parse_store_file_name_response,
                parse_store_state_response,
                scpi_store_file_name,
                store_state_is_active,
            )
        except Exception as exc:
            self._emit_ui(f"[DEWETRON] Oxygen 录波模块加载失败: {exc}")
            return False

        # 先停掉可能残留的 STORE
        self._send_controller(":STORE:STOP", "停止残留 STORE", "STORE STOP", timeout_ms=5000)
        time.sleep(0.3)

        candidates = oxygen_store_path_candidates(self._save_path or "")
        last_state = ""
        last_path = ""
        last_err = ""
        for path in candidates:
            last_path = path
            name_cmd = scpi_store_file_name(path)
            if not self._send_controller(
                name_cmd, f"设置 Oxygen 录波路径 {path}", "STORE FILE NAME", timeout_ms=5000
            ):
                continue
            if not self._send_controller(
                ":STORE:START", "启动 Oxygen 录波", "STORE START", timeout_ms=5000
            ):
                continue
            time.sleep(0.5)
            state_raw = self._query_controller(":STORE:STATE?", timeout_ms=5000)
            state = parse_store_state_response(state_raw)
            last_state = state
            if not store_state_is_active(state):
                err = self._query_controller(":SYSTEM:ERROR:ALL?", timeout_ms=3000)
                if err:
                    last_err = str(err).strip()
                # 再试下一个候选路径
                self._send_controller(
                    ":STORE:STOP", "停止失败的 STORE", "STORE STOP", timeout_ms=3000
                )
                time.sleep(0.2)
                continue

            # 录波已开始后再查路径（停着时 NAME? 固定返回 NONE，这是文档行为）
            actual_raw = self._query_controller(":STORE:FILE:NAME?", timeout_ms=5000)
            actual = parse_store_file_name_response(actual_raw) or path
            self._oxygen_store_path = actual.replace("/", "\\")
            self._oxygen_store_active = True
            self._emit_ui(
                f"[DEWETRON] 整段 Oxygen 录波已开始: {self._oxygen_store_path} "
                f"(STATE={state}；跳脱时会自动打标记，此刻不是跳脱)"
            )
            return True

        err_hint = f"；设备错误={last_err}" if last_err else ""
        self._oxygen_store_path = last_path
        self._emit_ui(
            f"[DEWETRON] Oxygen 录波未真正开始 STATE={last_state or 'Unknown'} "
            f"末次路径={last_path}{err_hint}；"
            f"已尝试默认目录文件名及 D:/E: 短路径。请在 Oxygen 里手动点一次存储确认默认可写目录"
        )
        return False

    def _stop_oxygen_store(self):
        """停止 Oxygen :STORE 录波。"""
        if not self._oxygen_store_active and not self._oxygen_store_enabled:
            return False
        ok = self._send_controller(
            ":STORE:STOP", "停止 Oxygen 录波", "STORE STOP", timeout_ms=5000
        )
        was = self._oxygen_store_active
        self._oxygen_store_active = False
        if was and ok:
            self._emit_ui(
                f"[DEWETRON] Oxygen 录波已停止: {self._oxygen_store_path or ''}"
            )
        return bool(ok)
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
            try:
                from utils.dewetron_recording import trim_leading_all_nan_samples

                trimmed = trim_leading_all_nan_samples(rows, rebase_time=True)
                dropped = max(0, len(rows) - len(trimmed))
            except Exception:
                trimmed = list(rows or [])
                dropped = 0
            # 若裁掉开头空点后变成 0 行、但库里其实有行：保留原始行，避免「空 CSV」
            if not trimmed and rows:
                trimmed = []
                for time_val, values in rows:
                    try:
                        tt = float(time_val)
                    except (TypeError, ValueError):
                        tt = 0.0
                    trimmed.append((tt, list(values or [])))
                dropped = 0
            if not trimmed:
                raw_count = 0
                try:
                    with self._db_lock:
                        raw_count = int(
                            self._conn.execute(
                                "SELECT COUNT(*) FROM de_data WHERE run_id = ?",
                                (run_id,),
                            ).fetchone()[0]
                            or 0
                        )
                except Exception:
                    raw_count = 0
                self._emit_ui(
                    f"[DEWETRON] 导出无有效测点: run_id={run_id} "
                    f"库内原始行={raw_count} 解码行={len(rows)} "
                    f"（请查操作日志是否出现过 START/采集已开始）"
                )
            csv_dir = os.path.dirname(csv_path)
            if csv_dir:
                os.makedirs(csv_dir, exist_ok=True)
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as output:
                writer = csv.writer(output)
                writer.writerow(header)
                expect_n = max(len(header) - 1, 0)
                places = self._clamp_csv_decimal_places(
                    getattr(self, "_csv_decimal_places", 4)
                )
                value_fmt = f"{{:.{places}f}}"
                for time_val, values in trimmed:
                    aligned = list(values or [])[:expect_n]
                    if len(aligned) < expect_n:
                        aligned.extend([float("nan")] * (expect_n - len(aligned)))
                    writer.writerow(
                        [f"{float(time_val):.4f}"]
                        + [value_fmt.format(float(value)) for value in aligned]
                    )
            msg = f"[Collector][export_run_to_csv] 导出完成: {csv_path} ({len(trimmed)} 行)"
            if dropped:
                msg += f"，已去掉开头空测点 {dropped} 行"
            print(msg)
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

    def set_save_path(self, csv_path):
        """Update the CSV path used by the next export / begin_run cycle."""
        self._save_path = str(csv_path or "")
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
            values = loads_channel_values(values_json)
            if not values and values_json not in (None, "", "[]"):
                # 非空原文却解不出 → 记一条，避免静默丢光
                continue
            decoded.append((time_val, values))
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

        rows = []
        for i, cmd in enumerate(commands):
            if len(cmd) < 3:
                continue
            raw_row = list(cmd[:10])
            if len(raw_row) < 10:
                raw_row.extend([''] * (10 - len(raw_row)))
            raw_row_json = json.dumps(raw_row, ensure_ascii=False, default=str)
            device = cmd[0] if len(cmd) > 0 else ''
            operation = cmd[1] if len(cmd) > 1 else ''
            command = cmd[2] if len(cmd) > 2 else ''
            params = [cmd[j] if len(cmd) > j else '' for j in range(3, 10)]
            wait_time = 0
            for idx in (8, 9):
                if len(cmd) > idx and cmd[idx] != '':
                    try:
                        wait_time = int(cmd[idx])
                    except (ValueError, TypeError):
                        pass
            rows.append(
                (
                    self._run_id,
                    i + 1,
                    device,
                    operation,
                    command,
                    params[0],
                    params[1],
                    params[2],
                    params[3],
                    params[4],
                    params[5],
                    params[6],
                    raw_row_json,
                    wait_time,
                )
            )

        with self._db_lock:
            self._conn.execute("DELETE FROM de_commands WHERE run_id = ?", (self._run_id,))
            if rows:
                self._conn.executemany(
                    "INSERT INTO de_commands (run_id, seq, device, operation, command, "
                    "param1, param2, param3, param4, param5, param6, param7, raw_row, wait_time) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    rows,
                )
            self._conn.commit()
        print(f"[Collector][save_commands] 保存 {len(rows)} 条命令到 run_id={self._run_id}")

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
        """在批次内创建 run；已有当前 run 时幂等返回其 ID（并刷新 csv_header）。"""
        if csv_header is not None:
            self._csv_header = list(csv_header)
        if self._run_id is not None:
            # 追加阶段可能早建了空 run；开测 prepare 后必须把最新表头写回库
            if self._conn and self._csv_header:
                try:
                    with self._db_lock:
                        self._conn.execute(
                            "UPDATE de_test_runs SET csv_header = ? WHERE id = ?",
                            (json.dumps(self._csv_header, ensure_ascii=False), self._run_id),
                        )
                        self._conn.commit()
                except sqlite3.Error as exc:
                    print(f"[Collector][begin_run] 刷新 csv_header 失败: {exc}")
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
        # 必须数量一致：仅用 substring 包含会在设备残留旧通道时误判成功
        reported = re.findall(r'"([^"]+)"', str(query_items))
        if reported:
            # 顺序可不一致：Oxygen 偶发重排；以集合相等为准
            if set(reported) != set(all_channels) or len(reported) != len(all_channels):
                print(
                    f"[Collector] NUMERIC ITEMs 不一致: "
                    f"expect={len(all_channels)} got={len(reported)}"
                )
                missing = [c for c in all_channels if c not in reported]
                extra = [c for c in reported if c not in all_channels]
                if missing:
                    print(f"[Collector] NUMERIC 缺少: {missing[:8]}")
                if extra:
                    print(f"[Collector] NUMERIC 多余: {extra[:8]}")
                return False
            if reported != all_channels:
                print(
                    "[Collector] NUMERIC ITEMs 顺序与设定不同，已按集合匹配放行: "
                    f"expect_head={all_channels[:3]} got_head={reported[:3]}"
                )
            return True
        return all(channel in query_items for channel in all_channels)

    def _collect_loop(self):
        """守护线程主循环。"""
        print("[Collector][_collect_loop] 守护线程已启动")
        loop_count = 0

        while not self._stop_event.is_set():
            if self.is_gather.is_set():
                interval_s = scpi_poll_interval_s(self._rate_ms)
                self._collect_one_point(interval_s)
                loop_count += 1
                if loop_count % 50 == 0:
                    print(f"[Collector][_collect_loop] 已采集 {self._total_rows} 行")
            else:
                time.sleep(0.05)

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
        """采集一个点；周期与界面设定刷新率一致。"""
        t_start = time.time()
        success = False
        try:
            raw_val = self._query_controller(":NUM:NORM:VALue?", timeout_ms=5000)
            if raw_val:
                if self._total_rows == 0:
                    print(f"[Collector][_collect_one_point] 首次响应: {repr(raw_val[:500])}")
                    if ',' not in raw_val:
                        print("[Collector][_collect_one_point] 警告：响应中没有逗号，可能只有时间戳")
                    # 首点对齐零点，避免准备耗时挤进 Time[s]
                    self._gather_start_time = time.time()
                    self._sample_deadline = self._gather_start_time

                row = self._align_numeric_row(self._parse_value(raw_val))
                if row and self._conn and self._run_id is not None:
                    elapsed = time.time() - float(self._gather_start_time or time.time())
                    values_json = dumps_channel_values(row)
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
                    self._maybe_trip_screenshot(row)
        except Exception as exc:
            print(f"[Collector][_collect_one_point] 异常: {exc}")

        interval = max(float(interval_s), 0.001)
        if success:
            elapsed = time.time() - t_start
            sleep_time = max(interval - elapsed, 0.0)
            self._sample_deadline = time.time() + sleep_time
        else:
            sleep_time = self._next_no_data_delay(interval)
        if sleep_time > 0:
            time.sleep(sleep_time)
        return success

    def _inject_current_channels_for_trip(self, valid, device_channels, warnings):
        """若尚无电流通道，从设备通道表补 I1/I2/I3（或 I_tRMS）。"""
        from utils.dewetron_trip_monitor import find_current_indices

        phase_idx, total_idx = find_current_indices(valid)
        if phase_idx or total_idx is not None:
            return valid

        preferred = ("I1_tRMS", "I2_tRMS", "I3_tRMS", "I_tRMS")
        added = []
        out = list(valid)
        for short in preferred:
            matched = next(
                (ch for ch in sorted(device_channels) if ch == short or ch.startswith(short + "@")),
                None,
            )
            if matched and matched not in out:
                out.append(matched)
                added.append(matched)
        if added:
            # 仅日志；不改 PrepareResult.warnings 契约，避免影响既有 UI/测试
            print(f"[Collector][prepare] 跳脱监测补通道: {added}")
            return out
        print("[Collector][prepare] 跳脱值监测：设备无 I1/I2/I3，本段无法自动测跳脱")
        return valid

    def _inject_uf_channels_for_trip_value(self, valid, device_channels):
        """补电压/频率通道，便于跳脱时直接读跳脱值。"""
        from utils.dewetron_trip_monitor import find_frequency_index, find_voltage_indices

        out = list(valid)
        added = []
        if not find_voltage_indices(out):
            for short in ("U1_tRMS", "U2_tRMS", "U3_tRMS", "U_tRMS"):
                matched = next(
                    (
                        ch
                        for ch in sorted(device_channels)
                        if ch == short or ch.startswith(short + "@")
                    ),
                    None,
                )
                if matched and matched not in out:
                    out.append(matched)
                    added.append(matched)
        if find_frequency_index(out) is None:
            for short in ("F_fund", "Freq", "Frequency"):
                matched = next(
                    (
                        ch
                        for ch in sorted(device_channels)
                        if ch == short or ch.startswith(short + "@")
                    ),
                    None,
                )
                if matched and matched not in out:
                    out.append(matched)
                    added.append(matched)
                    break
        if added:
            print(f"[Collector][prepare] 跳脱值补通道: {added}")
        return out

    def _setup_trip_monitor_from_fields(self):
        """按当前 NUMERIC 字段重建跳脱监视器。"""
        from utils.dewetron_trip_monitor import TripMonitor, find_current_indices

        if not self._trip_screenshot_enabled:
            self._trip_monitor = None
            return
        phase_idx, total_idx = find_current_indices(self._fields or [])
        if not phase_idx and total_idx is None:
            self._trip_monitor = None
            msg = "[Collector] 跳脱值监测未启用：采集字段中无电流通道"
            if msg != self._trip_last_warn:
                print(msg)
                self._trip_last_warn = msg
            return
        self._trip_monitor = TripMonitor(
            phase_indices=phase_idx,
            total_index=total_idx,
            startup_ignore_s=float(self._trip_startup_ignore_s),
            arm_hold_s=float(self._trip_arm_hold_s),
        )
        print(
            f"[Collector] 跳脱值监视已就绪 phase_idx={phase_idx} total_idx={total_idx} "
            f"startup_ignore={self._trip_startup_ignore_s}s arm_hold={self._trip_arm_hold_s}s"
        )

    def _maybe_trip_screenshot(self, values):
        """跳脱检测：写操作日志时刻；可选再出静态 PNG。"""
        mon = self._trip_monitor
        if mon is None or not self._trip_screenshot_enabled:
            return

        elapsed = time.time() - float(self._gather_start_time or time.time())
        try:
            self._trip_sample_buf.append((elapsed, list(values)))
            if len(self._trip_sample_buf) > self._trip_buf_max:
                overflow = len(self._trip_sample_buf) - self._trip_buf_max
                del self._trip_sample_buf[:overflow]
        except Exception:
            pass

        if self._trip_pending is not None:
            self._flush_pending_trip_shot(force=False, now_elapsed=elapsed)
            return

        try:
            event = mon.feed(values, now_mono=time.monotonic(), elapsed_s=elapsed)
        except Exception as exc:
            print(f"[Collector][trip] 检测异常: {exc}")
            return
        if event is None:
            return

        from utils.dewetron_trip_monitor import (
            extract_trip_values,
            format_trip_value_log,
        )
        from utils.dewetron_oxygen_store import trip_wall_clock_from_gather_start

        stamp = time.strftime("%Y%m%d_%H%M%S")
        wall_clock, _wall_unix = trip_wall_clock_from_gather_start(
            float(self._gather_start_time or time.time()), elapsed
        )
        trip_values = extract_trip_values(values, self._fields or [])
        self._trip_pending = {
            "trip_elapsed": elapsed,
            "stamp": stamp,
            "reason": event.reason,
            "wall_clock": wall_clock,
            "trip_values": trip_values,
        }
        self._trip_event_count += 1
        self._trip_events.append(
            {
                "elapsed": elapsed,
                "wall_clock": wall_clock,
                "reason": event.reason,
                "trip_values": trip_values,
            }
        )
        self._emit_ui(
            format_trip_value_log(
                wall_clock=wall_clock,
                elapsed_s=elapsed,
                reason=event.reason,
                trip_values=trip_values,
            )
        )
        # 不再截图 / 打 Oxygen 标记
        self._trip_pending = None

    def _add_oxygen_trip_markers(self, *, trip_elapsed: float, reason: str) -> bool:
        """已停用：实验室改为自动测跳脱值，不再写 Oxygen 标记。"""
        return False

    def _flush_pending_trip_shot(self, *, force: bool = False, now_elapsed: Optional[float] = None):
        pending = self._trip_pending
        if not pending:
            return
        trip_elapsed = float(pending["trip_elapsed"])
        if now_elapsed is None:
            now_elapsed = time.time() - float(self._gather_start_time or time.time())
        if (not force) and (now_elapsed < trip_elapsed + float(self._trip_post_s)):
            return

        stamp = str(pending.get("stamp") or time.strftime("%Y%m%d_%H%M%S"))
        reason = str(pending.get("reason") or "trip")
        self._trip_pending = None

        if not self._trip_render_period_png and not self._trip_capture_oxygen:
            return

        try:
            from utils.dewetron_trip_period_shot import (
                build_trip_oxygen_path,
                build_trip_period_path,
                render_trip_period_png,
                slice_trip_period,
            )
            from utils.oxygen_screenshot import capture_oxygen_window

            if self._trip_render_period_png:
                period = [
                    s
                    for s in self._trip_sample_buf
                    if (trip_elapsed - float(self._trip_pre_s))
                    <= float(s[0])
                    <= (trip_elapsed + float(self._trip_post_s) + 0.05)
                ]
                if len(period) < 2:
                    period = slice_trip_period(
                        self._trip_sample_buf,
                        pre_s=self._trip_pre_s,
                        post_s=self._trip_post_s,
                    )

                png = build_trip_period_path(self._save_path, stamp=stamp)
                ok, msg = render_trip_period_png(
                    period,
                    self._fields or [],
                    png,
                    title=f"{self._test_type or 'dewetron'} trip",
                    trip_time_s=trip_elapsed,
                )
                if ok:
                    self._trip_shot_count += 1
                    self._emit_ui(f"[Collector][trip] {reason} -> {msg}")
                else:
                    self._emit_ui(f"[Collector][trip] {reason}，时间段截图失败: {msg}")

            if self._trip_capture_oxygen:
                oxy = build_trip_oxygen_path(self._save_path, stamp=stamp)
                ok2, msg2 = capture_oxygen_window(oxy)
                self._emit_ui(
                    f"[Collector][trip] Oxygen附属: {msg2}"
                    if ok2
                    else f"[Collector][trip] Oxygen附属失败: {msg2}"
                )
        except Exception as exc:
            print(f"[Collector][trip] 截图异常: {exc}")

    def _align_numeric_row(self, row):
        """将 VALue? 解析结果对齐到当前 _fields 长度，避免 CSV 列错位。"""
        if not row:
            return None
        expect_n = len(self._fields or [])
        if expect_n <= 0:
            return list(row)
        if len(row) == expect_n:
            return list(row)
        msg = (
            f"[Collector] NUMERIC 列数不匹配: got={len(row)} expect={expect_n}"
        )
        if self._total_rows == 0 or (self._total_rows % 50 == 0):
            print(msg)
            try:
                self._log.info(msg)
            except Exception:
                pass
        if len(row) > expect_n:
            return list(row[:expect_n])
        return list(row) + [float("nan")] * (expect_n - len(row))

    def _parse_value(self, raw_val):
        """解析 :NUM:NORM:VAL? 返回值，返回数值列表。"""
        if not raw_val:
            return None

        clean = str(raw_val).strip()
        # 去掉 SCPI 回显前缀（如 :NUM:NORM:VALue? ），不要用首个空格——
        # ABS-TIME 形如 "2026-09-21 14:17:38" 时会误切。
        clean = re.sub(r"^:[^\s?]+\??\s*", "", clean, count=1).strip()
        if not clean:
            return None

        values = [v.strip() for v in clean.split(",")]

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
                    nums.append(float("nan"))

        return nums if nums else None
