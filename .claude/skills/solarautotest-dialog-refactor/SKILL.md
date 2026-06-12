---
name: solarautotest-dialog-refactor
description: SolarAutoTest 项目测试对话框重构专用技能。用于将剩余测试项目接入按钮逻辑、DC联动、功率分析仪配置内嵌。包含完整修改流程、已踩坑点、自测清单。当用户要求接入新测试项目、修复测试项目bug、或重构测试对话框时使用此技能。
---

# SolarAutoTest 测试对话框重构技能

本技能用于将 SolarAutoTest 项目中的测试对话框逐个接入标准逻辑。每个项目必须严格按照以下流程执行，不可跳步。

## 前置条件

- 闪变测试（fluctuation）是标准参考，只读参考，不允许修改
- 已完成项目：闪变、谐波电流、过载能力测试
- 所有改动必须在 `SolarAutoTestEnv` conda 环境下测试
- 运行命令：`conda activate SolarAutoTestEnv && python SCPITestWave.py`

## 项目信息收集

在开始修改前，必须收集以下信息：

### 1. 确认项目名称

从以下位置获取项目的中英文名称：
- `SCPITestWave.py` 中搜索 ` comboBox_PS ` 获取所有项目中文名
- 对应的 Dialog 文件名获取英文名（如 `Dialog_thaioverloads.py` → overloads）

### 2. 确认 Dialog 文件结构

读取对应的 `Dialog_thaiXxx.py` 文件，确认：
- 是否有 step2（功率分析仪配置）→ 需要 radio+stackedWidget 内嵌
- step3/step4/step5/step7 中是否有 DC 复选框 → 需要联动 step1
- 关机步骤是哪个（通常是最后一个步骤）
- 步骤条数量（决定 stackedWidget 页数）
- **是否有多个相同结构的步骤**（如谐波电流的 16 个谐波卡片）→ 可能需要合并到一个页面

### 3. 确认 Send 函数

在 `SCPITestWave.py` 中搜索 `xxxSend()` 函数，确认：
- 函数名（如 `thaioverloadsSend`）
- 已有的 global 声明
- 是否有 DC 块（搜索 `checkBox_S*_DC`）
- 是否有 WT 配置读取（搜索 `WT3000E_params_config` 或 `wt_config`）

### 4. 确认已有信号连接

搜索 `_safe_click(uiXxx,` 确认当前已有的按钮连接。

---

## 修改流程（按顺序执行，不可跳步）

### 阶段一：SCPITestWave.py — 按钮逻辑（5处改动）

#### 改动1：新增 Append 函数

在 `xxxSend()` 函数定义**之前**添加：

```python
def xxxAppend():
    global strAddTestFlag, xxx_append_count
    if 'xxx_append_count' not in globals():
        xxx_append_count = 0
    strAddTestFlag = "0" if xxx_append_count == 0 else "1"
    mode = "覆盖" if xxx_append_count == 0 else "追加"
    ui.textEdit_ReturnMessage.append(f"[项目中文名] 第{xxx_append_count + 1}次{mode}模式，开始生成命令...")
    xxxSend()
```

**注意**：`xxxSend()` 必须在 `xxxAppend()` 之后定义，否则会报 `NameError`。如果 `xxxSend()` 在文件中位于 `xxxAppend()` 之前，需要将 `xxxAppend()` 放在 `xxxSend()` 之后。

#### 改动2：Send 函数末尾加计数递增

在 `xxxSend()` 函数末尾、`dialog_windowXxx.close()` 之前添加：

```python
# 计数递增
if 'xxx_append_count' not in globals():
    xxx_append_count = 0
xxx_append_count += 1
uiXxx.label_append_count.setText(str(xxx_append_count))
_sync_start_end_buttons()
ui.textEdit_ReturnMessage.append(f"[项目中文名] 追加完成，当前计数: {xxx_append_count}，开始/结束试验按钮已启用")
```

#### 改动3：信号连接区域

在 `_safe_click` 批量连接处添加：

```python
# 追加测试
_safe_click(uiXxx, "pushButton_TestAppend", xxxAppend)

# 重置计数
def reset_xxx_count():
    global xxx_append_count
    xxx_append_count = 0
    uiXxx.label_append_count.setText("0")
    _sync_start_end_buttons()
    ui.textEdit_ReturnMessage.append("[项目中文名] 计数器已重置为0")
_safe_click(uiXxx, "pushButton_ResetCount", reset_xxx_count)
```

#### 改动4：同步按钮状态函数

在 `_sync_start_end_buttons()` 函数中添加分支：

