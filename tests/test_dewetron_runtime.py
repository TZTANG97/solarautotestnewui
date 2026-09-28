"""Runtime contracts for DEWETRON controller, collector, and data viewer."""

import csv
import os
import sqlite3
from unittest.mock import patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from Dialog_DEWETRON_DataViewer import DialogDEWETRONDataViewer
from devices.dewetron_controller import DewetronController
from devices.dewetron_data_collector import (
    DewetronDataCollector,
    PrepareResult,
    init_database,
)


class FakeLogger:
    """Collect log lines without depending on the application logger."""

    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(message)


class FakeHandle:
    """Minimal VISA handle that records calls and exposes timeout behavior."""

    def __init__(self):
        self.timeout = 1234
        self.writes = []
        self.responses = {}
        self.closed = False

    def write(self, command):
        self.writes.append(command)

    def close(self):
        self.closed = True

    def query(self, command):
        response = self.responses.get(command, "")
        if isinstance(response, Exception):
            raise response
        return response


class FakeController:
    """Public-controller fake used by collector tests."""

    def __init__(self, channels=None):
        self.connected = True
        self.channels = channels or ['U1_tRMS@AC']
        self.state = 'Stopped'
        self.numeric_items = ''
        self.values = []
        self.sent = []

    def query_command(self, command, timeout_ms=30000):
        if command == ':CHANNELLIST:NAMES?':
            return ','.join(
                f'"{index}","{channel}"'
                for index, channel in enumerate(self.channels, start=1)
            )
        if command == ':ACQUISITION:STATE?':
            return self.state
        if command == ':NUM:NORM:ITEMs?':
            return self.numeric_items
        if command == ':RATE?':
            return '100ms'
        if command == ':NUM:NORM:VALue?':
            if not self.values:
                return None
            value = self.values.pop(0)
            if isinstance(value, Exception):
                raise value
            return value
        return None

    def send_command(self, command, *args, **kwargs):
        self.sent.append(command)
        if command.startswith(':NUM:NORM:ITEMs '):
            self.numeric_items = command.split(' ', 1)[1]
        return True

    def stop_acquisition(self):
        self.sent.append(':ACQUISITION:STOP')
        self.state = 'Stopped'
        return True


