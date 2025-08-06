# 本番環境移行ガイド

## 1. Stripe本番環境の設定

### A. Stripeダッシュボードでの設定

1. **Stripeダッシュボードにログイン**
2. **本番キーの取得**：
   - ダッシュボード → 開発者 → APIキー
   - 本番キーをコピー：
     - `pk_live_...` (本番用公開キー)
     - `sk_live_...` (本番用秘密キー)

3. **Webhook設定**：
   - ダッシュボード → 開発者 → Webhook
   - 「エンドポイントを追加」をクリック
   - URL: `https://meeting-summary-app-backend.onrender.com/api/billing/webhook`
   - イベントを選択：
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
   - Webhookシークレットをコピー（`whsec_...`）

### B. Render環境変数の更新

1. **Renderダッシュボードにアクセス**
2. **meeting-summary-app-backend**サービスを選択
3. **Environment**タブで以下の変数を更新：

```
STRIPE_SECRET_KEY=sk_live_... (本番用秘密キー)
STRIPE_PUBLISHABLE_KEY=pk_live_... (本番用公開キー)
STRIPE_WEBHOOK_SECRET=whsec_... (本番用Webhookシークレット)
```

## 2. セキュリティ設定の強化

### A. 本番用の秘密鍵の生成

```bash
# 本番用のSECRET_KEYを生成
openssl rand -hex 32
```

### B. 暗号化キーの更新

```bash
# 本番用のENCRYPTION_KEYを生成
openssl rand -hex 32
```

### C. Render環境変数の追加更新

```
SECRET_KEY=生成した本番用秘密鍵
ENCRYPTION_KEY=生成した本番用暗号化キー
DEBUG=False
```

## 3. データベースの準備

### A. 本番データベースの確認

- RenderのPostgreSQLデータベースが正常に動作していることを確認
- データベース接続文字列が正しく設定されていることを確認

### B. テーブルの作成確認

```sql
-- 本番データベースでテーブルが存在することを確認
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

## 4. フロントエンドの設定

### A. 本番URLの確認

- フロントエンドが正しい本番バックエンドURLを使用していることを確認
- CORS設定が本番ドメインを含んでいることを確認

### B. Google OAuth設定の更新

1. **Google Cloud Console**で本番ドメインを追加：
   - 承認済みリダイレクトURI: `https://meeting-summary-app.onrender.com/auth/callback`

## 5. テスト手順

### A. 基本機能のテスト

1. **ユーザー登録/ログイン**
2. **録音機能**
3. **要約生成**
4. **PDF/Word出力**

### B. 課金機能のテスト

1. **プレミアムプラン購入**
2. **サブスクリプション管理**
3. **Webhook処理**

## 6. 監視とログ

### A. ログの確認

```bash
# Renderダッシュボードでログを確認
# エラーや警告がないことを確認
```

### B. パフォーマンス監視

- レスポンス時間の確認
- エラー率の監視
- リソース使用量の確認

## 7. バックアップ戦略

### A. データベースバックアップ

- Renderの自動バックアップが有効になっていることを確認
- 手動バックアップの手順を文書化

### B. ファイルバックアップ

- アップロードされた音声ファイルのバックアップ戦略を検討
- エクスポートファイルの保存期間を設定

## 8. トラブルシューティング

### よくある問題と解決方法

1. **Webhookエラー**：
   - StripeダッシュボードでWebhook設定を確認
   - エンドポイントURLが正しいことを確認

2. **認証エラー**：
   - Google OAuth設定を確認
   - 本番ドメインが承認済みリダイレクトURIに含まれていることを確認

3. **ファイル出力エラー**：
   - ファイル権限を確認
   - ディスク容量を確認

## 9. 本番移行チェックリスト

- [ ] Stripe本番キーの設定
- [ ] Webhook設定の完了
- [ ] 環境変数の更新
- [ ] セキュリティ設定の強化
- [ ] データベースの準備
- [ ] フロントエンド設定の確認
- [ ] 基本機能のテスト
- [ ] 課金機能のテスト
- [ ] ログと監視の設定
- [ ] バックアップ戦略の確認

## 10. 運用開始後の注意事項

1. **定期的な監視**：
   - ログの確認
   - パフォーマンスの監視
   - エラー率の確認

2. **セキュリティの維持**：
   - 定期的な秘密鍵の更新
   - アクセスログの確認
   - 脆弱性の監視

3. **バックアップの確認**：
   - データベースバックアップの確認
   - ファイルバックアップの確認

4. **ユーザーサポート**：
   - サポート体制の整備
   - よくある質問の整理
   - トラブルシューティングガイドの準備 