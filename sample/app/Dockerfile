FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY echoheaders .

EXPOSE 8080

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
