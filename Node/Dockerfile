FROM node:16-alpine3.11


RUN mkdir shared

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .


ENV PORT=8080

EXPOSE 8080

CMD ["npm","start"]