@pytest.fixture(scope='module')
def qapp():
    """Provide one offscreen QApplication for viewer tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def runtime(tmp_path):
    """Return a prepared collector backed by a temporary SQLite database."""
    controller = FakeController()
    collector = DewetronDataCollector(
        controller, FakeLogger(), db_path=str(tmp_path / 'runtime.sqlite')
    )
    result = collector.prepare(
        ['U1_tRMS'], '100', 'flicker', str(tmp_path / 'current.csv')
    )
    assert result.success
    yield controller, collector
    collector.stop()


def test_controller_public_start_stop_and_timeout_restore():
    logger = FakeLogger()
    controller = DewetronController(logger, lambda *_: None, lambda: '')
    handle = FakeHandle()
    controller.handle = handle
    controller.connected = True

    assert controller.send_command(':CUSTOM', timeout_ms=9000)
    assert handle.timeout == 1234
    assert controller.start_acquisition()
    assert controller.stop_acquisition()
    assert controller.send_start()
    assert controller.send_stop()
    assert handle.writes == [
        ':CUSTOM',
        ':ACQUISITION:START',
        ':ACQUISITION:STOP',
        ':ACQUISITION:START',
        ':ACQUISITION:STOP',
    ]

    handle.responses[':RATE?'] = '100ms\r\n'
    assert controller.query_command(':RATE?', timeout_ms=4000) == '100ms'
    assert handle.timeout == 1234


def test_visa_session_error_and_reconnect_closes_socket():
    from devices.dewetron_controller import is_visa_session_error

    assert is_visa_session_error("VI_ERROR_TMO (-1073807339)")
    assert is_visa_session_error("VI_ERROR_CONN_LOST")
    assert not is_visa_session_error("syntax error")

    from devices.dewetron_controller import is_visa_conn_lost, is_visa_timeout

    assert is_visa_timeout("VI_ERROR_TMO")
    assert not is_visa_conn_lost("VI_ERROR_TMO")
    assert is_visa_conn_lost("VI_ERROR_CONN_LOST")

    logger = FakeLogger()
    controller = DewetronController(logger, lambda *_: None, lambda: "")
    old = FakeHandle()
    controller.handle = old
    controller.connected = True
    controller.resource = "TCPIP0::192.168.40.23::10001::SOCKET"
    new = FakeHandle()

    def _fake_connect(tcp_addr, silent=False):
        controller.handle = new
        controller.connected = True
        controller.resource = tcp_addr
        return new, "1"

    controller.connect = _fake_connect
    assert controller._reconnect()
    assert old.closed is True
    assert controller.handle is new


def test_query_timeout_does_not_reconnect_or_mark_disconnected():
    logger = FakeLogger()
    popped = []
    controller = DewetronController(logger, lambda msg, *_: popped.append(msg), lambda: "")
    handle = FakeHandle()
    handle.responses[":CHANNELLIST:NAMES?"] = Exception("VI_ERROR_TMO (-1073807339)")
    controller.handle = handle
    controller.connected = True
    controller.resource = "TCPIP0::192.168.40.23::10001::SOCKET"
    reconnects = []
    controller.connect = lambda *a, **k: reconnects.append((a, k)) or (None, "0")
    assert controller.query_command(":CHANNELLIST:NAMES?", timeout_ms=1000) is None
    assert controller.connected is True
    assert handle.closed is False
    assert reconnects == []
    assert popped == []


def test_prepare_retries_empty_channellist(tmp_path, monkeypatch):
    class DelayedNames(FakeController):
        def __init__(self):
            super().__init__(channels=["U1_tRMS@AC"])
            self.lookups = 0

        def wait_scpi_ready(self, attempts=8, delay_seconds=1.0, timeout_ms=5000):
            return True

        def query_command(self, command, timeout_ms=30000):
            if command == ":CHANNELLIST:NAMES?":
                self.lookups += 1
                if self.lookups < 3:
                    return ""
            return super().query_command(command, timeout_ms=timeout_ms)

    monkeypatch.setattr("devices.dewetron_data_collector.time.sleep", lambda *_a, **_k: None)
    ctrl = DelayedNames()
    collector = DewetronDataCollector(
        ctrl, FakeLogger(), db_path=str(tmp_path / "retry.sqlite")
    )
    result = collector.prepare(["U1_tRMS"], "100", "staticqu", str(tmp_path / "a.csv"))
    assert result.success
    assert ctrl.lookups >= 3
    collector.stop()


def test_prepare_failures_and_iterable_success(tmp_path):
    no_controller = DewetronDataCollector(None, FakeLogger(), str(tmp_path / 'none.sqlite'))
    result = no_controller.prepare(['U1_tRMS'], '100', 'flicker', '')
    assert isinstance(result, PrepareResult)
    assert not result.success and result.error
    assert not no_controller._ready_to_gather

    disconnected = FakeController()
    disconnected.connected = False
    collector = DewetronDataCollector(
        disconnected, FakeLogger(), str(tmp_path / 'disconnected.sqlite')
    )
    assert not collector.prepare(['U1_tRMS'], '100', 'flicker', '').success

    connected = FakeController()
    collector = DewetronDataCollector(
        connected, FakeLogger(), str(tmp_path / 'valid.sqlite')
    )
    assert not collector.prepare([], '100', 'flicker', '').success
    connected.channels = []
    assert not collector.prepare(['U1_tRMS'], '100', 'flicker', '').success
    connected.channels = ['I1_tRMS@AC']
    assert not collector.prepare(['U1_tRMS'], '100', 'flicker', '').success

    connected.channels = ['U1_tRMS@AC']
    success = collector.prepare(['U1_tRMS', 'missing'], '100', 'flicker', '')
    valid_fields, warnings = success
    assert success.success
    assert valid_fields == ['U1_tRMS@AC']
    assert warnings == ["字段 'missing' 在设备上不存在，已跳过"]
    collector.stop()


def test_start_state_validation_and_idempotent_lifecycle(runtime):
    controller, collector = runtime
    first_run_id = collector.begin_run()
    assert collector.start_gathering()
    assert collector.current_run()['id'] == first_run_id
    assert collector.start_gathering()
    assert collector.current_run()['id'] == first_run_id
    assert len(collector.get_batch_runs(collector.current_batch()['id'])) == 1

    controller.state = 'Stopped'
    assert not collector.on_acquisition_started()
    assert not collector.is_gather.is_set()

    controller.state = 'Started'
    assert collector.on_acquisition_started()
    assert collector.is_gather.is_set()
    assert collector.stop_gathering()
    assert collector.current_run() is None
    assert not collector.stop_gathering()

    assert collector.begin_run()
    second_run_id = collector.current_run()['id']
    assert collector.begin_run() == second_run_id
    assert collector.finish_run()
    assert not collector.finish_run()
    assert collector.finish_batch()
    assert not collector.finish_batch()


def test_setup_command_failures_prevent_ready_state(runtime):
    controller, collector = runtime
    original_send = controller.send_command

    def fail_numeric(command, *args, **kwargs):
        if command.startswith(':NUM:NORM:ITEMs '):
            return False
        return original_send(command, *args, **kwargs)

    controller.send_command = fail_numeric
    assert not collector.start_gathering()
    assert collector.current_run() is None
    assert not collector._ready_to_gather


def test_no_data_and_query_failure_backoff_always_sleep(runtime):
    controller, collector = runtime
    collector.begin_run()
    collector._gather_start_time = 0
    controller.values = [None, RuntimeError('query failed'), ':NUM:NORM:VALue? "t",1.25']

    with patch('devices.dewetron_data_collector.time.sleep') as sleep:
        assert not collector._collect_one_point(0.1)
        assert not collector._collect_one_point(0.1)
        assert collector._collect_one_point(0.1)

    delays = [call.args[0] for call in sleep.call_args_list]
    assert delays[0] == pytest.approx(0.1)
    assert delays[1] == pytest.approx(0.2)
    assert delays[2] >= 0.001
    assert all(0 < delay <= 5.0 for delay in delays)
    assert collector._no_data_backoff_s == 0.0


def test_public_data_apis_and_csv_export(runtime, tmp_path):
    _controller, collector = runtime
    batch_id = collector.begin_batch()
    run_id = collector.begin_run()
    with collector._db_lock:
        collector._conn.execute(
            'INSERT INTO de_data (run_id, seq, time, channel_values) VALUES (?, ?, ?, ?)',
            (run_id, 0, 0.25, '[12.5]'),
        )
        collector._conn.commit()

    assert collector.has_database()
    assert collector.current_batch()['id'] == batch_id
    assert collector.current_run()['id'] == run_id
    assert collector.get_run_header(run_id) == ['Time [s]', 'U1_tRMS [V]@AC']
    assert collector.get_run_rows(run_id) == [(0.25, [12.5])]

    output = tmp_path / 'export.csv'
    assert collector.export_run_to_csv(run_id, str(output)) == str(output)
    collector.finish_run()
    legacy_output = tmp_path / 'legacy_export.csv'
    assert collector.export_to_csv(str(legacy_output)) == str(legacy_output)
    with open(output, encoding='utf-8-sig', newline='') as source:
        rows = list(csv.reader(source))
    assert rows == [['Time [s]', 'U1_tRMS [V]@AC'], ['0.2500', '12.5000']]


def test_csv_export_respects_decimal_places(runtime, tmp_path):
    _controller, collector = runtime
    collector.begin_batch()
    run_id = collector.begin_run()
    with collector._db_lock:
        collector._conn.execute(
            'INSERT INTO de_data (run_id, seq, time, channel_values) VALUES (?, ?, ?, ?)',
            (run_id, 0, 0.25, '[12.5]'),
        )
        collector._conn.commit()

    collector.set_csv_decimal_places(2)
    output = tmp_path / 'export_2dp.csv'
    assert collector.export_run_to_csv(run_id, str(output)) == str(output)
    with open(output, encoding='utf-8-sig', newline='') as source:
        rows = list(csv.reader(source))
    assert rows == [['Time [s]', 'U1_tRMS [V]@AC'], ['0.2500', '12.50']]

    collector.set_csv_decimal_places(0)
    output0 = tmp_path / 'export_0dp.csv'
    assert collector.export_run_to_csv(run_id, str(output0)) == str(output0)
    with open(output0, encoding='utf-8-sig', newline='') as source:
        rows0 = list(csv.reader(source))
    assert rows0 == [['Time [s]', 'U1_tRMS [V]@AC'], ['0.2500', '12']]

    assert collector.set_csv_decimal_places(99) == 6
    assert collector.set_csv_decimal_places(-1) == 0
    collector.prepare(['U1_tRMS'], '100', 'flicker', '', decimal_places=2)
    assert collector._csv_decimal_places == 2


def test_save_load_commands_raw_row_round_trip_and_replace(runtime):
    """Persist every one of the executor's ten columns without coercion or duplication."""
    _controller, collector = runtime
    run_id = collector.begin_run()
    original = [
        ['AC', 'write', 'VOLT 230', '', 0, False, None, '第七列', 17, '尾列'],
        ['DEWETRON', 'write', ':ACQUISITION:START', '元数据', 2,
         True, None, '触发', 0.25, 31],
        ['AC', 'wait', '', '', '', '', '', '', '', 42],
    ]

    collector.save_commands(original)
    assert collector.load_commands(run_id) == original
    with collector._db_lock:
        first_count = collector._conn.execute(
            'SELECT COUNT(*) FROM de_commands WHERE run_id = ?', (run_id,)
        ).fetchone()[0]
        raw_rows = collector._conn.execute(
            'SELECT raw_row FROM de_commands WHERE run_id = ? ORDER BY seq', (run_id,)
        ).fetchall()
    assert first_count == len(original)
    assert all(raw_row[0] for raw_row in raw_rows)

    replacement = [
        ['DC4', 'query', 'MEAS?', '一', '二', '三', '四', '五', '六', '七'],
    ]
    collector.save_commands(replacement)
    assert collector.load_commands(run_id) == replacement
    with collector._db_lock:
        rows = collector._conn.execute(
            'SELECT seq, device FROM de_commands WHERE run_id = ? ORDER BY seq',
            (run_id,),
        ).fetchall()
    assert rows == [(1, 'DC4')]


