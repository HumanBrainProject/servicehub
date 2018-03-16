FROM python:slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY servicehub servicehub
COPY servicehub.conf ./

EXPOSE 8080

CMD [ "python", "servicehub/run.py" ]
