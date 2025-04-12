# 團購平台

這是一個基於 Flask 和 React 的團購平台，支援商品管理、訂單處理、退款、結算、協作提案等功能。

## 功能概覽
- **後端**: 使用 Flask 提供 RESTful API，包含用戶認證、商品管理、訂單、結算、協作等模組。
- **前端**: 使用 React 實現響應式界面，包括首頁、商品列表、訂單管理、個人資料和協作頁面。
- **資料庫**: 使用 SQLAlchemy ORM 與 PostgreSQL，支持遷移。
- **即時通訊**: 使用 Flask-SocketIO 實現協作聊天功能。
- **定時任務**: 使用 schedule 模組處理結算和備份。
- **通知**: 整合 LINE Notify 發送通知。

## 安裝與運行

### 前置條件
- Python 3.8+
- Node.js 16+
- PostgreSQL

### 後端設置
1. 克隆專案：
   ```bash
   git clone <repository-url>
   cd <repository-folder>