def test_viewer_filters_latest_batch_and_uses_public_api(qapp):
    class PublicCollector:
        def __init__(self):
            self.filter_calls = []

        def has_database(self):
            return True

        def current_batch(self):
            return {'id': 1, 'batch_uid': 'harmonic_current', 'test_type': 'harmonic'}

        def list_batches(self, test_type=None):
            self.filter_calls.append(test_type)
            return [(2, 'flicker_latest', 'flicker', 1, 'now', None)]

        def get_batch_runs(self, batch_id):
            assert batch_id == 2
            return [(7, 1, 'now', None, 1)]

        def get_run_header(self, run_id):
            assert run_id == 7
            return ['Time [s]', 'U1']

        def get_run_rows(self, run_id):
            assert run_id == 7
            return [(0.1, [230.0])]

        def export_run_to_csv(self, run_id, path):
            return path

    collector = PublicCollector()
    viewer = DialogDEWETRONDataViewer(collector, parent=None, test_type='flicker')
    viewer._refresh_batch_info()
    assert collector.filter_calls == ['flicker']
    assert viewer._current_batch_id == 2
    assert viewer._lbl_batch.text() == '批次: flicker_latest'
    assert viewer._table.rowCount() == 1
    viewer.close()


def test_database_migration_adds_raw_row_to_preexisting_commands_schema(tmp_path):
    db_path = tmp_path / 'legacy_commands.sqlite'
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE de_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                seq INTEGER NOT NULL,
                device TEXT NOT NULL,
                operation TEXT NOT NULL,
                command TEXT NOT NULL,
                param1 TEXT, param2 TEXT, param3 TEXT, param4 TEXT,
                param5 TEXT, param6 TEXT, param7 TEXT,
                wait_time INTEGER DEFAULT 0,
                executed INTEGER DEFAULT 0,
                execute_time TEXT,
                execute_result TEXT
            );
            INSERT INTO de_commands (
                run_id, seq, device, operation, command, param1, wait_time
            ) VALUES (7, 1, 'AC', 'write', 'VOLT 230', 'keep-me', 12);
            """
        )

    assert init_database(str(db_path))
    with sqlite3.connect(db_path) as conn:
        columns = {row[1] for row in conn.execute('PRAGMA table_info(de_commands)')}
        preserved = conn.execute(
            'SELECT run_id, seq, device, command, param1, wait_time, raw_row '
            'FROM de_commands WHERE id = 1'
        ).fetchone()

    assert 'raw_row' in columns
    assert preserved == (7, 1, 'AC', 'VOLT 230', 'keep-me', 12, None)


def test_non_destructive_migration_adds_missing_columns(tmp_path):
    db_path = tmp_path / 'legacy.sqlite'
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE de_test_batch (
                id INTEGER PRIMARY KEY, batch_uid TEXT UNIQUE NOT NULL,
                test_type TEXT NOT NULL, total_versions INTEGER DEFAULT 0,
                start_time TEXT, end_time TEXT
            );
            CREATE TABLE de_test_runs (
                id INTEGER PRIMARY KEY, batch_id INTEGER NOT NULL,
                version INTEGER NOT NULL, start_time TEXT, end_time TEXT,
                UNIQUE(batch_id, version)
            );
            INSERT INTO de_test_batch (id, batch_uid, test_type) VALUES (1, 'keep', 'legacy');
            """
        )

    collector = DewetronDataCollector(None, FakeLogger(), str(db_path))
    assert collector._connect_database()
    columns = {
        row[1] for row in collector._conn.execute('PRAGMA table_info(de_test_runs)')
    }
    assert {'total_rows', 'csv_header'} <= columns
    assert collector._conn.execute(
        'SELECT batch_uid FROM de_test_batch WHERE id = 1'
    ).fetchone()[0] == 'keep'
    assert collector._conn.execute('PRAGMA busy_timeout').fetchone()[0] == 5000
    collector.stop()


