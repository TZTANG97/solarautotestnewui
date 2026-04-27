solarautotestdev/
├── SCPITestWave.py                      # 旧主文件：先保留，逐步变薄
├── main.py                              # 可选：真正入口只负责启动
├── app/
│   ├── __init__.py
│   ├── bootstrap.py                     # 启动装配：创建窗口、setupUi、信号绑定、初始化顺序
│   ├── context.py                       # 全局上下文/运行时状态容器（过渡层）
│   ├── app_state.py                     # 项目状态、当前试验状态、页面状态
│   └── app_facade.py                    # 对外统一入口，做转调兼容
├── ui/
│   ├── __init__.py
│   ├── window_manager.py                # 所有 show()/hide()/弹窗展示逻辑
│   ├── dialog_registry.py               # 对话框注册与引用管理
│   └── signal_bindings.py               # 信号槽绑定集中管理
├── devices/
│   ├── __init__.py
│   ├── ac_controller.py                 # AC 设备连接/断开/读写/显示控制
│   ├── dc_controller.py                 # DC1~DC4 设备连接/断开/读写/显示控制
│   ├── wt_controller.py                 # WT3000/WT1800/WT1806E/WT5000 相关控制
│   ├── dl850_controller.py              # DL850 相关控制
│   └── scpi_common.py                   # SCPI 通用封装、资源配置、异常提示
├── projects/
│   ├── __init__.py
│   ├── project_router.py                 # 主项目/子项目选择、项目跳转
│   ├── project_state.py                  # project_now 等状态管理
│   └── project_catalog.py                # 项目映射表、试验名称与窗口/流程映射
├── tests/
│   ├── __init__.py
│   ├── flow_common.py                   # 通用试验流程辅助函数
│   ├── step_builder.py                  # 步骤数组/命令数组构造
│   ├── time_utils.py                    # 时间换算、时长处理
│   ├── command_templates.py             # 命令模板、RampCommand 等
│   ├── fixed_pf/
│   │   ├── __init__.py
│   │   ├── runner.py
│   │   └── ui_helpers.py
│   ├── overloads/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── zhiliufenliang/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── static_qu/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── static_cosphi/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── cosphi_brazil/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── volt_protect_10min/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── guopin_jiangzai/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── test_pu/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── guoqianya_pin/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── guoqianpin_immun/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── dianyashanbian/
│   │   ├── __init__.py
│   │   └── runner.py
│   ├── chonglian/
│   │   ├── __init__.py
│   │   └── runner.py
│   └── xiebodianliu/
│       ├── __init__.py
│       └── runner.py
├── config/
│   ├── __init__.py
│   ├── app_config.py                    # 配置文件读取
│   ├── path_config.py                   # 路径常量
│   └── wt_config.py                     # WT 参数配置相关
├── infra/
│   ├── __init__.py
│   ├── logging_setup.py                 # 日志初始化
│   ├── exception_handler.py             # 统一异常处理
│   └── message_box.py                   # 消息提示封装
└── utils/
    ├── __init__.py
    ├── windows_helpers.py               # 窗口枚举、按钮查找、句柄辅助
    ├── file_dialogs.py                  # 打开/保存文件对话框封装
    ├── ui_helpers.py                    # UI 小工具函数
    └── time_helpers.py                  # 通用时间处理