```python
elif current == '项目中文名':
    count = xxx_append_count
```

#### 改动5：对话框显示函数

在 `chooseDetailDialog()` 和 `addtestDialog()` 中添加分支：

```python
elif currentSecond == '项目中文名':
    uiXxx.label_append_count.setText(str(xxx_append_count))
    _sync_start_end_buttons()
    dialog_windowXxx.show()
```

**同时**在函数顶部的 global 声明中加入 `xxx_append_count`，并在函数体开头初始化：

```python
global xxx_append_count
if 'xxx_append_count' not in globals():
    xxx_append_count = 0
```

---

### 阶段二：SCPITestWave.py — _reset_current_project_count()

在 `_reset_current_project_count()` 函数中添加分支：

```python
elif current == '项目中文名':
    xxx_append_count = 0
    uiXxx.label_append_count.setText("0")
```

---

### 阶段三：SCPITestWave.py — DC 命令联动（坑11）

**这是最容易遗漏的步骤，必须逐一检查。**

搜索 `xxxSend()` 函数中所有 `checkBox_S*_DC`，确保每个 DC 块都同时检查 step1 DC 复选框。

**修改模式**：

```python
# 错误（只检查 step 步骤复选框）：
if uiXxx.checkBox_S3_DC1.isChecked():
    ...

# 正确（同时检查 step1 DC 复选框）：
if uiXxx.checkBox_S1_DC1.isChecked() and uiXxx.checkBox_S3_DC1.isChecked():
    ...
```

**检查范围**：
- step3 DC 块
- step4 DC 块（如果有）
- step5 DC 块
- step7 DC 块（如果有）
- 关机步骤 DC 块（通常是最后一个步骤）

**如何定位所有 DC 块**：
1. 在 `xxxSend()` 函数中搜索 `checkBox_S`
2. 找到所有 `if uiXxx.checkBox_S*_DC*.isChecked():` 行
3. 检查每个前面是否有 `checkBox_S1_DC` 的检查
4. 没有的补上

---

### 阶段四：Dialog 文件 — DC 联动（坑10）

#### 4.1 确认 step1 DC 复选框名称

读取 Dialog 文件，找到 step1 中的 DC 复选框，通常命名为：
- `self.checkBox_S1_DC1`
- `self.checkBox_S1_DC2`
- `self.checkBox_S1_DC3`
- `self.checkBox_S1_DC4`

#### 4.2 修改 step3/step4/step5/step7 的 DC 联动

在构建步骤的函数中（如 `_build_step3()` 或 `_build_step4()`），找到 DC 复选框的构建代码。

**添加联动逻辑**（以 step3 为例）：

```python
# 收集该步骤的 DC 复选框
s3_dc = [self.checkBox_S3_DC1, self.checkBox_S3_DC2,
         self.checkBox_S3_DC3, self.checkBox_S3_DC4]

# 收集 step1 DC 复选框
step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
             self.checkBox_S1_DC3, self.checkBox_S1_DC4]

def _update_s3_dc():
    step_on = self.checkBox_S3.isChecked()
    for i in range(4):
        should_enable = step_on and step1_dcs[i].isChecked()
        s3_dc[i].setEnabled(should_enable)
        s3_dc[i].setChecked(should_enable)  # 自动勾选

# 连接信号
self.checkBox_S3.toggled.connect(_update_s3_dc)
for s1dc in step1_dcs:
    s1dc.toggled.connect(_update_s3_dc)
_update_s3_dc()  # 初始化状态
```

**关键点**：
- `s3_dc[i].setChecked(should_enable)` — 当 step1 DC 勾选时自动勾选 step3 DC
- `s3_dc[i].setEnabled(should_enable)` — 当 step1 DC 未勾选时禁用 step3 DC
- 必须同时连接 step checkbox 和 step1 DC 的 toggled 信号
- 必须调用一次初始化

#### 4.3 关机步骤 DC 联动

关机步骤（通常是最后一个步骤，如 step5 或 step7）的 DC 复选框也必须联动 step1。

**模式与 step3 完全相同**，只是 DC 复选框名称不同（如 `checkBox_S5_DC1`~`DC4`）。

---

### 阶段四-B：步骤合并（如果用户要求合并相同步骤）

某些项目中，多个步骤的内容结构相同（如谐波电流的 step3 有 16 个谐波卡片，每个卡片结构完全一致）。用户可能要求将这些相同内容合并到一个步骤页面中，用 QStackedWidget 或 QTabWidget 切换。

**触发条件**：用户明确说"合并步骤"、"把 step3/4/5 合并到一个页面"、"像谐波一样处理"。

