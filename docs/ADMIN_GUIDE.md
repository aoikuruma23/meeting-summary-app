# 🔧 会議要約アプリ 管理者ガイド

## 🎯 概要

このガイドは、会議要約アプリの管理者向けに、システムの管理、デプロイ、トラブルシューティング方法を説明します。

## 🏗️ システムアーキテクチャ

### 技術スタック
- **Backend**: FastAPI + Python 3.11
- **Frontend**: React + TypeScript + Vite
- **Database**: PostgreSQL (Render)
- **AI Services**: OpenAI Whisper + ChatGPT
- **Payment**: Stripe
- **Hosting**: Render

### システム構成
```
meeting-summary-app/
├── backend/          # FastAPI バックエンド
├── frontend/         # React フロントエンド
├── docs/            # ドキュメント
└── render.yaml      # Render設定
```

## 🚀 デプロイ手順

### 1. 環境準備
```bash
# リポジトリのクローン
git clone https://github.com/aoikuruma23/meeting-summary-app.git
cd meeting-summary-app
```

### 2. 環境変数の設定
```bash
# backend/.env ファイルを作成
cp backend/env.example backend/.env

# 必要な環境変数
OPENAI_API_KEY=your_openai_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
SECRET_KEY=your_secret_key
ENCRYPTION_KEY=your_encryption_key
DATABASE_URL=postgresql://...
```

### 3. Renderでのデプロイ
1. Renderダッシュボードにアクセス
2. 「New Web Service」をクリック
3. GitHubリポジトリを接続
4. 設定を確認:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

### 4. フロントエンドのデプロイ
1. 「New Static Site」をクリック
2. 同じリポジトリを選択
3. 設定を確認:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

## 🔧 システム管理

### データベース管理
```bash
# テーブル作成
python backend/create_tables.py

# データベース状態確認
python backend/check_tables.py

# プレミアムユーザー設定
python backend/fix_render_premium.py
```

### ログ監視
```bash
# Renderログの確認
# Renderダッシュボード → Logs タブ

# 主要ログファイル
backend/logs/
├── app.log          # アプリケーションログ
├── error.log        # エラーログ
└── security.log     # セキュリティログ
```

### パフォーマンス監視
- **API応答時間**: 平均 < 2秒
- **録音処理時間**: 平均 < 30秒
- **要約生成時間**: 平均 < 60秒
- **同時接続数**: 最大100ユーザー

## 🔒 セキュリティ管理

### 認証・認可
- **JWT認証**: 24時間有効期限
- **レート制限**: IPアドレス別制限
- **CORS設定**: 許可されたオリジンのみ

### データ保護
- **音声データ**: AES暗号化
- **要約データ**: データベース保存
- **決済情報**: Stripeで処理

### セキュリティチェックリスト
- [ ] 環境変数の適切な設定
- [ ] APIキーの定期ローテーション
- [ ] セキュリティログの監視
- [ ] 定期的なセキュリティアップデート

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. アプリケーションが起動しない
**症状**: Renderでデプロイ失敗
**原因**: 依存関係の問題
**解決方法**:
```bash
# requirements.txtの確認
pip install -r backend/requirements.txt

# Pythonバージョンの確認
python --version  # 3.11以上が必要
```

#### 2. データベース接続エラー
**症状**: `Database connection failed`
**原因**: DATABASE_URLの設定ミス
**解決方法**:
```bash
# 環境変数の確認
echo $DATABASE_URL

# データベース接続テスト
python backend/check_tables.py
```

#### 3. OpenAI API エラー
**症状**: `RateLimitError` または `InvalidAPIKey`
**原因**: APIキーの問題
**解決方法**:
```bash
# APIキーの確認
echo $OPENAI_API_KEY

# キーの長さ確認（51文字である必要）
echo ${#OPENAI_API_KEY}
```

#### 4. フロントエンドが表示されない
**症状**: 404エラー
**原因**: ビルド設定の問題
**解決方法**:
```bash
# フロントエンドビルドの確認
cd frontend
npm install
npm run build

# distフォルダの確認
ls -la dist/
```

#### 5. 録音機能が動作しない
**症状**: マイクが認識されない
**原因**: HTTPS設定の問題
**解決方法**:
- HTTPS証明書の確認
- ブラウザの権限設定確認

## 📊 監視・メトリクス

### 重要なメトリクス
- **稼働率**: 99.9%以上
- **応答時間**: API平均 < 2秒
- **エラー率**: < 1%
- **同時ユーザー数**: 最大100

### 監視ツール
- **Render**: 基本的な監視
- **ログ分析**: エラーパターンの特定
- **パフォーマンス**: 応答時間の監視

## 🔄 バックアップ・復旧

### データベースバックアップ
```bash
# PostgreSQLバックアップ
pg_dump $DATABASE_URL > backup.sql

# 復元
psql $DATABASE_URL < backup.sql
```

### ファイルバックアップ
- **音声ファイル**: 暗号化して保存
- **設定ファイル**: バージョン管理
- **ログファイル**: 定期的なアーカイブ

## 🚀 スケーリング

### 水平スケーリング
- **ロードバランサー**: 複数インスタンス
- **データベース**: 読み取りレプリカ
- **キャッシュ**: Redis導入

### 垂直スケーリング
- **メモリ増加**: Renderプランアップグレード
- **CPU増加**: より高性能なインスタンス

## 📞 サポート・連絡先

### 緊急時連絡先
- **技術サポート**: tech@meeting-summary-app.com
- **緊急時**: +81-XX-XXXX-XXXX
- **Slack**: #meeting-summary-support

### エスカレーション手順
1. 初期対応（30分以内）
2. 技術チーム連絡（1時間以内）
3. 緊急対応（2時間以内）

## 📋 定期メンテナンス

### 日次タスク
- [ ] ログの確認
- [ ] エラー率のチェック
- [ ] パフォーマンス監視

### 週次タスク
- [ ] セキュリティログの分析
- [ ] バックアップの確認
- [ ] 依存関係の更新確認

### 月次タスク
- [ ] セキュリティアップデート
- [ ] パフォーマンス最適化
- [ ] ドキュメントの更新

---

**© 2024 Meeting Summary App. All rights reserved.** 