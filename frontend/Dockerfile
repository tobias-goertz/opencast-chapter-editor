# build stage
FROM node:lts-alpine as frontend-build-stage
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN yarn --pure-lockfile
RUN yarn build

# production stage
FROM nginx:stable-alpine as frontend-production-stage
COPY --from=frontend-build-stage /app/dist /usr/share/nginx/html
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
