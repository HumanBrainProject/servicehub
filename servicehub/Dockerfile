FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY servicehub .

EXPOSE 8080

CMD [ "python", "app.py" ]
