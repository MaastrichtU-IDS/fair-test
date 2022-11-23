import datetime
from typing import List, Optional


class FairTestLogger:
    """Class to manipulate a FAIR metrics test logs"""

    def __init__(self) -> None:
        self._logs: List[str] = []

    def __repr__(self) -> str:
        return "\n".join(self.logs)

    @property
    def logs(self) -> List[str]:
        return self._logs

    @logs.setter
    def logs(self, value):
        self._logs = value

    def log(self, log_msg: str, prefix: Optional[str] = None) -> None:
        # Add timestamp?
        log_msg = "[" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")) + "] " + log_msg
        if prefix:
            log_msg = prefix + " " + log_msg
        self._logs.append(log_msg)

    def warn(self, log_msg: str) -> None:
        """
        Log a warning related to the FAIR test execution (add to the comments of the test)

        Parameters:
            log_msg: Message to log
        """
        self.log(log_msg, "WARN:")

    def info(self, log_msg: str) -> None:
        """
        Log an info message related to the FAIR test execution (add to the comments of the test)

        Parameters:
            log_msg: Message to log
        """
        self.log(log_msg, "INFO:")

    def failure(self, log_msg: str) -> None:
        """
        Log a failure message related to the FAIR test execution (add to the comments of the test and set score to 0)

        Parameters:
            log_msg: Message to log
        """
        self.score = 0
        self.log(log_msg, "FAILURE:")

    def success(self, log_msg: str) -> None:
        """
        Log a success message related to the FAIR test execution (add to the comments of the test and set score to 1)

        Parameters:
            log_msg: Message to log
        """
        self.log(log_msg, "SUCCESS:")

    # def __call__(self) -> List[str]:
    #     return self._logs
