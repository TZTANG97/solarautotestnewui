"""测试 DEWETRON :NUMERIC:NORMAL: 读取测量值。

严格按 :RATE 间隔采集，导出 CSV。

用法:
    uv run python test_dewetron_numeric.py <IP地址> [采集次数] [RATE毫秒]

示例:
    uv run python test_dewetron_numeric.py 192.168.40.25          # 默认 50ms, 20次
    uv run python test_dewetron_numeric.py 192.168.40.25 50 100   # 100ms间隔, 50次
"""

import sys
import time
import csv
import pyvisa

from devices.dewetron_controller import DewetronController

# CSV 表头（带单位）
CSV_HEADER = [
    'Time [s]',
    'U1_tRMS [V]', 'U2_tRMS [V]', 'U3_tRMS [V]',
    'I1_tRMS [A]', 'I2_tRMS [A]', 'I3_tRMS [A]',
    'P1_t [W]', 'P2_t [W]', 'P3_t [W]',
]

# 目标通道（不带 _AVG）
TARGET_CHANNELS = [
    'ABS-TIME',
    'U1_tRMS@POWER/0', 'U2_tRMS@POWER/0', 'U3_tRMS@POWER/0',
    'I1_tRMS@POWER/0', 'I2_tRMS@POWER/0', 'I3_tRMS@POWER/0',
    'P1_t@POWER/0',    'P2_t@POWER/0',    'P3_t@POWER/0',
]


class QuickLogger:
    def info(self, msg):
        pass


def parse_value(raw_val):
    """解析 :NUM:NORM:VAL? 返回值。"""
    clean = raw_val
    sp = clean.find(' ')
    if sp >= 0:
        clean = clean[sp+1:].strip()
    values = [v.strip() for v in clean.split(',')]
    nums = []
    for v in values[1:]:  # 跳过 ABS-TIME
        try:
            nums.append(float(v))
        except ValueError:
            nums.append(0.0)
    return nums


def main():
    if len(sys.argv) < 2:
        print("用法: uv run python test_dewetron_numeric.py <IP地址> [采集次数] [RATE毫秒]")
        sys.exit(1)

    ip = sys.argv[1]
    max_read = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    rate_ms = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    interval_s = rate_ms / 1000.0

    print(f"=== DEWETRON NUMERIC 严格间隔采集 ===")
    print(f"设备 IP: {ip}, 采集次数: {max_read}, 目标间隔: {rate_ms}ms")
    print()

    # 连接
    rm = pyvisa.ResourceManager()
    ctrl = DewetronController(
        logger=QuickLogger(),
        show_message=lambda msg, ui=None: None,
        now_to_datenow=lambda: time.strftime('%H:%M:%S '),
        rm=rm, ui=None
    )

    print("1. 连接 DEWETRON...")
    _, status = ctrl.connect(ip)
    if status != '1':
        print("   连接失败！")
        sys.exit(1)
    idn = ctrl._query("*IDN?")
    print(f"   连接成功: {idn}")

    # 配置 NUMERIC
    print("\n2. 配置 NUMERIC...")
    ctrl._send(":NUM:NORM:CLEar ALL", "清除旧配置", "NUM CLEAR")
    items_str = ','.join(f'"{c}"' for c in TARGET_CHANNELS)
    ctrl._send(f":NUM:NORM:ITEMs {items_str}", "设置输出通道", "NUM ITEMS")
    ctrl._send(f":NUM:NORM:NUMber {len(TARGET_CHANNELS)}", "设置传输数量", "NUM NUMBER")

    # 设置 RATE
    rate_cmd = f":RATE {rate_ms}ms"
    ctrl._send(rate_cmd, f"设置聚合时间 {rate_ms}ms", "RATE")
    rate_val = ctrl._query(":RATE?")
    print(f"   聚合时间确认: {rate_val}")

    # 启动采集
    acq_state = ctrl._query(":ACQUISITION:STATE?")
    if acq_state != 'Started':
        print("\n3. 启动采集...")
        ctrl._send(":ACQUISITION:START", "启动采集", "ACQUISITION START")
        time.sleep(1)
    print(f"   采集状态: {ctrl._query(':ACQUISITION:STATE?')}")

    # ── 严格间隔采集 ──
    print(f"\n4. 开始采集 (间隔 {rate_ms}ms, 共 {max_read} 次)...")
    print()

    rows = []
    actual_intervals = []
    t_start = time.time()  # 精确起点

    for i in range(max_read):
        # 发送 query（blocking，耗时约15-20ms）
        raw_val = ctrl._query(":NUM:NORM:VALue?", timeout_ms=5000)
        t_query = time.time()  # query 返回的时刻

        if raw_val:
            nums = parse_value(raw_val)
            while len(nums) < 9:
                nums.append(0.0)

            # 计算实际经过时间
            elapsed = t_query - t_start
            actual_intervals.append(elapsed)

            # 打印
            print(f"{i+1:>4} | {elapsed:>7.4f}s | "
                  f"{nums[0]:>10.4f} {nums[1]:>10.4f} {nums[2]:>10.4f} | "
                  f"{nums[3]:>10.6f} {nums[4]:>10.6f} {nums[5]:>10.6f} | "
                  f"{nums[6]:>10.4f} {nums[7]:>10.4f} {nums[8]:>10.4f}")

            row = [f"{elapsed:.4f}"] + [f"{v:.7f}" for v in nums[:9]]
            rows.append(row)
        else:
            print(f"{i+1:>4} | 读取失败")

        # 精确 sleep 到下一个目标时间
        if i < max_read - 1:
            next_target = t_start + (i + 1) * interval_s
            sleep_time = next_target - time.time()
            if sleep_time > 0.001:
                time.sleep(sleep_time)
            # 如果 query 耗时超过间隔，不 sleep，直接进入下一次

    # 统计
    if len(actual_intervals) > 1:
        diffs = [actual_intervals[j] - actual_intervals[j-1] for j in range(1, len(actual_intervals))]
        avg_ms = (sum(diffs) / len(diffs)) * 1000
        min_ms = min(diffs) * 1000
        max_ms = max(diffs) * 1000
        total = actual_intervals[-1]
        print()
        print(f"5. 采集间隔统计:")
        print(f"   目标: {rate_ms}ms | 实际平均: {avg_ms:.1f}ms | 最小: {min_ms:.1f}ms | 最大: {max_ms:.1f}ms")
        print(f"   总耗时: {total:.3f}s, 共 {max_read} 个数据点")

    # 导出 CSV
    csv_file = f"dewetron_numeric_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)
            writer.writerows(rows)
        print(f"\n6. 已导出 CSV: {csv_file}")
    except Exception as e:
        print(f"\n6. CSV 导出失败: {e}")

    ctrl.disconnect(lambda h: None)
    print("\n完成")


if __name__ == '__main__':
    main()
