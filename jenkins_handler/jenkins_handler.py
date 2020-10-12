import typing
import jenkins
import os
import requests
from common.logging import log_wrapper
from jenkins_handler.jenkins_config import JenkinsConfig
from jenkins_handler.jenkins_job import JenkinsJobList, JenkinsJob
from jenkins_handler.jenkins_logs_parser import JobLogParserFactory

os.environ["PYTHONHTTPSVERIFY"] = "0"

logger = log_wrapper.logger()


class JenkinsHandler:
    def __init__(self, server: jenkins.Jenkins):
        self.server = server

    def get_all_builds_results(self) -> JenkinsJobList:
        try:
            all_jenkins_jobs = self._get_job_objects(folder_path=JenkinsConfig.JOBS_FOLDER)
            jobs_results = self._convert_jenkins_objects_to_results(all_jenkins_jobs)
            return JenkinsJobList(jobs=jobs_results)

        except requests.exceptions.ConnectionError as e:
            if 'HTTPSConnectionPool' in str(e):
                raise ConnectionError('Could not reach jenkions server - make sure you are connected with VPN')

    def _convert_jenkins_objects_to_results(self, all_jenkins_jobs):
        jobs = [
            JenkinsJob(url=job['url'], name=job['name'], last_build=job['lastBuild']['number'],
                       last_result=job['color'], folder=os.path.dirname(job['fullName']))
            for job in all_jenkins_jobs]

        return self._update_failed_builds_exceptions(jobs)

    def _update_failed_builds_exceptions(self, jobs):
        for job in jobs:
            if job.last_result == 'red':
                job.log_parser = JobLogParserFactory().get_job_log_parser(
                    console_output=self._get_last_console_output(job))
                job.traceback = job.log_parser.exception_traceback
                job.last_exception = job.log_parser.exception_to_show
        return jobs

    def _get_last_console_output(self, job):
        return self.server.get_build_console_output(name=f'{job.folder}/{job.name}',
                                                    number=job.last_build)

    def _get_job_objects(self, folder_path: str):
        jobs_paths = self._get_jobs_paths(folder_path=folder_path)
        all_jenkins_jobs = [self.server.get_job_info(path) for path in jobs_paths]
        return all_jenkins_jobs

    def _get_jobs_paths(self, folder_path: str) -> typing.List[str]:
        jobs_names = [job['name'] for job in self.server.get_job_info(name=folder_path)['jobs']]
        jobs_paths = [f'{folder_path}/{name}' for name in jobs_names]
        return jobs_paths


def get_jenkins_handler() -> 'JenkinsHandler':
    logger.debug('getting jenkins handler object')
    try:
        server = jenkins.Jenkins(url=JenkinsConfig.JENKINS_URL, username=JenkinsConfig.JENKINS_USERNAME,
                                 password=JenkinsConfig.JENKINS_PASSWORD)
    except ConnectionError:
        logger.exception('Could not connect to jenkins server')
        return None

    return JenkinsHandler(server=server)