#### 合并模式（以谐波电流为参考）

谐波电流的 step3 有 16 个谐波测量卡片，原始设计是每个谐波一个独立步骤（step3~step18）。合并后：

1. **侧边栏步骤条**：只显示一个"谐波测量"步骤（step3）
2. **页面内容**：用 QStackedWidget 承载 16 个卡片，通过顶部 QComboBox 或 QTabBar 切换
3. **DC 联动**：所有卡片共享同一个 step1 DC 联动逻辑
4. **命令生成**：遍历所有卡片，为每个启用的卡片生成 DC 块

#### 实现步骤

**1. Dialog 文件重构**

在 `_build_step3()`（或对应步骤构建方法）中：

```python
def _build_step3(self):
    page = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(page)

    # 步骤启用复选框
    self.checkBox_S3 = self._make_checkbox("checkBox_S3", "谐波测量", parent=self)
    layout.addWidget(self.checkBox_S3)

    # QComboBox 选择具体谐波次数
    self.comboBox_S3_harmonic = QtWidgets.QComboBox()
    self.comboBox_S3_harmonic.addItems([f"第{i+1}次谐波" for i in range(16)])
    layout.addWidget(self.comboBox_S3_harmonic)

    # QStackedWidget 承载所有卡片
    self._harmonicStacked = QtWidgets.QStackedWidget()
    for i in range(16):
        card = self._build_harmonic_card(i)  # 构建单个卡片
        self._harmonicStacked.addWidget(card)
    layout.addWidget(self._harmonicStacked)

    # ComboBox 切换联动
    self.comboBox_S3_harmonic.currentIndexChanged.connect(
        self._harmonicStacked.setCurrentIndex
    )

    layout.addStretch()
    self.stackedWidget.addWidget(page)
```

**2. 单个卡片构建方法**

```python
def _build_harmonic_card(self, index):
    """构建第 index 次谐波的配置卡片"""
    card = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(card)

    # DC 复选框（每个卡片有自己的 DC 选择）
    dc_group = QtWidgets.QGroupBox(f"DC通道选择（第{index+1}次谐波）")
    dc_layout = QtWidgets.QGridLayout(dc_group)
    self._make_checkbox(f"checkBox_S3_DC1_{index}", "DC1", parent=card)
    self._make_checkbox(f"checkBox_S3_DC2_{index}", "DC2", parent=card)
    self._make_checkbox(f"checkBox_S3_DC3_{index}", "DC3", parent=card)
    self._make_checkbox(f"checkBox_S3_DC4_{index}", "DC4", parent=card)
    dc_layout.addWidget(card.checkBox_S3_DC1_{index}, 0, 0)
    dc_layout.addWidget(card.checkBox_S3_DC2_{index}, 0, 1)
    dc_layout.addWidget(card.checkBox_S3_DC3_{index}, 0, 2)
    dc_layout.addWidget(card.checkBox_S3_DC4_{index}, 0, 3)
    layout.addWidget(dc_group)

    # 其他配置控件...
    # 注意：objectName 必须包含 index 后缀，避免重名

    return card
```

**3. DC 联动（所有卡片共享）**

```python
def _connect_step3_dc_linkage(self):
    """连接 step1 DC 与所有谐波卡片的 DC 联动"""
    step1_dcs = [self.checkBox_S1_DC1, self.checkBox_S1_DC2,
                 self.checkBox_S1_DC3, self.checkBox_S1_DC4]

    def _update_all_harmonic_dc():
        step_on = self.checkBox_S3.isChecked()
        for i in range(16):  # 遍历所有卡片
            card_dcs = [
                getattr(self, f"checkBox_S3_DC1_{i}"),
                getattr(self, f"checkBox_S3_DC2_{i}"),
                getattr(self, f"checkBox_S3_DC3_{i}"),
                getattr(self, f"checkBox_S3_DC4_{i}"),
            ]
            for j in range(4):
                should_enable = step_on and step1_dcs[j].isChecked()
                card_dcs[j].setEnabled(should_enable)
                card_dcs[j].setChecked(should_enable)

    self.checkBox_S3.toggled.connect(_update_all_harmonic_dc)
    for s1dc in step1_dcs:
        s1dc.toggled.connect(_update_all_harmonic_dc)
    _update_all_harmonic_dc()  # 初始化
```

**4. SCPITestWave.py — 命令生成修改**

合并后，Send 函数需要遍历所有卡片生成命令：

