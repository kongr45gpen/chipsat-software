from lib.template_task import Task
from pycubed import cubesat

class Task(Task):

    def debug(self, msg, level=1, log=False):
        """
        Print a debug message formatted with the task name and color.
        Also log the message to a log file if log is set to True.

        :param msg: Debug message to print
        :type msg: str
        :param level: > 1 will print as a sub-level
        :type level: int
        :param log: Whether to log the message to a file
        :type log: bool
        """
        msg = super().debug(msg, level)
        if cubesat.sdcard and log:
            with open("./sd/debug", "a") as f:
                f.write(msg)
                f.write('\n')
