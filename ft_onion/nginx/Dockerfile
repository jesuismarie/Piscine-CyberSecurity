FROM debian:bullseye-slim

RUN apt update -y && apt install nginx \
	&& rm -rf /var/lib/apt/lists/*

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

COPY nginx/index.html /var/www/html/index.html

RUN chown -R nginx:nginx /usr/share/nginx/html \
	&& chmod -R 644 /usr/share/nginx/html/*

RUN chown www-data:www-data /var/www/html/index.html \
	&& chmod 644 /var/www/html/index.html
