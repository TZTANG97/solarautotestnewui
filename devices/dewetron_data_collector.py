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


# 数据库固定路径
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
DB_PATH = os.path.join(DB_DIR, 'db.sqlite')
INIT_SQL_PATH = os.path.join(DB_DIR, 'init.sql')


def init_database():
    """初始化 SQLite 数据库：如果表不存在则执行 init.sql。

    在项目启动时调用，确保数据库结构就绪。
    """
    # 确保 database 目录存在
    os.makedirs(DB_DIR, exist_ok=True)

    # 检查是否已初始化（检查 de_test_runs 表是否存在）
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='de_test_runs'"
    )
    if cursor.fetchone():
        # 表已存在，检查 de_data 表
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='de_data'"
        )
        if cursor.fetchone():
            conn.close()
            print(f"[DB] 数据库已初始化: {DB_PATH}")
            return True

    # 表不存在，执行 init.sql
    print(f"[DB] 数据库未初始化，执行 {INIT_SQL_PATH} ...")
    if not os.path.exists(INIT_SQL_PATH):
        print(f"[DB] 错误: {INIT_SQL_PATH} 不存在")
        conn.close()
        return False

    with open(INIT_SQL_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.executescript(sql)
    conn.close()
    print(f"[DB] 数据库初始化完成: {DB_PATH}")
    return True


# MaxUpdateRate 文本 -> 毫秒数
RATE_MAP = {
    'Default': 100,
    'SYNC to HARMONIC': 200,
    'SYNC_TO_HARMONIC': 200,
}


def parse_rate_ms(rate_text):
    """将 MaxUpdateRate 文本转换为毫秒数。"""
    rate_text = rate_text.strip()
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

    def __init__(self, controller, logger):
        """初始化采集器。

        Args:
            controller: DewetronController 实例（已连接）
            logger: 日志对象，需有 info() 方法
        """
        self._ctrl = controller
        self._log = logger
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
        self._seq = 0

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
        """停止守护线程。"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
        self._log.info("[Collector] 守护线程已停止")

    def prepare(self, fields, rate_text, test_type, save_path):
        """采集前准备：校验字段、映射 RATE、连接数据库。

        Args:
            fields: 用户选择的字段列表
            rate_text: MaxUpdateRate 文本
            test_type: 测试类型（如 'flicker', 'harmonic', 'dewetron'）
            save_path: CSV 保存路径

        Returns:
            tuple: (valid_fields, warnings)
        """
        warnings = []
        print(f"[Collector][prepare] fields={fields}, rate={rate_text}, "
              f"test_type={test_type}, save_path={save_path}")

        # 1. 查询设备实际通道
        device_channels = set()
        raw = self._ctrl._query(":CHANNELLIST:NAMES?", timeout_ms=30000)
        if raw:
            for m in re.finditer(r'"(\d+)","([^"]+)"', raw):
                device_channels.add(m.group(2))

        if not device_channels:
            warnings.append("无法查询设备通道列表，跳过校验")
            self._fields = list(fields)
        else:
            # 从设备通道中提取电力组后缀（如 @AC, @POWER/0 等）
            power_suffixes = set()
            for ch in device_channels:
                if '@' in ch:
                    suffix = ch[ch.index('@'):]
                    power_suffixes.add(suffix)
            print(f"[Collector][prepare] 设备电力组后缀: {power_suffixes}")

            # 排序后缀：优先使用不带 _AVG 的（实时数据）
            def suffix_priority(s):
                # 不带 _AVG 的优先级最高
                if '_AVG' not in s:
                    return 0
                # 带 _AVG 的按长度排序
                return len(s)
            sorted_suffixes = sorted(power_suffixes, key=suffix_priority)
            print(f"[Collector][prepare] 排序后后缀: {sorted_suffixes}")

            valid = []
            for field in fields:
                # 1. 直接匹配
                if field in device_channels:
                    valid.append(field)
                    continue
                # 2. 按优先级尝试电力组后缀
                matched = False
                for suffix in sorted_suffixes:
                    full_name = f"{field}{suffix}"
                    if full_name in device_channels:
                        valid.append(full_name)
                        matched = True
                        break
                if matched:
                    continue
                # 3. 模糊匹配
                matched = [ch for ch in device_channels if ch.startswith(field)]
                if matched:
                    valid.append(matched[0])
                    continue
                warnings.append(f"字段 '{field}' 在设备上不存在，已跳过")
            self._fields = valid

        # 2. 构建 SCPI 通道名和 CSV 表头
        self._scpi_channels = list(self._fields)
        self._csv_header = ['Time [s]']
        for ch in self._fields:
            short_id = ch.split('@')[0] if '@' in ch else ch
            suffix = ch[ch.index('@'):] if '@' in ch else ''
            if short_id in self.CSV_HEADER_MAP:
                # 拼接后缀：如 "U1_tRMS [V]" + "@AC" = "U1_tRMS@AC [V]"
                self._csv_header.append(self.CSV_HEADER_MAP[short_id][0] + suffix)
            else:
                self._csv_header.append(ch)

        # 3. 映射采集频率
        self._rate_ms = parse_rate_ms(rate_text)

        # 4. 设置保存路径和测试类型
        self._save_path = save_path
        self._test_type = test_type

        # 5. 连接 SQLite 数据库
        self._connect_database()

        print(f"[Collector][prepare] 完成: {len(self._fields)} 个有效字段, "
              f"间隔 {self._rate_ms}ms, test_type={test_type}")
        return self._fields, warnings

    def start_gathering(self):
        """开始采集配置（不启动采集线程查询）。"""
        print(f"[Collector][start_gathering] === 开始采集准备 ===")

        # 重置采集状态
        self._total_rows = 0
        self._seq = 0
        self._gather_start_time = time.time()

        # 插入 de_test_runs 记录
        self._insert_test_run()

        # 先停止采集（如果正在运行）
        acq_state = self._ctrl._query(":ACQUISITION:STATE?")
        print(f"[Collector][start_gathering] 当前采集状态: {acq_state}")
        if acq_state == 'Started':
            self._ctrl._send(":ACQUISITION:STOP", "停止采集", "ACQUISITION STOP")
            time.sleep(0.5)

        # 配置设备 NUMERIC 输出
        self._setup_numeric()

        # 设置 RATE（在采集停止时设置）
        self._ctrl._send(f":RATE {self._rate_ms}ms",
                         f"设置采集间隔 {self._rate_ms}ms", "RATE")
        # 验证 RATE 是否生效
        rate_val = self._ctrl._query(":RATE?")
        print(f"[Collector][start_gathering] RATE 验证: 设置={self._rate_ms}ms, 实际={rate_val}")

        # 标记准备完成
        self._ready_to_gather = True
        print(f"[Collector][start_gathering] 准备完成，等待 :ACQUISITION:START")

    def on_acquisition_started(self):
        """在 :ACQUISITION:START 发送后调用，正式启动采集线程查询。"""
        if not self._ready_to_gather:
            return

        # 等待设备稳定（ :ACQUISITION:START 需要时间生效）
        time.sleep(1.0)

        # 验证采集状态
        acq_state = self._ctrl._query(":ACQUISITION:STATE?", timeout_ms=5000)
        print(f"[Collector][on_acquisition_started] 采集状态: {acq_state}")

        # 验证 NUMERIC 通道
        items = self._ctrl._query(":NUM:NORM:ITEMs?", timeout_ms=5000)
        print(f"[Collector][on_acquisition_started] NUMERIC 通道: {items[:100] if items else '空'}")

        # 启动采集
        self.is_gather.set()
        self._ready_to_gather = False
        print(f"[Collector][on_acquisition_started] 采集线程开始工作")

    def stop_gathering(self):
        """停止采集，更新 de_test_runs 记录。"""
        self.is_gather.clear()
        self._update_test_run_end()
        self._log.info(f"[Collector] 停止采集，共 {self._total_rows} 行数据")

    def end_batch(self):
        """结束当前批次，更新批次结束时间。"""
        if not self._conn or not self._batch_id:
            return
        end_time = time.strftime('%Y-%m-%d %H:%M:%S')
        with self._db_lock:
            self._conn.execute(
                "UPDATE de_test_batch SET end_time = ? WHERE id = ?",
                (end_time, self._batch_id)
            )
            self._conn.commit()
        print(f"[Collector][end_batch] 批次结束: {self._batch_uid}")
        self._batch_id = None
        self._batch_uid = None

    def export_to_csv(self, csv_path=None):
        """将当前 run_id 的数据导出到 CSV。"""
        if not self._conn or not self._run_id:
            return None

        csv_path = csv_path or self._save_path
        if not csv_path:
            return None

        try:
            row = self._conn.execute(
                "SELECT csv_header FROM de_test_runs WHERE id = ?", (self._run_id,)
            ).fetchone()
            if not row or not row[0]:
                return None
            header = json.loads(row[0])

            rows = self._conn.execute(
                "SELECT time, channel_values FROM de_data WHERE run_id = ? ORDER BY seq",
                (self._run_id,)
            ).fetchall()

            csv_dir = os.path.dirname(csv_path)
            if csv_dir and not os.path.exists(csv_dir):
                os.makedirs(csv_dir, exist_ok=True)

            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for time_val, values_json in rows:
                    values = json.loads(values_json)
                    writer.writerow([f"{time_val:.4f}"] + [f"{v:.7f}" for v in values])

            print(f"[Collector][export_to_csv] 导出完成: {csv_path} ({len(rows)} 行)")
            return csv_path

        except Exception as e:
            print(f"[Collector][export_to_csv] 导出异常: {e}")
            return None

    def get_save_path(self):
        """获取当前保存路径。"""
        return self._save_path

    def get_total_rows(self):
        """获取已采集的总行数。"""
        return self._total_rows

    def get_run_id(self):
        """获取当前 de_test_runs.id。"""
        return self._run_id

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

        for i, cmd in enumerate(commands):
            if len(cmd) < 3:
                continue
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
                    "param1, param2, param3, param4, param5, param6, param7, wait_time) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (self._run_id, i + 1, device, operation, command,
                     params[0], params[1], params[2], params[3], params[4], params[5], params[6],
                     wait_time)
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
            "param4, param5, param6, param7, wait_time "
            "FROM de_commands WHERE run_id = ? ORDER BY seq",
            (target_run_id,)
        ).fetchall()

        commands = []
        for row in rows:
            device, operation, command = row[0], row[1], row[2]
            params = list(row[3:10])
            wait_time = row[10]

            # 重建命令数组（与 strArrayTest 格式一致）
            cmd = ['' for _ in range(10)]
            cmd[0] = device
            cmd[1] = operation
            cmd[2] = command
            for j, p in enumerate(params):
                if j + 3 < len(cmd):
                    cmd[j + 3] = p or ''
            # wait_time 放在索引8（或9，根据原逻辑）
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
        """连接 SQLite 数据库。"""
        print(f"[Collector][_connect_database] 连接数据库: {DB_PATH}")
        self._conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._conn.execute('PRAGMA journal_mode=WAL')

    def start_batch(self):
        """开始一个新的测试批次。

        每次连接 DEWETRON 并准备测试时调用，创建一个新的批次。
        同一test_type 的后续追加都属于这个批次，直到下次连接。
        """
        if not self._conn:
            self._connect_database()

        # 生成批次唯一标识: test_type_YYYYMMDD_HHMMSS
        batch_uid = f"{self._test_type}_{time.strftime('%Y%m%d_%H%M%S')}"
        start_time = time.strftime('%Y-%m-%d %H:%M:%S')

        with self._db_lock:
            cursor = self._conn.execute(
                "INSERT INTO de_test_batch (batch_uid, test_type, start_time, save_path) "
                "VALUES (?, ?, ?, ?)",
                (batch_uid, self._test_type, start_time, self._save_path)
            )
            self._batch_id = cursor.lastrowid
            self._batch_uid = batch_uid
            self._conn.commit()
        self._conn.commit()
        print(f"[Collector][start_batch] 新批次: {batch_uid} (batch_id={self._batch_id})")
        return self._batch_id

    def _get_next_version(self):
        """获取当前批次内的下一个版本号。"""
        if not self._batch_id:
            return 1
        row = self._conn.execute(
            "SELECT MAX(version) FROM de_test_runs WHERE batch_id = ?",
            (self._batch_id,)
        ).fetchone()
        return (row[0] or 0) + 1

    def _insert_test_run(self):
        """插入一条 de_test_runs 记录（在当前批次内）。"""
        if not self._batch_id:
            self.start_batch()

        version = self._get_next_version()
        start_time = time.strftime('%Y-%m-%d %H:%M:%S')
        csv_header_json = json.dumps(self._csv_header)

        with self._db_lock:
            cursor = self._conn.execute(
                "INSERT INTO de_test_runs (batch_id, version, start_time, csv_header) "
                "VALUES (?, ?, ?, ?)",
                (self._batch_id, version, start_time, csv_header_json)
            )
            self._run_id = cursor.lastrowid

            # 更新批次的 total_versions
            self._conn.execute(
                "UPDATE de_test_batch SET total_versions = ? WHERE id = ?",
                (version, self._batch_id)
            )
            self._conn.commit()
        print(f"[Collector][_insert_test_run] {self._batch_uid} v{version} (run_id={self._run_id})")

    def _update_test_run_end(self):
        """更新 de_test_runs 的结束时间和总行数。"""
        if not self._conn or not self._run_id:
            return
        end_time = time.strftime('%Y-%m-%d %H:%M:%S')
        with self._db_lock:
            self._conn.execute(
                "UPDATE de_test_runs SET end_time = ?, total_rows = ? WHERE id = ?",
                (end_time, self._total_rows, self._run_id)
            )
            self._conn.commit()

    def _setup_numeric(self):
        """配置设备 NUMERIC 输出通道。"""
        self._ctrl._send(":NUM:NORM:CLEar ALL", "清除旧配置", "NUM CLEAR")

        if not self._scpi_channels:
            return

        all_channels = ['ABS-TIME'] + self._scpi_channels
        items_str = ','.join(f'"{c}"' for c in all_channels)
        self._ctrl._send(f":NUM:NORM:ITEMs {items_str}",
                         "设置 NUMERIC 输出通道", "NUM ITEMS")
        self._ctrl._send(f":NUM:NORM:NUMber {len(all_channels)}",
                         "设置传输数量", "NUM NUMBER")

        query_items = self._ctrl._query(":NUM:NORM:ITEMs?")
        print(f"[Collector] NUMERIC 配置确认: {query_items}")

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

    def _collect_one_point(self, interval_s):
        """采集一个数据点，直接写入 SQLite。"""
        t_start = time.time()

        try:
            raw_val = self._ctrl._query(":NUM:NORM:VALue?", timeout_ms=5000)
            if not raw_val:
                return

            # 首次采集打印完整响应，便于调试
            if self._total_rows == 0:
                print(f"[Collector][_collect_one_point] 首次响应: {repr(raw_val[:500])}")
                # 检查响应格式
                if ',' not in raw_val:
                    print(f"[Collector][_collect_one_point] 警告：响应中没有逗号，可能只有时间戳")

            row = self._parse_value(raw_val)
            if not row:
                return

            elapsed = time.time() - self._gather_start_time

            if self._total_rows == 0:
                print(f"[Collector][_collect_one_point] 首条数据: [{elapsed:.4f}, ...]")

            # 直接写入 SQLite
            values_json = json.dumps(row)
            with self._db_lock:
                self._conn.execute(
                    "INSERT INTO de_data (run_id, seq, time, channel_values) VALUES (?, ?, ?, ?)",
                    (self._run_id, self._seq, round(elapsed, 4), values_json)
                )
                self._conn.commit()
            self._seq += 1
            self._total_rows += 1

        except Exception as e:
            print(f"[Collector][_collect_one_point] 异常: {e}")

        # 精确 sleep
        elapsed = time.time() - t_start
        sleep_time = interval_s - elapsed
        if sleep_time > 0.001:
            time.sleep(sleep_time)

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
