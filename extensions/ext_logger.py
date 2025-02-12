import logging
import os
from logging.handlers import TimedRotatingFileHandler
import time


def init_app(app):
    log_directory = os.path.join(os.getcwd(), 'storage/logs')

    # 份文件记录日志
    today = time.strftime('%Y%m%d')
    log_file_path = os.path.join(log_directory, f"app-{today}.log")

    # 创建日志记录器，设置日志级别
    handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=30)
    handler.setLevel(logging.INFO)

    # 创建日志格式
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)

    # 添加到 Flask 应用的日志记录器
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)