```python
# 合并前（每个步骤独立）：
if uiXxx.checkBox_S3_DC1.isChecked():
    strArrayTest.append(["DC1", ...])

# 合并后（遍历所有卡片）：
for i in range(16):  # 遍历所有谐波卡片
    if uiXxx.checkBox_S3_DC1_{i}.isChecked() and uiXxx.checkBox_S1_DC1.isChecked():
        strArrayTest.append(["DC1", ...])
```

**5. Open_Save 修改**

保存/读取时需要遍历所有卡片的控件：

```python
# 保存：
for i in range(16):
    for dc in ['DC1', 'DC2', 'DC3', 'DC4']:
        cb = getattr(uiXxx, f"checkBox_S3_{dc}_{i}")
        row.append(str(int(cb.isChecked())))

# 读取：
for i in range(16):
    for j, dc in enumerate(['DC1', 'DC2', 'DC3', 'DC4']):
        cb = getattr(uiXxx, f"checkBox_S3_{dc}_{i}")
        cb.setChecked(bool(int(data[index + j])))
```

#### 合并注意事项

1. **objectName 必须唯一**：每个卡片的控件 objectName 必须包含 index 后缀（如 `checkBox_S3_DC1_0`、`checkBox_S3_DC1_1`），否则 `_make_checkbox` 的 `setattr` 会覆盖同名属性
2. **DC 联动必须遍历所有卡片**：不能只联动当前显示的卡片，因为用户可能切换卡片
3. **命令生成必须遍历所有卡片**：即使某些卡片未显示，只要启用了就要生成命令
4. **CSV 格式变化**：合并后 CSV 行结构改变，需要在文件开头写入版本标识（如 `ThaiHarmonicV2`），读取时根据版本解析
5. **_PageWidgetFinder 不适用**：合并后的卡片不是 stacked page，而是 stacked widget 内的 widget，需要用 `findChild` 或 `getattr` 按 objectName 访问

#### 自测补充（合并步骤项目）

在标准自测清单基础上，增加以下测试：

- [ ] ComboBox 切换正确显示对应卡片
- [ ] 每个卡片的 DC 联动都正常（逐一测试）
- [ ] 命令生成遍历所有启用的卡片
- [ ] 保存/读取正确处理所有卡片的参数
- [ ] 切换卡片后，之前卡片的参数保持不变

---

### 阶段五：功率分析仪配置内嵌（如果 step2 是 WT 配置）

#### 5.1 判断是否需要内嵌

检查 `Dialog_thaiXxx.py` 的 `_build_step2()` 方法：
- 如果有 `pushButton_S2_WT_3000_CONFIG` 等按钮 → 需要内嵌
- 如果已经是 radio+stackedWidget → 跳过

#### 5.2 重构 _build_step2()

将原来的 4 个 checkbox + 4 个 button 替换为 radio + QStackedWidget：

```python
def _build_step2(self):
    page = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(page)

    grp = QtWidgets.QGroupBox("功率分析仪配置")
    gLayout = QtWidgets.QGridLayout(grp)

    # 步骤启用复选框
    self.checkBox_S2 = self._make_checkbox("checkBox_S2", "step2", parent=self)
    gLayout.addWidget(self.checkBox_S2, 0, 0)

    # Radio buttons
    self.radioButton_S2_WT3000 = self._make_radio("radio_S2_WT3000", "WT3000", parent=self, checked=True)
    self.radioButton_S2_WT1800 = self._make_radio("radio_S2_WT1800", "WT1800", parent=self)
    self.radioButton_S2_WT1806E = self._make_radio("radio_S2_WT1806E", "WT1806E", parent=self)
    self.radioButton_S2_WT5000 = self._make_radio("radio_S2_WT5000", "WT5000", parent=self)

    radio_group = QtWidgets.QButtonGroup(None)
    radio_group.addButton(self.radioButton_S2_WT3000, 0)
    radio_group.addButton(self.radioButton_S2_WT1800, 1)
    radio_group.addButton(self.radioButton_S2_WT1806E, 2)
    radio_group.addButton(self.radioButton_S2_WT5000, 3)
    self._radio_group = radio_group  # 保持引用，防止垃圾回收

    # Radio 行布局
    radio_layout = QtWidgets.QHBoxLayout()
    for rb in [self.radioButton_S2_WT3000, self.radioButton_S2_WT1800,
               self.radioButton_S2_WT1806E, self.radioButton_S2_WT5000]:
        radio_layout.addWidget(rb)
    radio_layout.addStretch()
    gLayout.addLayout(radio_layout, 0, 1, 1, 3)

    # QStackedWidget
    self._wtStacked = QtWidgets.QStackedWidget()
    self._wtStacked.addWidget(build_wt3000_content(self))   # index 0
    self._wtStacked.addWidget(build_wt1800_content(self))   # index 1
    self._wtStacked.addWidget(build_wt1806e_content(self))  # index 2
    self._wtStacked.addWidget(build_wt5000_content(self))   # index 3
    gLayout.addWidget(self._wtStacked, 1, 0, 1, 4)

    # Radio 切换联动
    def _on_radio_toggled(btn, checked):
        if checked:
            self._wtStacked.setCurrentIndex(radio_group.id(btn))
    radio_group.buttonToggled.connect(_on_radio_toggled)

    layout.addWidget(grp)
    layout.addStretch()
    self.stackedWidget.addWidget(page)
```

