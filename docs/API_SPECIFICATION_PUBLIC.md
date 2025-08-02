# 🔌 会議要約アプリ API仕様書（公開版）

## 🎯 概要

会議要約アプリのRESTful API仕様書です。開発者向けにAPIの使用方法を説明しています。

## 🔐 認証

### JWT認証
すべてのAPIエンドポイント（`/auth/*`を除く）はJWT認証が必要です。

```http
Authorization: Bearer <jwt_token>
```

### トークン取得
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

**レスポンス**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "is_premium": true
  }
}
```

## 📡 API エンドポイント

### 認証関連

#### ログイン
```http
POST /auth/login
```

**リクエスト**:
```json
{
  "email": "string",
  "password": "string"
}
```

**レスポンス**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "integer",
    "email": "string",
    "name": "string",
    "is_premium": "boolean"
  }
}
```

#### ダミーログイン
```http
POST /auth/dummy-login
```

**レスポンス**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "dummy@example.com",
    "name": "テストユーザー",
    "is_premium": false
  }
}
```

### 録音関連

#### 録音開始
```http
POST /api/recording/start
Authorization: Bearer <token>
Content-Type: application/json
```

**リクエスト**:
```json
{
  "title": "会議タイトル",
  "participants": "参加者1,参加者2,参加者3"
}
```

**レスポンス**:
```json
{
  "meeting_id": 1,
  "status": "recording",
  "message": "録音を開始しました"
}
```

#### 録音停止
```http
POST /api/recording/stop/{meeting_id}
Authorization: Bearer <token>
```

**レスポンス**:
```json
{
  "meeting_id": 1,
  "status": "processing",
  "message": "録音を停止しました。要約を生成中..."
}
```

#### 録音一覧取得
```http
GET /api/recording/list
Authorization: Bearer <token>
```

**レスポンス**:
```json
{
  "recordings": [
    {
      "id": 1,
      "title": "会議タイトル",
      "participants": "参加者1,参加者2",
      "created_at": "2024-12-01T10:00:00Z",
      "duration": 1800,
      "status": "completed",
      "summary": "要約テキスト..."
    }
  ]
}
```

#### 録音詳細取得
```http
GET /api/recording/{meeting_id}
Authorization: Bearer <token>
```

**レスポンス**:
```json
{
  "id": 1,
  "title": "会議タイトル",
  "participants": "参加者1,参加者2",
  "created_at": "2024-12-01T10:00:00Z",
  "duration": 1800,
  "status": "completed",
  "summary": "要約テキスト...",
  "transcription": "文字起こしテキスト..."
}
```

#### 要約取得
```http
GET /api/recording/summary/{meeting_id}
Authorization: Bearer <token>
```

**レスポンス**:
```json
{
  "meeting_id": 1,
  "summary": "要約テキスト...",
  "created_at": "2024-12-01T10:30:00Z"
}
```

#### 要約エクスポート（PDF）
```http
GET /api/recording/export/{meeting_id}/pdf
Authorization: Bearer <token>
```

**レスポンス**: PDFファイル（バイナリ）

#### 要約エクスポート（Word）
```http
GET /api/recording/export/{meeting_id}/word
Authorization: Bearer <token>
```

**レスポンス**: Wordファイル（バイナリ）

### 課金関連

#### サブスクリプション状態取得
```http
GET /api/billing/subscription-status
Authorization: Bearer <token>
```

**レスポンス**:
```json
{
  "status": "premium",
  "plan": "premium",
  "current_period_end": "2024-12-31T23:59:59Z",
  "cancel_at_period_end": false
}
```

#### チェックアウトセッション作成
```http
POST /api/billing/create-checkout-session
Authorization: Bearer <token>
Content-Type: application/json
```

**リクエスト**:
```json
{
  "price_id": "price_1234567890"
}
```

**レスポンス**:
```json
{
  "session_id": "cs_test_1234567890",
  "url": "https://checkout.stripe.com/pay/cs_test_..."
}
```

#### カスタマーポータルセッション作成
```http
POST /api/billing/create-portal-session
Authorization: Bearer <token>
```

**レスポンス**:
```json
{
  "url": "https://billing.stripe.com/session/..."
}
```

## 📊 データモデル

### User
```json
{
  "id": "integer",
  "email": "string",
  "name": "string",
  "is_premium": "boolean",
  "stripe_customer_id": "string",
  "stripe_subscription_id": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Meeting
```json
{
  "id": "integer",
  "user_id": "integer",
  "title": "string",
  "participants": "string",
  "status": "string",
  "duration": "integer",
  "summary": "string",
  "transcription": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 🔒 セキュリティ

### レート制限
- **認証エンドポイント**: 5回/分
- **録音エンドポイント**: 10回/分
- **その他**: 100回/分

### CORS設定
許可されたオリジンのみアクセス可能です。

### 入力検証
- **文字列**: 最大1000文字
- **ファイルサイズ**: 最大100MB
- **録音時間**: 無料版30分、プレミアム版2時間

## 🐛 エラーレスポンス

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "errors": [
    {
      "field": "title",
      "message": "Title is required"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Premium feature. Please upgrade your plan."
}
```

### 404 Not Found
```json
{
  "detail": "Meeting not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## 📈 パフォーマンス

### 応答時間目標
- **GET リクエスト**: < 500ms
- **POST リクエスト**: < 1秒
- **ファイルアップロード**: < 30秒
- **要約生成**: < 60秒

### 同時接続数
- **最大同時ユーザー**: 100
- **最大同時録音**: 50

## 🔧 開発・テスト

### ローカル開発
```bash
# バックエンド起動
cd backend
python main.py

# フロントエンド起動
cd frontend
npm run dev
```

### APIテスト
```bash
# テスト実行
python -m pytest backend/tests/

# 特定のテスト
python -m pytest backend/tests/test_auth.py
```

## 📞 サポート

### APIサポート
- **メール**: jibunkaikakulab@gmail.com
- **LINE**: [@meeting-summary-app](https://lin.ee/HQWdapv)
- **GitHub**: https://github.com/aoikuruma23/meeting-summary-app

### 制限事項
- **API呼び出し制限**: 1000回/日（無料版）
- **ファイルサイズ制限**: 100MB
- **同時接続制限**: 10（無料版）

---

**© 2024 Meeting Summary App. All rights reserved.** 