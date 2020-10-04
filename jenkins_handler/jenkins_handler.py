import typing
from dataclasses import dataclass

import jenkins
import os
import re

# from framework.agent.vmwareapi.vcenter_data import VCenterData
# from infra import log_wrapper
# from infra.exceptions.illegal_state_exception import IllegalStateException
# from utils import condition_polling
import requests

os.environ["PYTHONHTTPSVERIFY"] = "0"
JENKINS_URL = 'https://chief'
JENKINS_USERNAME = 'automation'
JENKINS_PASSWORD = 'tuyunmhv2018!'


@dataclass
class JenkinsJob:
    folder: str
    name: str
    last_build: int
    last_result: str
    url: str
    traceback: str = None
    last_exception: str = None


@dataclass
class JenkinsJobList:
    jobs: typing.List[JenkinsJob]


def find_all(substring, full_string):  # TODO: move to infra (string utils)
    return [m.start() for m in re.finditer(substring, full_string)]


class JenkinsHandler:
    def __init__(self, server: jenkins.Jenkins):
        self.server = server

    def _get_build_result(self, project_path, build_number):
        return self.server.get_build_info(name=project_path, number=build_number)['result']

    def was_build_successful(self, project_path, build_number):
        # logger.debug(f'checking if dev build #{build_number} was successful')
        try:
            result = self._get_build_result(project_path=project_path, build_number=build_number)
        except Exception as e:
            # logger.warning(f'got exception while trying to get build info: {e}')
            return False
        if result is not None:
            return 'SUCCESS' in result

    def get_build_name(self, project_path, build_number):
        # logger.debug('getting build name')
        return self.server.get_build_info(name=project_path, number=build_number)['displayName']

    def get_console_output(self, project_path, build_number):
        # logger.debug(f'getting console output, project path: <{project_path}>, build number: <{build_number}>')
        return self.server.get_build_console_output(project_path, build_number)

    def get_all_build_numbers(self, project_path) -> typing.List:
        # logger.debug(f'getting all builds from job {project_path}')
        builds = self.server.get_job_info(project_path)['builds']
        return list(map(lambda build: build['number'], builds))

    def _get_last_build_number(self, project_path: str):
        return self.server.get_job_info(project_path)['lastBuild']['number']

    def get_all_builds(self) -> JenkinsJobList:
        try:

            all_jenkins_jobs = self.get_job_objects(folder_path='QA/Nightly')
            jobs = [
                JenkinsJob(url=j['url'], name=j['name'], last_build=j['lastBuild']['number'],
                           last_result=j['color'],
                           folder=os.path.dirname(j['fullName']))
                for j in
                all_jenkins_jobs]

            for job in jobs:
                if job.last_result == 'red':
                    job.traceback = self.get_exception_traceback(job)
                    job.last_exception = self.get_last_three_lines_of_traceback(job.traceback)
            return JenkinsJobList(jobs=jobs)

        except requests.exceptions.ConnectionError as e:
            if 'HTTPSConnectionPool' in str(e):
                raise ConnectionError('Could not reach jenkions server - make sure you are connected with VPN')
                # abort(HTTPStatus.FORBIDDEN)

    def get_last_three_lines_of_traceback(self, traceback):
        if traceback is not None:
            return '\n'.join(traceback.splitlines()[-3:])  # get last three lines of traceback

    def get_exception_traceback(self, job):  # TODO: extract to a class and prettify
        last_console = self.get_last_console_output(job)
        if 'short test summary info' in last_console:  # TODO: const
            start = last_console.find('short test summary info')
            end = last_console.find('Pipeline', start) - 1
            return last_console[start:end]
        start = find_all('Traceback', last_console)[-1]
        end = last_console.find('Pipeline', start) - 1
        return last_console[start:end]

    def get_last_console_output(self, job: JenkinsJob):
        return self.server.get_build_console_output(name=f'{job.folder}/{job.name}',
                                                    number=job.last_build)

    def get_job_objects(self, folder_path: str):
        jobs_paths = self.get_jobs_paths(folder_path=folder_path)
        all_jenkins_jobs = [self.server.get_job_info(path) for path in jobs_paths]
        return all_jenkins_jobs

    def get_jobs_paths(self, folder_path: str) -> typing.List[str]:
        jobs_names = [job['name'] for job in self.server.get_job_info(name=folder_path)['jobs']]
        jobs_paths = [f'{folder_path}/{name}' for name in jobs_names]
        return jobs_paths


def get_jenkins_handler() -> 'JenkinsHandler':
    # logger.debug('getting jenkins handler object')
    try:
        server = jenkins.Jenkins(url=JENKINS_URL, username=JENKINS_USERNAME, password=JENKINS_PASSWORD)
    except ConnectionError:
        print('Could not connect to jenkins server')
        return None

    return JenkinsHandler(server=server)
