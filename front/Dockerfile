FROM node:22.12.0 as build-stage

WORKDIR /root/frontend

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 8080

CMD ["npm", "run", "dev"]