#coding=utf-8
# 只是建两个文件夹啦
import os

if __name__ == "__main__":
    if not os.path.exists("logs"):
        os.mkdir("logs")
    if not os.path.exists("traceback"):
        os.mkdir("traceback")