**必须添加的 import**：

```python
from components.wt_config_content import (
    build_wt3000_content, build_wt1800_content,
    build_wt1806e_content, build_wt5000_content
)
```

**必须添加的 `_make_radio` 方法**（如果 Dialog 类中没有）：

```python
def _make_radio(self, name, text, parent=None, checked=False):
    rb = QtWidgets.QRadioButton(text)
    rb.setObjectName(name)
    if parent:
        rb.setParent(parent)
        setattr(self, name, rb)
    if checked:
        rb.setChecked(True)
    return rb
```

#### 5.3 修改 SCPITestWave.py — 移除弹窗连接

删除类似以下行：

```python
uiXxx.pushButton_S2_WT_3000_CONFIG.clicked.connect(wt_3000E_show)
uiXxx.pushButton_S2_WT_1800_CONFIG.clicked.connect(wt_1800_show)
uiXxx.pushButton_S2_WT_1806E_CONFIG.clicked.connect(wt_1806e_show)
uiXxx.pushButton_S2_WT_5000_CONFIG.clicked.connect(wt_5000_show)
```

#### 5.4 修改 SCPITestWave.py — WT 配置读取

在 `xxxSend()` 函数中，将 WT 配置读取改为使用 `_PageWidgetFinder`：

```python
# 修改前：
wt_config_dict = WT3000E_params_config(uiThiaWT3000E)

# 修改后：
from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder

if uiXxx.radioButton_S2_WT3000.isChecked():
    wt_config_dict = WT3000E_params_config(_PageWidgetFinder(uiXxx._wtStacked.widget(0)))
elif uiXxx.radioButton_S2_WT1800.isChecked():
    wt_config_dict = WT1800_params_config(_PageWidgetFinder(uiXxx._wtStacked.widget(1)))
elif uiXxx.radioButton_S2_WT1806E.isChecked():
    wt_config_dict = WT1806E_params_config(_PageWidgetFinder(uiXxx._wtStacked.widget(2)))
elif uiXxx.radioButton_S2_WT5000.isChecked():
    wt_config_dict = WT5000_params_config(_PageWidgetFinder(uiXxx._wtStacked.widget(3)))
```

#### 5.5 修改 Open_Save 文件

在 `utils/Open_Save_ThaiXxx.py` 中：

1. 添加 import：
```python
from utils.Open_Save_ThaiXieBoDianLiu import _PageWidgetFinder
```

2. 保存函数中，将 checkbox 改为 radio：
```python
# 修改前：
if uiXxx.checkBox_S2_WT3000.isChecked():

# 修改后：
if uiXxx.radioButton_S2_WT3000.isChecked():
```

3. WT 配置保存/读取改为使用 `_PageWidgetFinder`：
```python
# 修改前：
WT3000E_params_config(uiThiaWT3000E)

# 修改后：
WT3000E_params_config(_PageWidgetFinder(uiXxx._wtStacked.widget(0)))
```

4. 所有 QMessageBox 和 QFileDialog 的 parent 参数必须是 `None`（坑1+坑8）

---

### 阶段六：Open_Save 文件 — 其他修改

#### 6.1 检查 QMessageBox parent

搜索整个文件，确保所有 `QMessageBox.warning/information/critical` 的第一个参数是 `None`，不是 `dialog_window`。

```python
# 错误：
QMessageBox.warning(dialog_window, "标题", "内容")

# 正确：
QMessageBox.warning(None, "标题", "内容")
```

#### 6.2 检查 QFileDialog parent

搜索整个文件，确保所有 `QFileDialog.getSaveFileName/getOpenFileName` 的第一个参数是 `None`。

```python
# 错误：
QFileDialog.getSaveFileName(dialog_window, "保存", "./", "Text Files(*.csv)")

# 正确：
QFileDialog.getSaveFileName(None, "保存", "./", "Text Files(*.csv)")
```

#### 6.3 CSV 编码

