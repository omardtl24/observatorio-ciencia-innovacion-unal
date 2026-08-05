FROM openresty/openresty:1.27.1.1-alpine

RUN apk add --no-cache perl curl gettext
RUN opm get ledgetech/lua-resty-http

COPY nginx_app.conf.template /etc/nginx/templates/nginx.conf.template
COPY lua /etc/nginx/lua

EXPOSE 80 443

CMD envsubst '${NGINX_RESOLVER} ${NGINX_BACKEND_URL} ${NGINX_FRONTEND_URL}' \
    < /etc/nginx/templates/nginx.conf.template \
    > /usr/local/openresty/nginx/conf/nginx.conf \
    && openresty -g 'daemon off;'