# T-5.2: sirve el frontend estatico (app/frontend/public) con nginx.
FROM nginx:alpine
COPY app/frontend/public /usr/share/nginx/html
EXPOSE 80
