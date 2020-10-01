import typing
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

from automation_core.named_json import NamedJson

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


if __name__ == '__main__':
    app.run()

#
# from models import Result
# import requests
# from flask import abort
#
# from automation_core.named_json import NamedJson
# from jenkins_handler import jenkins_handler
# from jenkins_handler.jenkins_handler import JenkinsHandler
# import typing
# from http import HTTPStatus
#

    # @staticmethod
    # def get_jenkins_job_object(name=None, last_build=None, last_result=None, last_console=None):
    #     response = JenkinsJob(json_obj={})
    #     response.name = name
    #     response.last_build = last_build
    #     response.last_result = last_result
    #     response.last_console = last_console
    #     return response



# jenkins = jenkins_handler.get_jenkins_handler()
# jenkins.get_all_build_numbers('/QA/Nightly/Windows10x64 Managed 2.4')
# builds_ints = jenkins.get_all_build_numbers('Management/Management-CI')
# builds_ints = jenkins.server.get_jobs(view_name='QA')

# builds = [str(build) for build in builds_ints]
# return str(','.join(builds))
#
#
# @app.route('/')
# def hello_world():
#     return 'Hello World!'
#
#
# @app.route('/getallbuilds')
# def get_all_builds():
#     try:
#         jenkins = jenkins_handler.get_jenkins_handler()
#
#         # jenkins.get_all_build_numbers('/QA/Nightly/Windows10x64 Managed 2.4')
#         # builds_ints = jenkins.get_all_build_numbers('Management/Management-CI')
#         # jenkins.server.get_job_info(f'QA/Nightly/{name}')
#
#         all_jenkins_jobs = get_job_objects(jenkins, folder_path='QA/Nightly')
#
#         jobs = [
#             JenkinsJob(json_obj={}, name=j['name'], last_build=j['lastBuild']['number'], last_result=j['color'],
#                        last_console=jenkins.server.get_build_console_output(name=j['fullName'],
#                                                                             number=j['lastBuild'][
#                                                                                 'number'])) for j in
#             all_jenkins_jobs]
#
#         ret_val = JenkinsJobList.get_jenkins_jobs_object(jobs=jobs)
#         return flask.jsonify(ret_val.dumps())
#
#     except requests.exceptions.ConnectionError as e:
#         if 'HTTPSConnectionPool' in str(e):
#             abort(HTTPStatus.FORBIDDEN)
#     # alljobs = [JenkinsJob(name=job['name'], last_result=job['color']) for job in jobs]
#
#     # return '</br>'.join()
#
#

# if __name__ == '__main__':
#     app.run(debug=True)
