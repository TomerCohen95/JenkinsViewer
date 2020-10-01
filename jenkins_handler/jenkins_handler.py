import typing
from http import HTTPStatus

import jenkins
import os
import re

# from framework.agent.vmwareapi.vcenter_data import VCenterData
# from infra import log_wrapper
# from infra.exceptions.illegal_state_exception import IllegalStateException
# from utils import condition_polling
import requests

from automation_core.named_json import NamedJson

os.environ["PYTHONHTTPSVERIFY"] = "0"
JENKINS_URL = ''
JENKINS_USERNAME = ''
JENKINS_PASSWORD = '!'


# logger = log_wrapper.logger()


# class ManagementJenkinsHandler:
#     _jenkins_handler: 'JenkinsHandler'
#     _project_path: str
#
#     def __init__(self, jenkins_handler, project_path='Management/Management-CI'):
#         self._jenkins_handler = jenkins_handler
#         self._project_path = project_path
#
#     def get_rpm_url(self, version):
#         logger.debug(f'getting rpm url from management jenkins job - {self._jenkins_handler}')
#         latest_successful_build = self._get_latest_successful_build_number(version=version)
#         console_output = self._jenkins_handler.get_console_output(self._project_path,
#                                                                   build_number=latest_successful_build)
#         return self._get_rpm_url_from_output(console_output)
#
#     def _get_latest_successful_build_number(self, version) -> int:
#         logger.debug('getting latest successful build from branch dev')
#         builds = self._jenkins_handler.get_all_build_numbers(self._project_path)
#         for build in builds:
#             if self._is_build_from_branch(build=build, version=version) and self._jenkins_handler.was_build_successful(
#                     project_path=self._project_path, build_number=build):
#                 logger.info(f'latest successful build from branch dev is - {build}')
#                 return build
#         raise IllegalStateException(f'Could not find successful build for branch {version}')
#
#     def _is_build_from_branch(self, build, version):
#         logger.debug(f'checking if build is {version}')
#         build_name = self._jenkins_handler.get_build_name(project_path=self._project_path, build_number=build)
#         return (f'dev - develop_{version}' in build_name) or (f'master_{version} - develop_{version}' in build_name)
#
#     @staticmethod
#     def _get_rpm_url_from_output(console_output: str):
#         logger.debug('extracting rpm url from build console output')
#         # dev local rpm url is \ test local rpm url is:
#         dhub_repo = 'dev'
#         if VCenterData.is_gve():
#             dhub_repo = 'test'
#         return re.search(f'{dhub_repo} local rpm url is: (https://.*\\.rpm)', console_output).group(1)
#

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

    def get_all_builds(self):
        try:

            all_jenkins_jobs = self.get_job_objects(folder_path='QA/Nightly')

            jobs = [
                JenkinsJob(json_obj={}, name=j['name'], last_build=j['lastBuild']['number'], last_result=j['color'],
                           last_console=self.server.get_build_console_output(name=j['fullName'],
                                                                             number=j['lastBuild'][
                                                                                 'number'])) for j in
                all_jenkins_jobs]

            return JenkinsJobList.get_jenkins_jobs_object(jobs=jobs).dumps()
            # return flask.jsonify(ret_val.dumps())

        except requests.exceptions.ConnectionError as e:
            if 'HTTPSConnectionPool' in str(e):
                pass
                # abort(HTTPStatus.FORBIDDEN)

    def get_job_objects(self, folder_path: str):
        jobs_paths = self.get_jobs_paths(folder_path=folder_path)
        all_jenkins_jobs = [self.server.get_job_info(path) for path in jobs_paths]
        return all_jenkins_jobs

    def get_jobs_paths(self, folder_path: str) -> typing.List[str]:
        jobs_names = [job['name'] for job in self.server.get_job_info(name=folder_path)['jobs']]
        jobs_paths = [f'{folder_path}/{name}' for name in jobs_names]
        return jobs_paths


class JenkinsJob(NamedJson):
    # server: jenkins.Jenkins
    name: str
    last_build: int
    last_result: int
    last_console: str
    url: str

    def __init__(self, json_obj, name=None, last_build=None, last_result=None, last_console=None, url=None):
        super().__init__(json_obj)
        self.url = url
        self.last_console = last_console
        self.last_result = last_result
        self.last_build = last_build
        self.name = name


