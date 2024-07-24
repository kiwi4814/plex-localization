import os
import re
import logging
from logging.handlers import TimedRotatingFileHandler

# 设置日志格式
LOG_PATH = os.path.dirname(__file__) + '/logs/'
LOG_NAME = 'log'
LOG_FORMAT = '[%(asctime)s] - %(levelname)s: %(message)s'

# 开启日志
def get_logger(log_path=LOG_PATH, log_name=LOG_NAME, log_format=LOG_FORMAT):
    
    # 如无log文件则先创建
    if os.path.exists(log_path) != True:
        os.mkdir(log_path)
        
    # 创建logger对象。传入logger名字
    logger = logging.getLogger(log_name)
    # 如果已经实例过一个相同名字的 logger，则不用再追加 handler
    if not logger.handlers:
        log_path = log_path + log_name
        # 设置日志记录等级
        logger.setLevel(logging.INFO)
        # interval 滚动周期，
        # when="MIDNIGHT", interval=1 表示每天0点为更新点，每天生成一个文件
        # backupCount  表示日志保存个数
        file_handler = TimedRotatingFileHandler(
            filename=log_path, when="MIDNIGHT", interval=1, backupCount=7, encoding='utf-8'
        )
        # filename="mylog" suffix设置，会生成文件名为mylog.2020-02-25.log
        file_handler.suffix = "%Y-%m-%d.log"
        # extMatch是编译好正则表达式，用于匹配日志文件名后缀
        # 需要注意的是suffix和extMatch一定要匹配的上，如果不匹配，过期日志不会被删除。
        file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        # 定义日志输出格式
        file_handler.setFormatter(
            logging.Formatter(
            log_format
            )
        )
        logger.addHandler(file_handler)
    return logger