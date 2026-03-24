import sys,os
from loguru import logger

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(root_dir, "logs")

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

class MyLogger:
    def __init__(self):
        self.logger = logger
        self.logger.remove()
        self.logger.add(sys.stdout,level="DEBUG",
                        format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "
                            "{process.name} | "
                            "{thread.name} | "
                            "<cyan>{module}</cyan>.<cyan>{function}</cyan>"
                            ":<cyan>{line}</cyan> | "
                            "<level>{level}</level>:"
                            "<cyan>{message}</cyan>",
                        )
    def get_logger(self):
        return self.logger
logger = MyLogger().get_logger()