class JenkinsJobList(NamedJson):
    jobs: typing.List[JenkinsJob]

    @staticmethod
    def get_jenkins_jobs_object(jobs: typing.List[JenkinsJob]) -> 'JenkinsJobList':
        response = JenkinsJobList(json_obj={})
        response.jobs = jobs
        return response

        # alljobs = [JenkinsJob(name=job['name'], last_result=job['color']) for job in jobs]

        # return '</br>'.join()

    # def wait_for_build_to_finish(self, build_number, job_path):
    #     # logger.debug(f'wait for build number: {build_number} to finish')
    #     condition_polling.poll(
    #         func=lambda: self._get_build_result(project_path=job_path, build_number=build_number) == 'SUCCESS',
    #         sleep_time_sec=10, timeout_in_sec=660)

    # def wait_for_build_to_start(self, build_number, job_path):
    #     logger.debug(f'wait for build number: {build_number} to start')
    #     condition_polling.poll(
    #         func=lambda: self._get_last_build_number(project_path=job_path) == build_number, timeout_in_sec=660)


# class ApplianceK8sJenkinsHandler(JenkinsHandler):
#     def __init__(self, server):
#         super().__init__(server)
#         self.create_path = 'Management/K8s/Development-QA/Create appliance in K8S - DEV QA'
#         self.delete_path = 'Management/K8s/Development-QA/Delete appliance in K8S - DEV QA'
#
#     def create_appliance(self, image_tag: str = 'latest', msp_option: bool = False, max_replicas: int = 5) -> str:
#         next_build_number = self.server.get_job_info(self.create_path)['nextBuildNumber']
#         logger.debug(f'going to run create appliance job path: {self.create_path} build number: {next_build_number}')
#         self.server.build_job(self.create_path,
#                               parameters={'TAG': image_tag, 'MSP_OPTION': msp_option,
#                                           'MAX_REPLICAS': max_replicas})
#         self.wait_for_build_to_start(build_number=next_build_number, job_path=self.create_path)
#         self.wait_for_build_to_finish(build_number=next_build_number, job_path=self.create_path)
#         console_output = self.server.get_build_console_output(self.create_path, next_build_number)
#         return self._get_appliance_name_from_output(console_output=console_output)
#
#     def delete_appliance(self, namespace: str):
#         logger.debug(f'going to run delete appliance with namespace: {namespace}')
#         next_build_number = self.server.get_job_info(self.delete_path)['nextBuildNumber']
#         self.server.build_job(self.delete_path, parameters={'NAMESPACE': namespace})
#         self.wait_for_build_to_start(build_number=next_build_number, job_path=self.delete_path)
#         self.wait_for_build_to_finish(build_number=next_build_number, job_path=self.delete_path)
#
#     @staticmethod
#     def _get_appliance_name_from_output(console_output: str):
#         logger.debug('extracting appliance name from build console output')
#         pattern = r'automation-[0-9]*-.*testing.deepinstinctweb.com'
#         return re.search(pattern=pattern, string=console_output).group(0)
#
#
# class LocustK8sScalingJenkinsHandler(JenkinsHandler):
#
#     def __init__(self, server):
#         super().__init__(server)
#         self.path = 'DevOps/update locust server'
#
#     def deploy_code_to_locust_worker(self, locust_ip: str, branch: str):
#         next_build_number = self.server.get_job_info(self.path)['nextBuildNumber']
#         logger.debug(
#             f'going to deploy branch: {branch} to locust server: {locust_ip} build number: {next_build_number}')
#         self.server.build_job(self.path,
#                               parameters={'MASTER_IP': locust_ip, 'GIT_BRANCH': branch})
#         self.wait_for_build_to_start(build_number=next_build_number, job_path=self.path)
#         self.wait_for_build_to_finish(build_number=next_build_number, job_path=self.path)
#
#
# class AgentJenkinsHandler(JenkinsHandler):
#
#     def __init__(self, server, branch):
#         super().__init__(server)
#         self.path = f'Windows/WindowsAgent/{branch}'
#         self.branch = branch
#
#     def get_installer_url_for_latest_build(self):
#         logger.info(f'fetching latest successful job under {self.path}')
#         builds = self.server.get_job_info(name=self.path)['builds']
#         for build in builds:
#             if self.was_build_successful(project_path=self.path, build_number=build['number']):
#                 logger.info(f'Found successful build #{build["number"]}: {build["url"]}')
#                 installer_name = 'WizardInstaller_deep' if self.branch == 'develop' else 'InstallerManaged_deep'
#                 return f'{build["url"]}artifact/bin/Release/Win32/{installer_name}.exe'
#
#         raise IllegalStateException('Could not find Successful build')


def get_jenkins_handler() -> 'JenkinsHandler':
    # logger.debug('getting jenkins handler object')
    try:
        server = jenkins.Jenkins(url=JENKINS_URL, username=JENKINS_USERNAME, password=JENKINS_PASSWORD)
    except ConnectionError:
        print('Could not connect to jenkins server')
        return None

    return JenkinsHandler(server=server)
