FROM debian:bookworm-slim

RUN apt update -y && apt install nginx -y \
	&& apt clean && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY index.html /var/www/html/index.html

RUN chown www-data:www-data /var/www/html/index.html \
	&& chmod 644 /var/www/html/index.html

CMD ["nginx", "-g", "daemon off;"]
