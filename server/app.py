import flask
import requests
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import os

from jenkins_wrapper import jenkins_handler

from configs.config import Config

app = Flask(__name__, template_folder=f'{os.path.dirname(os.path.dirname(__file__))}/templates')
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from server.models import Result


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form['url']
            r = requests.get(url)
            print(r.text)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
    results = Result.query.all()
    for res in results:
        if res.last_exception is not None:
            pass
            # res.last_exception = res.last_exception.replace('\n', '</br>')
    return render_template('index.html', errors=errors, results=results)


@app.route('/update')
def update_nightly_results():
    Result.query.delete()
    db.session.commit()
    jenkins = jenkins_handler.get_jenkins_handler(url=Config.JENKINS_URL, username=Config.JENKINS_USERNAME,
                                                  password=Config.JENKINS_PASSWORD)
    builds = jenkins.get_all_builds_results(jobs_folder_path=Config.JOBS_FOLDER)
    for build in builds.jobs:
        result = Result(
            name=build.name,
            last_build=build.last_build,
            last_exception=build.last_exception,
            last_result=build.last_result,
            traceback=build.traceback,
            url=build.url
        )
        db.session.add(result)
    db.session.commit()
    return 'OK'


@app.route('/getNightly')
def get_nightly_results():
    return flask.jsonify(Result.query.all())


@app.route('/getNightly/<job>')
def get_job_results(job):
    job = Result.query.filter_by(name=job).first()
    return flask.jsonify(job)


@app.route('/<job_name>/traceback')
def get_job_traceback(job_name):
    job = Result.query.filter_by(name=job_name).first()
    if job.traceback:
        return job.traceback.replace('\n', '<br>')
    else:
        return '<h1>No traceback to show<h1>'


@app.route('/test')
def test():
    return 'server is up'


if __name__ == '__main__':
    app.run()
