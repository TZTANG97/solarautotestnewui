# 共享目录打开「启动测试版」

## 场景

多台电脑打开**同一份共享工程目录**（网盘 / `\\服务器\share` / 映射盘），点 `启动测试版.bat`。

## 以前能开、后来不能：常见原因

1. **启动器改成「本机独立虚拟环境」**  
   环境在 `%LOCALAPPDATA%\SolarAutoTestDev\.venv`，不再默认用共享盘里的 `.venv`。  
   别的电脑第一次没有本机 venv，又没网同步依赖 → 起不来。

2. **Windows 禁止直接运行网上的 exe**  
   共享盘上的 `tools\uv.exe` 在其它电脑上双击/调用常被拦。

3. **`tools\uv.exe` 不在 Git 里**  
   若共享的是「纯克隆、没带 tools\uv.exe」的目录，也会缺启动器。

## 现在启动器会做什么

1. 若检测到网络路径：把 `tools\uv.exe` **复制到本机** `%LOCALAPPDATA%\SolarAutoTestDev\uv.exe` 再运行  
2. 本机还没有 venv、但共享目录里有 `.venv`：自动**回退用共享 .venv**（兼容以前用法）  
3. 本机 venv 首次失败时：自动再 `uv sync` 一次

## 推荐用法（稳）

| 角色 | 做什么 |
|---|---|
| 主机（共享提供者） | 保证共享里有完整工程 + `tools\uv.exe`；可选保留能用的 `.venv` |
| 其它电脑 | 点 `启动测试版.bat`；首次允许访问外网装依赖到本机 AppData |
| 长期 | 每台电脑用自己的 `%LOCALAPPDATA%\SolarAutoTestDev\.venv`，避免多机抢同一个网盘 venv |

## 自检

在共享目录打开 CMD：

```bat
启动测试版.bat --check
```

应看到 `uv:` 指向本机 AppData 或 tools，并打印 `[OK]`。
