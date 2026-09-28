import configparser

# 关闭 %(…)s 插值，允许 ini 里写 %LOCALAPPDATA% 等环境变量字面量
config = configparser.ConfigParser(interpolation=None)
config.read("config_files/config.ini", encoding="utf-8")