def test_parse_value_strips_scpi_prefix_not_timestamp_space(tmp_path):
    collector = DewetronDataCollector(
        FakeController(), FakeLogger(), str(tmp_path / 'parse.sqlite')
    )
    assert collector._parse_value(
        ':NUM:NORM:VALue? "2026-09-21 14:17:38",230.0,10.5,7000.0'
    ) == [230.0, 10.5, 7000.0]
    assert collector._parse_value('"14:17:38.1",1.0,2.0') == [1.0, 2.0]
    collector.stop()


def test_align_numeric_row_truncates_overflow(tmp_path):
    controller = FakeController(channels=['U1_tRMS@AC', 'I1_tRMS@AC'])
    collector = DewetronDataCollector(
        controller, FakeLogger(), str(tmp_path / 'align.sqlite')
    )
    assert collector.prepare(
        ['U1_tRMS', 'I1_tRMS'], '100', 'flicker', str(tmp_path / 'a.csv')
    ).success
    assert collector._fields == ['U1_tRMS@AC', 'I1_tRMS@AC']
    # 模拟设备多返回谐波桶，应对齐到 2 列
    aligned = collector._align_numeric_row([230.0, 10.0, 0.1, 0.2, 0.3])
    assert aligned == [230.0, 10.0]
    padded = collector._align_numeric_row([230.0])
    assert len(padded) == 2 and padded[0] == 230.0
    assert padded[1] != padded[1]  # NaN
    collector.stop()


