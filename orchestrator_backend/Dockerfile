FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
RUN npm rebuild sqlite3
COPY . .
CMD [ "node", "server.js" ]
