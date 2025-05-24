# 團購平台系統

這是一個基於 Python Flask 後端和 React 前端的現代化團購平台系統。本系統支援多角色團購管理、訂單處理、金流整合、物流追蹤及互動式協作等功能。

## 功能特色

### 用戶管理
- 多角色支援 (會員、團媽、供應商、管理員)
- 團媽分級制度 (小團媽、中團媽、大團媽)
- 完整的權限控管機制

### 商品管理
- 多樣化商品分類
- 動態庫存管理
- SEO最佳化商品頁面
- 客製化風格版面

### 訂單系統
- 靈活的購物車功能
- 多元支付方式整合
- 即時訂單狀態追蹤
- 自動化分潤計算

### 互動功能
- 商品評價系統
- 即時聊天功能
- 團購直播支援
- 許願池系統

### 結算系統
- 自動化對帳系統
- 多層級分潤機制
- 完整的財務報表
- 退換貨流程管理

## 技術架構

### 後端架構
- 框架: Flask
- 資料庫: PostgreSQL
- ORM: SQLAlchemy
- 認證: JWT
- 即時通訊: Flask-SocketIO
- 工作排程: APScheduler

### 前端架構
- 框架: React
- 狀態管理: Redux
- UI庫: Ant Design
- 路由: React Router
- 即時通訊: Socket.IO-client

### 部署架構
- 容器化: Docker
- 多容器管理: Docker Compose
- 資料持久化: Docker Volumes
- Nginx反向代理

## 安裝與設定

### 系統需求
- Python 3.8+
- Node.js 14+
- PostgreSQL 13+
- Docker & Docker Compose

### 環境設定

1. 複製環境變數範本:
```bash
cp .env.example .env
```

2. 設定環境變數:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://postgres:password@db:5432/groupbuy_db
CORS_ORIGINS=http://localhost:3000
```

### 啟動服務

使用 Docker Compose:
```bash
docker-compose up -d
```

手動啟動:
```bash
# 後端
cd backend
pip install -r requirements.txt
flask db upgrade
flask run

# 前端
cd frontend
npm install
npm start
```

## API文件

API文件使用 OpenAPI (Swagger) 規格撰寫，可透過以下方式查看:

1. 開發環境: http://localhost:5000/api/docs
2. 專案根目錄: /docs/api.md

## 開發指南

### 程式碼風格
- 後端遵循 PEP 8 規範
- 前端遵循 Airbnb JavaScript Style Guide

### Git Workflow
1. 建立新分支: `git checkout -b feature/your-feature`
2. 提交變更: `git commit -m "feat: your feature description"`
3. 發起 Pull Request 到 develop 分支

### 測試
```bash
# 後端測試
cd backend
pytest

# 前端測試
cd frontend
npm test
```

## 專案結構

```
group-buy-platform/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── public/
│   └── package.json
├── docs/
└── docker-compose.yml
```

## 待優化項目

1. 安全性改進
   - 實作 rate limiting
   - 加強 input validation
   - 改善密碼策略

2. 架構優化
   - 實作 API 版本控制
   - 改善錯誤處理機制
   - 加強服務層分離

3. 效能優化
   - 實作快取機制
   - 優化資料庫查詢
   - 加入 CDN 支援

4. 功能擴充
   - 增加數據分析功能
   - 擴充報表系統
   - 優化會員等級制度

## 貢獻指南

1. Fork 專案
2. 建立功能分支
3. 提交程式碼
4. 發起 Pull Request

## 授權條款

本專案採用 MIT 授權條款 - 詳情請見 [LICENSE](LICENSE) 檔案

## 聯絡資訊

如有任何問題或建議，請聯繫專案維護者:
- Email: contact@groupbuy-platform.com
- GitHub Issues