def test_export_truncates_values_to_header(tmp_path):
    controller = FakeController(channels=['U1_tRMS@AC'])
    collector = DewetronDataCollector(
        controller, FakeLogger(), str(tmp_path / 'ex.sqlite')
    )
    assert collector.prepare(
        ['U1_tRMS'], '100', 'flicker', str(tmp_path / 'e.csv')
    ).success
    run_id = collector.begin_run()
    with collector._db_lock:
        collector._conn.execute(
            'INSERT INTO de_data (run_id, seq, time, channel_values) VALUES (?, ?, ?, ?)',
            (run_id, 0, 1.0, '[12.5, 99.0, 88.0]'),
        )
        collector._conn.commit()
    out = tmp_path / 'trunc.csv'
    assert collector.export_run_to_csv(run_id, str(out))
    with open(out, encoding='utf-8-sig', newline='') as source:
        rows = list(csv.reader(source))
    assert rows[0] == ['Time [s]', 'U1_tRMS [V]@AC']
    assert rows[1] == ['1.0000', '12.5000000']
    collector.stop()


def test_scpi_poll_follows_configured_rate():
    from devices.dewetron_data_collector import scpi_poll_interval_s

    assert scpi_poll_interval_s(200) == pytest.approx(0.2)
    assert scpi_poll_interval_s(100) == pytest.approx(0.1)
    assert scpi_poll_interval_s(2000) == pytest.approx(2.0)
    assert scpi_poll_interval_s(0) == pytest.approx(0.1)


