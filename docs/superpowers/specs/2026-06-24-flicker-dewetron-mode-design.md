# 闪变对话框 — 德威创模式子页面

## 概述

在现有电压闪变项目配置对话框 (`Dialog_thaiguodianyashanbian.py`) 中，新增"德威创模式"子页面。该页面与现有 5 步 WT3000 流程并存，通过工具栏切换，**不影响现有 WT3000 闪变逻辑**。

## 设计原则

- 现有 WT3000 闪变 5 步流程完全不动
- 德威创模式是新增的独立页面，通过切换显示
- 复用 DEWETRON 设置页的"最大刷新率"下拉框选项
- 所有 XML 配置修改走同一个 `modify_xml()` 入口

## UI 布局

### 切换机制

在顶部工具栏（步骤指示器左侧）添加一个切换按钮组：

```
[测试追加] [读取设定] [保存设定] | 项目设置 0 [重置] | ◉ WT3000闪变  ○ 德威创模式 | ① AC/DC 电源 ...
```

- 使用两个 `QRadioButton`，包裹在 `QButtonGroup` 中
- 默认选中"WT3000闪变"
- 切换时联动 `stackedWidget` 显示对应页面组：
  - WT3000闪变：显示原有 5 步（step1~step5）
  - 德威创模式：显示 DEWETRON 闪变配置页（1 页）

### 德威创模式页面内容

单页布局，包含以下配置项：

```
┌─────────────────────────────────────────────────────┐
│  DEWETRON 闪变测量配置                                │
│                                                       │
│  ☑ 闪变计算依照IEC61000-4-15: 2011                    │
│                                                       │
│  加权类型:  [自动检测 ▼]                               │
│             自动检测                                   │
│             230V / 50Hz                               │
│             230V / 60Hz                               │
│             120V / 50Hz                               │
│             120V / 60Hz                               │
│                                                       │
│  最大刷新率:  [Default ▼]    (复用 DEWETRON 设置)       │
│                                                       │
│  标称电压:    [230] V                                  │
│  输入电压值:  [230] V                                  │
│                                                       │
│  短时闪变计算时间:  [10] 分钟                           │
│  长时闪变计算时间:  [120] 分钟                          │
│  短路视在功率:      [50] MVA                           │
│                                                       │
│  ☑ 打开滚动计算                                        │
└─────────────────────────────────────────────────────┘
```

### 样式

与现有步骤页面保持一致：
- `QGroupBox` 带 `border: 1px solid #e2e8f0; border-radius: 6px`
- `QCheckBox` 默认勾选
- `QComboBox` 固定宽度 150px
- `QTextEdit` 输入框 `setFixedSize(100, 31)`
- 单位标签 `QLabel` 紧跟输入框右侧

## 涉及文件

| 文件 | 改动 |
|------|------|
| `Dialog_thaiguodianyashanbian.py` | 新增 `_build_dewetron_page()` 方法，添加 RadioButton 切换逻辑 |
| `SCPITestWave.py` | `thaidianyashanbianSend()` 中根据模式选择读取 WT3000 或 DEWETRON 配置 |
| `utils/Open_Save_ThaiGuoDianYaShanBian.py` | 保存/读取时处理 DEWETRON 模式配置项 |

## 实现要点

### 1. Dialog 改动 (`Dialog_thaiguodianyashanbian.py`)

- 在 `topBar` 步骤指示器前插入两个 `QRadioButton` + `QButtonGroup`
- `self._radio_group` 保持引用（防止 GC 回收信号）
- 新增 `_build_dewetron_page()` 构建 DEWETRON 配置页
- 切换逻辑：
  - WT3000 模式：`stackedWidget` 显示 step1~step5，步骤指示器可见
  - DEWETRON 模式：`stackedWidget` 只显示 DEWETRON 页，步骤指示器隐藏
- `self._mode = 'wt3000' | 'dewetron'` 记录当前模式

### 2. SCPITestWave.py 改动

- `thaidianyashanbianSend()` 中根据 `uiThaiGuoDianYaShanBian._mode` 判断：
  - `'wt3000'`：走现有 WT3000 逻辑（不变）
  - `'dewetron'`：读取 DEWETRON 闪变配置，生成对应命令

### 3. 保存/读取改动

- DEWETRON 模式的配置保存到 CSV 时，增加对应字段
- 读取时根据模式加载对应字段

## 不改动的部分

- 现有 5 步 WT3000 闪变流程的所有逻辑
- `_connect_step_toggles()` 中的联动逻辑
- `thaidianyashanbianSend()` 中的 WT3000 命令生成
- 其他测试项目的对话框
