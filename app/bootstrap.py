"""应用启动装配入口。

当前阶段这个模块只提供一个很薄的装配层，
目标是把主程序里最容易抽离的初始化逻辑先集中起来。

注意：
- 这里不改变试验业务逻辑。
- 这里只负责创建/注入上下文，并预留后续启动流程迁移位置。
"""

from typing import Any

from app.context import AppContext, get_app_context


def build_context(ui: Any = None, logger: Any = None, rm: Any = None) -> AppContext:
    """创建或更新应用上下文。

    参数：
    - ui: 主界面对象
    - logger: 日志对象
    - rm: VISA ResourceManager 或等价对象

    返回：
    - AppContext 实例
    """
    context = get_app_context()
    context.ui = ui
    context.logger = logger
    context.rm = rm
    return context


def bootstrap(ui: Any = None, logger: Any = None, rm: Any = None) -> AppContext:
    """启动装配入口。

    当前仅完成上下文构建，后续可继续迁移：
    - 控制器初始化
    - 信号绑定
    - 默认状态恢复
    - 页面显示与初始刷新
    """
    return build_context(ui=ui, logger=logger, rm=rm)
