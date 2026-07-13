"""测试 DEWETRON DSTREAM 高速数据流采集。

复用 DewetronController 的现有 SCPI 连接，DSTREAM 数据流通过独立 socket 接收。

用法:
    uv run python test_dewetron_dstream.py <IP地址> [数据流端口]

示例:
    uv run python test_dewetron_dstream.py 192.168.40.25
"""

import sys
import time
import logging
import pyvisa

from devices.dewetron_controller import DewetronController


class QuickLogger:
    """简易 logger，兼容 Controller 的 logger.info() 调用。"""
    def __init__(self):
        self._log = logging.getLogger("dstream_test")
        self._log.setLevel(logging.DEBUG)
        if not self._log.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt='%H:%M:%S'))
            self._log.addHandler(h)

    def info(self, msg):
        self._log.info(msg)

    def debug(self, msg):
        self._log.debug(msg)


_pkt_count = 0
_MAX_PKT = 10

def on_stream_data(data_bytes, channel_names, floats):
    """数据流回调：打印收到的数据。"""
    global _pkt_count
    _pkt_count += 1
    num_floats = len(floats)
    print(f"\n[DSTREAM] 第 {_pkt_count}/{_MAX_PKT} 包: {len(data_bytes)} 字节, {num_floats} 个 float32")

    if not channel_names or num_floats == 0:
        return

    ch_count = len(channel_names)
    samples_per_ch = num_floats // ch_count
    remainder = num_floats % ch_count

    if remainder:
        print(f"  注意: {num_floats} 个 float 不能被 {ch_count} 通道整除 (余 {remainder})")

    for ch_idx, ch_name in enumerate(channel_names):
        start = ch_idx * samples_per_ch
        end = start + samples_per_ch
        ch_data = floats[start:end]
        if len(ch_data) > 0:
            avg = sum(ch_data) / len(ch_data)
            mn = min(ch_data)
            mx = max(ch_data)
            print(f"  {ch_name}: {samples_per_ch}点, 均值={avg:.4f}, 最小={mn:.4f}, 最大={mx:.4f}")
            preview = ch_data[:6]
            print(f"    前6点: {[f'{v:.4f}' for v in preview]}")

    if _pkt_count >= _MAX_PKT:
        print(f"\n[DSTREAM] 已收到 {_MAX_PKT} 包，自动停止")
        raise KeyboardInterrupt


def main():
    if len(sys.argv) < 2:
        print("用法: uv run python test_dewetron_dstream.py <IP地址> [数据流端口]")
        sys.exit(1)

    ip = sys.argv[1]
    stream_port = int(sys.argv[2]) if len(sys.argv) > 2 else 10003

    print(f"=== DEWETRON DSTREAM 测试 ===")
    print(f"设备 IP: {ip}, 数据流端口: {stream_port}")
    print()

    # 1. 创建 Controller 并连接（复用主程序的连接方式）
    rm = pyvisa.ResourceManager()
    ctrl = DewetronController(
        logger=QuickLogger(),
        show_message=lambda msg, ui=None: print(f"[MSG] {msg}"),
        now_to_datenow=lambda: time.strftime('%H:%M:%S '),
        rm=rm,
        ui=None
    )

    print("1. 连接 DEWETRON...")
    _, status = ctrl.connect(ip)
    if status != '1':
        print("   连接失败！请确保设备可达且无其他连接")
        sys.exit(1)
    print("   连接成功")

    # 2. 查询设备信息
    print("\n2. 查询设备信息...")
    idn = ctrl._query("*IDN?")
    print(f"   *IDN? = {idn}")

    # 3. 查询通道
    print("\n3. 查询通道...")
    raw = ctrl._query(":CHANNELLIST:NAMES?", timeout_ms=30000)
    if raw:
        import re
        channels = [m.group(2) for m in re.finditer(r'"(\d+)","([^"]+)"', raw)]
        ai_channels = [c for c in channels if c.startswith('AI')]
        print(f"   AI 通道: {ai_channels}")

    # 4. 选择电力组通道
    power_group_names = ['AI 1/U1', 'AI 1/I1', 'AI 1/U2', 'AI 1/I2', 'AI 1/U3', 'AI 1/I3']
    target = [c for c in power_group_names if c in ai_channels]
    if len(target) < 2:
        target = ai_channels[:4]
    print(f"\n4. 使用通道: {target}")

    # 5. 配置 DSTREAM
    print("\n5. 配置 DSTREAM...")
    if not ctrl.dstream_configure(target, port=stream_port):
        print("   配置失败")
        ctrl.disconnect(lambda h: None)
        return

    # 6. 初始化
    state = ctrl.dstream_init()
    print(f"   初始化状态: {state}")

    # 7. 启动采集
    acq_state = ctrl._query(":ACQUISITION:STATE?")
    if acq_state != 'Started':
        print("\n6. 启动采集...")
        ctrl._send(":ACQUISITION:START", "启动采集", "ACQUISITION START")
        time.sleep(2)
        acq_state = ctrl._query(":ACQUISITION:STATE?")
        print(f"   采集状态: {acq_state}")

    # 8. 启动数据流
    print("\n7. 启动数据流...")
    state = ctrl.dstream_start()
    print(f"   DSTREAM 状态: {state}")

    # 9. 连接数据流端口
    print("\n8. 连接数据流端口...")
    if not ctrl.dstream_connect_data_port():
        print("   连接失败，退出")
        ctrl.disconnect(lambda h: None)
        return

    # 10. 启动后台接收
    print("\n9. 启动数据流接收...")
    ctrl.dstream_start_receiving(callback=on_stream_data)

    print("\n   按 Ctrl+C 停止...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n   用户中断")

    # 11. 清理
    print("\n10. 清理...")
    ctrl.dstream_stop_receiving()
    ctrl.dstream_cleanup()
    print("   完成")


if __name__ == '__main__':
    main()
