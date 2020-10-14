# JenkinsViewer

How to run jenkins-viewer
```bash
git clone https://github.com/TomerCohen95/JenkinsViewer.git
cd JenkinsViewer
```
edit .env file to enter JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD and JOBS_FOLDER
```bash
docker-compose up --build
docker-compose exec web python manage.py db init
docker-compose exec web python manage.py db migrate
docker-compose exec web python manage.py db upgrade
```
