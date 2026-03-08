import sys
from loguru import Logger, logger

# 首先，移除默认的控制台输出，以便完全自定义
logger.remove()

# Sink 1: 控制台，用于开发调试，输出彩色、详细的日志
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    colorize=True,
    enqueue=True,
)

# Sink 2: 主日志文件，记录所有INFO及以上级别的日志，采用结构化JSON格式
logger.add(
    "logs/info/structured_log.json",
    level="INFO",
    serialize=True,  # 输出JSON
    rotation="1 day",
    enqueue=True,
)

# Sink 3: 错误专用文件，只记录ERROR及以上级别，便于快速定位问题
logger.add(
    "logs/error/error_only.log",
    level="ERROR",
    format="{time} | {level} | {message}",
    rotation="1 week",
    enqueue=True,
)


def get_logger(name: str) -> Logger:
    """
    获取一个命名的 logger 实例，便于区分不同模块的日志来源。

    参数:
    - name (str): Logger 的名称，通常使用模块名或类名。

    返回:
    - logger: 一个配置好的 logger 实例，可以直接使用 logger.debug/info/error 等方法记录日志。
    """
    return logger.bind(name=name)
