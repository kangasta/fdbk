FROM node:lts-alpine as build

RUN apk add git
WORKDIR /app

RUN git clone https://github.com/kangasta/fdbk-data-display.git
WORKDIR /app/fdbk-data-display
RUN export TAG=$(git name-rev --tags --name-only $(git rev-parse HEAD)) && \
    export TAG=$(test $TAG != undefined && echo $TAG || echo '') && \
    echo "TAG=$TAG" > ".env" && \
    echo "COMMIT=$(git rev-parse HEAD)" >> ".env"
RUN npm i && \
    npm run build


FROM nginx:alpine

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/fdbk-data-display/dist /app
COPY ./config.js /app/config.js
