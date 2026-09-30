# SAMS Frontend Dockerfile - Multi-stage build
# Stage 1: Development (hot reload)
FROM node:20-alpine AS development

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]

# Stage 2: Build for production
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --production=false

COPY . .
RUN npm run build

# Stage 3: Production - serve via Nginx (nhẹ hơn)
# Hoặc mount dist/ vào shared volume cho nginx service
FROM node:20-alpine AS production

WORKDIR /app
COPY --from=builder /app/dist ./dist

# Dùng serve package nhẹ để host static files nếu cần
RUN npm install -g serve

EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
