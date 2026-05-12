FROM openresty/openresty:1.27.1.1-alpine

RUN apk add --no-cache perl curl
RUN opm get ledgetech/lua-resty-http

COPY nginx_app.conf.template /usr/local/openresty/nginx/conf/nginx.conf
COPY lua /etc/nginx/lua

EXPOSE 80

CMD ["openresty", "-g", "daemon off;"]
