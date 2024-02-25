# Use a Node.js base image
FROM node:14

WORKDIR /app

COPY /app/package*.json .

RUN npm install && sleep 5

COPY /app .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]