def test_channel_values_json_roundtrip_with_nan():
    """历史 bug：json.dumps(nan) 无法被 json.loads 读回 → 导出空 CSV。"""
    import math

    from devices.dewetron_data_collector import dumps_channel_values, loads_channel_values

    raw = dumps_channel_values([230.1, float("nan"), 10.5])
    assert "NaN" not in raw
    assert "null" in raw
    got = loads_channel_values(raw)
    assert got[0] == pytest.approx(230.1)
    assert math.isnan(got[1])
    assert got[2] == pytest.approx(10.5)

    # 兼容库里已有的非标准 NaN 文本
    legacy = loads_channel_values("[1.0, NaN, 2.0]")
    assert legacy[0] == pytest.approx(1.0)
    assert math.isnan(legacy[1])
    assert legacy[2] == pytest.approx(2.0)


def test_export_keeps_rows_that_contain_nan(tmp_path):
    import math

    controller = FakeController(channels=["U1_tRMS@AC", "I1_tRMS@AC"])
    collector = DewetronDataCollector(
        controller, FakeLogger(), str(tmp_path / "nan_export.sqlite")
    )
    assert collector.prepare(
        ["U1_tRMS", "I1_tRMS"], "100", "flicker", str(tmp_path / "n.csv")
    ).success
    run_id = collector.begin_run()
    with collector._db_lock:
        from devices.dewetron_data_collector import dumps_channel_values

        collector._conn.execute(
            "INSERT INTO de_data (run_id, seq, time, channel_values) VALUES (?, ?, ?, ?)",
            (run_id, 0, 0.2, dumps_channel_values([230.0, float("nan")])),
        )
        # 模拟旧版写入
        collector._conn.execute(
            "INSERT INTO de_data (run_id, seq, time, channel_values) VALUES (?, ?, ?, ?)",
            (run_id, 1, 0.4, "[231.0, NaN]"),
        )
        collector._conn.commit()
    out = tmp_path / "with_nan.csv"
    assert collector.export_run_to_csv(run_id, str(out))
    with open(out, encoding="utf-8-sig", newline="") as source:
        rows = list(csv.reader(source))
    assert len(rows) == 3  # header + 2 data
    assert rows[1][1] == "230.0000000"
    assert rows[2][1] == "231.0000000"
    collector.stop()
