from abc import ABC, abstractmethod
from dataclasses import dataclass

from common.logging.string_utils import find_all


@dataclass
class JobLogParser(ABC):
    console_output: str
    TEST_RUN_INDICATION: str = 'short test summary info'
    EARLY_FAILURE_INDICATION: str = 'Traceback'
    END_OF_PIPELINE_INDICATION = 'Pipeline'
    _exception_traceback: str = None
    _exception_to_show: str = None

    @property
    @abstractmethod
    def exception_traceback(self):
        pass

    @property
    @abstractmethod
    def exception_to_show(self):
        pass


class TestsJobLogParser(JobLogParser):
    """
    A parser for a run in which tests were run
    """
    @property
    def exception_traceback(self):
        if self._exception_traceback is None:
            start = self.console_output.find(JobLogParser.TEST_RUN_INDICATION)
            end = self.console_output.find(JobLogParser.END_OF_PIPELINE_INDICATION, start) - 1
            self._exception_traceback = self.console_output[start:end]
        return self._exception_traceback

    @property
    def exception_to_show(self):
        return self.exception_traceback


class EarlyFailedJobLogParser(JobLogParser):
    """
    A parser for a run in which tests weren't run and an early failure occurred
    """
    def _get_end_of_traceback(self):
        if self.exception_traceback is not None:
            return '\n'.join(self.exception_traceback.splitlines()[-3:])  # gets last three lines of traceback

    @property
    def exception_traceback(self):
        if self._exception_traceback is None:
            start = find_all(substring=JobLogParser.EARLY_FAILURE_INDICATION, full_string=self.console_output)[-1]
            end = self.console_output.find(JobLogParser.END_OF_PIPELINE_INDICATION, start) - 1
            self._exception_traceback = self.console_output[start:end]
        return self._exception_traceback

    @property
    def exception_to_show(self):
        if self._exception_to_show is None:
            self._exception_to_show = self._get_end_of_traceback()
        return self._exception_to_show


class JobLogParserFactory:
    @staticmethod
    def _did_run_tests(console_output):
        return JobLogParser.TEST_RUN_INDICATION in console_output

    def get_job_log_parser(self, console_output):
        if self._did_run_tests(console_output=console_output):
            return TestsJobLogParser(console_output)
        else:
            return EarlyFailedJobLogParser(console_output)
