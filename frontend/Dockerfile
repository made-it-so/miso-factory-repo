FROM nginx:1.27.0-alpine

# Copy the static website files
COPY ./public/ /usr/share/nginx/html

# Add our new proxy configuration
COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
