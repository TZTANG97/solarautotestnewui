# 增量迁移约定（Boy Scout）

本仓库不做一次性目录大重构。**修 BUG / 接试验 / 改逻辑时，只整理本次真正改到的代码。**

完整落点见 [`project_layout.md`](project_layout.md)。

## 必须做

1. 本次 diff 里动到的 `xxxSend` / `xxxAppend`：抽到 `sends/<project>_send.py`（或已有 `utils/*_commands.py`），`SCPITestWave.py` 只保留薄包装。  
2. 本次动到的试验专用纯函数：放到 `utils/<topic>.py`。  
3. 本次动到的共用 UI 控件：放到 `components/`。  
4. 根目录新增的一次性脚本：放 `code_example/patches|audits|smoke|ops/` 或 `scripts/scratch/`，禁止再往根目录加 `test_*.py` / `_tmp*`。  
5. 迁移后删掉旧实现路径，或主文件只留一行 re-export；**禁止长期双写两套逻辑**。

## 禁止做

- 为了“顺手干净”去改未触及的已绿试验（除非用户点名）。  
- 同一次任务里同时搬全部 `Dialog_*.py` + 拆执行器 + 改设备协议。  
- 只改文件位置、不改行为时，仍须保证 `uv run python SCPITestWave.py` 能启动。

## 目标落点（碰到再迁）

| 碰到的代码 | 迁往 |
|---|---|
| `xxxSend` / `xxxAppend` | `sends/<name>_send.py` |
| 录波/文件名/命令构造纯函数 | `utils/` |
| WT/录波 UI 行 | `components/` |
| 设备读写 | `devices/` |
| Dialog UI | `dialogs/`（调用方 `from dialogs.Dialog_xxx import …`；根目录不再留兼容壳） |
| 正式测试 | `tests/` |
| 一次性补丁/台架冒烟 | `code_example/` 分筐子目录 |
