FROM node:20-alpine AS build
WORKDIR /app

RUN apk add --no-cache ca-certificates
COPY avg-ca.crt* /usr/local/share/ca-certificates/
RUN update-ca-certificates || true
ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt

COPY package*.json ./
RUN npm install

COPY . .
ARG VITE_API_BASE_URL=http://localhost:8420
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