确保所有文件读写使用 UTF-8 编码：

```python
# 写入：
with open(file_path, 'w+', encoding='utf-8-sig') as f:
    ...

# 读取：
try:
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        ...
except UnicodeDecodeError:
    with open(file_path, 'r', encoding='gbk') as f:
        ...
```

---

## 已踩坑点（必须逐一检查）

### 坑1：LazyDialog 不能作为 QMessageBox/QFileDialog 的 parent

- `dialog_windowXxx` 是 `LazyDialog` 实例，不是 `QWidget`
- 所有 Open/Save 工具函数中 `QMessageBox` 和 `QFileDialog` 的 parent 传 `None`
- **检查方法**：搜索 `dialog_window` 在 QMessageBox/QFileDialog 调用中的使用

### 坑2：_make_checkbox 不传 parent 不会存储到 self

- `_make_checkbox(name, text)` 不传 `parent` 时，只创建 widget 但不 `setattr(self, name, cb)`
- **检查方法**：搜索代码中引用的所有 UI 属性，确认对应的 `_make_checkbox`/`_make_combo`/`_make_input` 调用都传了 `parent=self`

### 坑3：reset 函数不能直接操作全局 Start/End 按钮

- reset 函数只重置计数器和 label，按钮状态由 `_sync_start_end_buttons()` 统一管理
- **检查方法**：搜索 `pushButton_StartTest.setEnabled` 和 `pushButton_EndTest.setEnabled`，确保不在 reset 函数中直接调用

### 坑4：按钮状态必须在启动时初始化 + 切换项目时同步

- 程序启动时计数器为 0 但按钮默认启用
- **检查方法**：确认信号连接处调用了 `_sync_start_end_buttons()` 初始化

### 坑5：调试后必须检查未定义属性

- 每个项目调试完毕后，必须检查代码中引用的所有 UI 属性是否都已定义
- **检查方法**：
  1. 搜索 `self.uiXxx.属性名` 引用
  2. 验证这些属性名在对应的 Dialog 文件中都有定义
  3. 特别注意 `_make_checkbox`、`_make_combo`、`_make_input` 创建的控件是否传了 `parent=self`

### 坑6：DC 验证错误标志会被覆盖

- `strShowErrorMessageBoxFlag` 在每个 DC 通道检查时会被覆盖
- **修复**：使用 `dc_error_messages` 列表收集所有错误，最后一次性显示

### 坑7：DC 变量未初始化会导致 UnboundLocalError

- 如果未勾选 step1 DC 通道，变量（如 `S1DC2Vmp`）未定义
- **修复**：在函数开头初始化所有 DC 变量为空字符串

### 坑8：所有 QMessageBox 和 QFileDialog 调用都需要检查 parent

- 不仅是 `utils/Open_Save_Thai*.py`，`SCPITestWave.py` 中的调用也需要检查
- **检查方法**：搜索 `QMessageBox\.(warning|information|critical)\(` 确保 parent 是 `None`

### 坑9：计数器变量未初始化会导致 UnboundLocalError

- `xxx_append_count` 在 Send 函数开头未声明 global 且未初始化
- **检查方法**：搜索每个 Send 函数中的 `+= 1`，确认对应的计数器变量在该函数的 `global` 声明中且有初始化检查
- **代码模式**：
```python
def xxxSend():
    global xxx_append_count  # 必须声明！
    if 'xxx_append_count' not in globals():
        xxx_append_count = 0
```

### 坑10：步骤启用复选框必须联动子控件

- 取消勾选步骤启用复选框后，下方的 DC 通道复选框仍可操作
- **检查方法**：确认每个步骤的 DC 复选框都有 `setEnabled(should_enable)` 联动

### 坑11：所有 DC 块必须联动 step1 DC 复选框

- step3/step4/step5/step7 中的 DC 块生成命令时，必须同时检查 step1 DC 复选框
- **检查方法**：搜索 Send 函数中所有 `checkBox_S*_DC`，确保每个都有对应的 `checkBox_S1_DC` 联动
- **这是最容易遗漏的步骤！**

---

## 自测清单（必须逐一完成）

### 自测1：启动测试

```bash
conda activate SolarAutoTestEnv
python SCPITestWave.py
```

- [ ] 程序正常启动，无 ImportError
- [ ] 无 NameError 或 AttributeError

### 自测2：对话框显示

- [ ] 进入 AutoTest → 选择项目 → 点击项目
- [ ] 对话框正常显示，无崩溃
- [ ] 步骤条正常显示
- [ ] 默认选中第一个步骤

