import typing
from dataclasses import dataclass

from jenkins_handler.jenkins_logs_parser import JobLogParser


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
