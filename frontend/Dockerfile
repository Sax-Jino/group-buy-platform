# 第一階段：構建前端（使用最新 Node.js 20）
FROM node:23-slim AS builder

# 設定工作目錄
WORKDIR /app

# 複製 package.json 和 package-lock.json
COPY package.json package-lock.json ./
RUN npm install

# 複製前端程式碼
COPY . .

# 構建生產環境
RUN npm run build

# 第二階段：提供靜態檔案
FROM nginx:1.27-alpine-slim

# 複製自定義的 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 複製構建後的檔案
COPY --from=builder /app/build /usr/share/nginx/html

# 開放端口
EXPOSE 80

# 啟動 nginx
CMD ["nginx", "-g", "daemon off;"]