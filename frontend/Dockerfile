# 使用官方 Node.js 16 映像作為基礎
FROM node:16-alpine

# 設定工作目錄
WORKDIR /app

# 複製 package.json 和 package-lock.json
COPY package.json package-lock.json ./
RUN npm install

# 複製前端程式碼
COPY . .

# 構建生產環境
RUN npm run build

# 使用 nginx 提供靜態文件
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html

# 開放端口
EXPOSE 80

# 啟動 nginx
CMD ["nginx", "-g", "daemon off;"]