import datetime
import os
import random
import sys
import unittest

__all__ = ["helpers", "test_knapsack", "test_partition", "test_reports", "tAPI", "try_redirect_out"]

from pathlib import Path

from flags.flags import printToFile, verbose

if __name__ == '__main__':
    unittest.main()

dtNow = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
random.seed(hash(dtNow))
randomTestCount = 2

script_dir = Path(os.path.dirname(__file__))  # <-- absolute dir the script is in
out_dir = os.path.join(f"{script_dir.parent}", f"Out")
test_data_dir = os.path.join(f"{script_dir.parent.parent}", "testData")

if verbose:
    print(f"Initial random seed is {hash(dtNow)}")


# pycharm stdout wrapper
class Logger:
    def __init__(self, filename):
        self.log = open(filename, "a")

    def write(self, message):
        self.log.write(message)

    def getvalue(self):
        pass

    def close(self):
        self.log.close()


# pycharm stdout wrapper
class StdoutLogger:
    def __init__(self, std):
        self.terminal = std

    def write(self, message):
        self.terminal.write(message)

    def getvalue(self):
        pass

    def close(self):
        pass


stdLogger = StdoutLogger(sys.stdout)


def try_redirect_out(fileNamePart, prefix):
    if printToFile:
        nt = datetime.datetime.now()

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        fileName = os.path.join(f"{out_dir}", f"{fileNamePart}.{prefix}.out.{nt.hour}-{nt.minute}.txt")

        if isinstance(sys.stdout, Logger):
            sys.stdout.close()

        sys.stdout = stdLogger
        print(f"{fileNamePart}.{prefix}, output fileName: {fileName}")

        sys.stdout = Logger(fileName)


def restore_out():
    if isinstance(sys.stdout, Logger):
        sys.stdout.close()

    sys.stdout = stdLogger
