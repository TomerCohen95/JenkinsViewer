FROM python:3.8
COPY . /app
RUN ls /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD python manage.py runserver --host 0.0.0.0