### 自测3：WT 配置内嵌（如果有）

- [ ] 默认选中 WT3000，配置内容正确显示
- [ ] 切换 Radio 到 WT1800/WT1806E/WT5000，配置内容随之切换
- [ ] 取消勾选 checkBox_S2，确认 Radio + 配置内容全部禁用
- [ ] 重新勾选 checkBox_S2，确认 Radio + 配置内容恢复启用

### 自测4：DC 联动（step1 → step3+）

- [ ] step1 中勾选 DC1 → step3 中 DC1 复选框自动勾选且启用
- [ ] step1 中取消勾选 DC1 → step3 中 DC1 复选框自动取消勾选且禁用
- [ ] step1 中勾选 DC2/3/4 → step3 中对应 DC 复选框自动勾选
- [ ] step1 中取消勾选 DC2/3/4 → step3 中对应 DC 复选框自动禁用
- [ ] 对 step4/step5/step7 重复上述测试

### 自测5：关机步骤 DC 联动

- [ ] 关机步骤的 DC 复选框与 step1 联动（同上）
- [ ] 取消勾选关机步骤 checkbox → DC 复选框全部禁用
- [ ] 勾选关机步骤 checkbox + step1 DC → DC 复选框启用且自动勾选

### 自测5-B：合并步骤测试（如果有）

- [ ] ComboBox 切换正确显示对应卡片（每个选项都测试）
- [ ] 每个卡片的 DC 联动都正常（逐一测试每个卡片的 DC1-4）
- [ ] 切换卡片后，之前卡片的参数保持不变
- [ ] 命令生成遍历所有启用的卡片（勾选多个卡片，确认命令正确）
- [ ] 保存参数 → 重新读取 → 所有卡片参数正确回显
- [ ] 取消勾选步骤 checkbox → 所有卡片的 DC 复选框全部禁用

### 自测6：测试追加

- [ ] 点击"测试追加"按钮
- [ ] 计数器从 0 变为 1
- [ ] label_append_count 显示 "1"
- [ ] 操作日志显示"覆盖模式，开始生成命令..."
- [ ] 开始/结束试验按钮启用

### 自测7：测试追加（第二次）

- [ ] 再次点击"测试追加"按钮
- [ ] 计数器从 1 变为 2
- [ ] label_append_count 显示 "2"
- [ ] 操作日志显示"追加模式，开始生成命令..."
- [ ] 开始/结束试验按钮保持启用

### 自测8：重置计数

- [ ] 点击"重置计数"按钮
- [ ] 计数器归 0
- [ ] label_append_count 显示 "0"
- [ ] 开始/结束试验按钮禁用

### 自测9：切换项目

- [ ] 切换到另一个项目
- [ ] 再切换回来
- [ ] 计数器和 label 正确回显
- [ ] 按钮状态正确

### 自测10：保存参数

- [ ] 设置一些参数（勾选/取消勾选 checkbox、选择 combo 值等）
- [ ] 点击"保存"按钮
- [ ] 弹出文件选择对话框（无 TypeError）
- [ ] 选择保存位置，确认
- [ ] 弹出"保存完成"提示（无 TypeError）
- [ ] CSV 文件正常生成

### 自测11：读取参数

- [ ] 点击"读取"按钮
- [ ] 弹出文件选择对话框（无 TypeError）
- [ ] 选择之前保存的 CSV 文件
- [ ] 弹出"读取完成"提示（无 TypeError）
- [ ] 所有参数正确回显（checkbox、combo、input 等）
- [ ] WT 配置正确回显（radio 选中正确的设备，配置值正确）

### 自测12：WT 配置保存/读取（如果有）

- [ ] 选择 WT1800，修改一些配置
- [ ] 保存参数
- [ ] 重新读取参数
- [ ] WT1800 仍被选中，配置值正确回显
- [ ] 切换到 WT3000，确认配置为空/默认值

### 自测13：开始试验

- [ ] 先执行一次测试追加（计数 >= 1）
- [ ] 点击"开始试验"按钮
- [ ] 弹出设备连接检查（如果有设备未连接）
- [ ] 如果所有设备已连接，试验正常开始

### 自测14：结束试验

- [ ] 点击"结束试验"按钮
- [ ] 弹出二次确认弹窗
- [ ] 点击"取消"→ 弹窗关闭，试验继续
- [ ] 再次点击"结束试验"→ 确认 → 试验结束
- [ ] 计数器归 0，开始按钮禁用

### 自测15：操作日志

- [ ] 所有操作（追加、重置、保存、读取）都在主 UI 的 textEdit_ReturnMessage 中有日志输出
- [ ] 日志内容准确，无乱码

