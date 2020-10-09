import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass

from automation_core.logging.string_utils import find_all


@dataclass
class JobLogParser(ABC):
    console_output: str
    TEST_RUN_INDICATION: str = 'short test summary info'
    EARLY_FAILURE_INDICATION: str = 'Traceback'
    END_OF_PIPELINE_INDICATION = 'Pipeline'

    @property
    @abstractmethod
    def exception_traceback(self):
        pass

    @abstractmethod
    def get_exception_to_show(self):
        pass

    def _get_end_of_traceback(self):
        if self.exception_traceback is not None:
            return '\n'.join(self.exception_traceback.splitlines()[-3:])  # gets last three lines of traceback


class TestsJobLogParser(JobLogParser):
    @property
    def exception_traceback(self):
        if self.exception_traceback is None:
            start = self.console_output.find(JobLogParser.TEST_RUN_INDICATION)
            end = self.console_output.find(JobLogParser.END_OF_PIPELINE_INDICATION, start) - 1
            return self.console_output[start:end]

    def get_exception_to_show(self):
        return self.exception_traceback


class EarlyFailedJobLogParser(JobLogParser):
    @property
    def exception_traceback(self):
        if self.exception_traceback is None:
            start = find_all(substring=JobLogParser.EARLY_FAILURE_INDICATION, full_string=self.console_output)[-1]
            end = self.console_output.find(sub=JobLogParser.END_OF_PIPELINE_INDICATION, __start=start) - 1
            return self.console_output[start:end]

    def get_exception_to_show(self):
        return self._get_end_of_traceback()


class JobLogParserFactory:
    @staticmethod
    def _did_run_tests(console_output):
        return JobLogParser.TEST_RUN_INDICATION in console_output

    def get_job_log_parser(self, console_output):
        if self._did_run_tests(console_output=console_output):
            return TestsJobLogParser(console_output)
        else:
            return EarlyFailedJobLogParser(console_output)


@dataclass
class JenkinsJob:
    folder: str
    name: str
    last_build: int
    last_result: str
    url: str
    did_run_tests: bool = None
    traceback: str = None
    last_exception: str = None
    log_parser: JobLogParser = None


@dataclass
class JenkinsJobList:
    jobs: typing.List[JenkinsJob]
