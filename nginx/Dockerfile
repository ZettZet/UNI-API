FROM nginx:1.12.2-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/
COPY /dist/uni-dictionary  /home/front