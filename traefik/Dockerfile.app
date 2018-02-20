FROM node:argon

WORKDIR /

RUN npm install -g http-server

EXPOSE 8080

CMD echo "USER:$USER COLLAB:$COLLAB" > index.html && http-server