### 自测16：未定义属性检查（坑5）

在代码中搜索所有 `uiXxx.` 引用，验证每个属性都在 Dialog 文件中有定义：

```python
# 在 SCPITestWave.py 中搜索：
uiXxx.checkBox_
uiXxx.comboBox_
uiXxx.textEdit_
uiXxx.radioButton_
uiXxx.pushButton_

# 在 Dialog 文件中验证每个属性都有 self.xxx = ... 定义
```

### 自测17：DC 命令联动检查（坑11）

在 Send 函数中搜索所有 DC 块，确认每个都有 step1 DC 检查：

```python
# 搜索所有 DC 块：
grep -n "checkBox_S.*_DC.*isChecked" SCPITestWave.py

# 确认每个 DC 块前都有 checkBox_S1_DC 的检查
```

### 自测18：Global 声明检查（坑9）

确认 Send 函数的 global 声明包含计数器变量：

```python
def xxxSend():
    global xxx_append_count  # 必须存在
    if 'xxx_append_count' not in globals():
        xxx_append_count = 0
```

---

## 常见错误及修复

### ImportError: No module named 'utils'

**原因**：直接运行 `python utils/Open_Save_ThaiXxx.py` 时，Python 找不到 `utils` 包。

**修复**：在文件开头添加：
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**注意**：这个错误只在直接运行文件时出现，通过主程序 `SCPITestWave.py` 运行时不会出现。

### NameError: name 'Noneoverloads' is not defined

**原因**：替换 `dialog_window` 时拼写错误，写成了 `Noneoverloads`。

**修复**：将 `Noneoverloads` 改为 `None`。

### AttributeError: 'Ui_Dialog_xxx' object has no attribute 'checkBox_S3'

**原因**：`_make_checkbox` 没有传 `parent=self`，属性未存储到 self。

**修复**：在 `_make_checkbox` 调用时传 `parent=self`。

### TypeError: information(parent: Optional[QWidget]...): argument 1 has unexpected type 'LazyDialog'

**原因**：QMessageBox 的 parent 传了 `dialog_windowXxx`（LazyDialog 实例）。

**修复**：将 parent 改为 `None`。

### UnboundLocalError: local variable 'xxx_append_count' referenced before assignment

**原因**：Send 函数中使用了计数器变量但没有 global 声明。

**修复**：在 Send 函数开头添加 `global xxx_append_count` 和初始化检查。

---

## 文件修改检查表

每个项目修改完成后，填写以下检查表：

| 检查项 | 状态 | 备注 |
|--------|------|------|
| SCPITestWave.py: Append 函数已添加 | ☐ | |
| SCPITestWave.py: Send 函数 global 声明+初始化 | ☐ | |
| SCPITestWave.py: Send 函数末尾计数递增 | ☐ | |
| SCPITestWave.py: TestAppend 信号连接 | ☐ | |
| SCPITestWave.py: ResetCount 信号连接 | ☐ | |
| SCPITestWave.py: _sync_start_end_buttons 分支 | ☐ | |
| SCPITestWave.py: _reset_current_project_count 分支 | ☐ | |
| SCPITestWave.py: chooseDetailDialog 分支 | ☐ | |
| SCPITestWave.py: addtestDialog 分支 | ☐ | |
| SCPITestWave.py: 所有 DC 块联动 step1 | ☐ | |
| SCPITestWave.py: WT 配置读取改用 _PageWidgetFinder | ☐ | (如果有) |
| Dialog: step3 DC 联动 step1 | ☐ | |
| Dialog: step4 DC 联动 step1 | ☐ | (如果有) |
| Dialog: step5 DC 联动 step1 | ☐ | (如果有) |
| Dialog: step7 DC 联动 step1 | ☐ | (如果有) |
| Dialog: 关机步骤 DC 联动 step1 | ☐ | |
| Dialog: radio+stackedWidget 内嵌 | ☐ | (如果有) |
| Dialog: 步骤合并（ComboBox+StackedWidget） | ☐ | (如果用户要求) |
| Dialog: 合并卡片 DC 联动遍历所有 | ☐ | (如果合并) |
| Open_Save: QMessageBox parent = None | ☐ | |
| Open_Save: QFileDialog parent = None | ☐ | |
| Open_Save: CSV 编码 UTF-8 | ☐ | |
| Open_Save: radio 替换 checkbox | ☐ | (如果有) |
| Open_Save: _PageWidgetFinder | ☐ | (如果有) |
| 自测1-18 全部通过 | ☐ | (合并项目含自测5-B) |
