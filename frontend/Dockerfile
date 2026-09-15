# Multi-stage: build the SPA with Node, serve it with nginx which also
# reverse-proxies /api to the backend and injects the API key.
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
# Config is rendered from a template at start so API_KEY / API_UPSTREAM come
# from the environment (Kubernetes Secret / compose) rather than being baked in.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
