# Supabase移行ガイド

## 1. Supabaseプロジェクト作成

1. **Supabaseにアクセス**: https://supabase.com
2. **新規プロジェクト作成**:
   - プロジェクト名: `meeting-summary-app`
   - データベースパスワード: 強力なパスワードを設定
   - リージョン: `Asia Northeast (Tokyo)`

## 2. 接続情報の取得

1. **Supabaseダッシュボード** → **Settings** → **Database**
2. **Connection string** をコピー
3. **Connection pooling** の設定も確認

## 3. 環境変数の設定

### ローカル開発環境
```bash
# .env ファイルに追加
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### 本番環境（Render）
```bash
# Render環境変数に設定
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

## 4. 移行実行

```bash
# 1. 依存関係のインストール
pip install -r requirements.txt

# 2. データベース接続テスト
python setup_supabase.py

# 3. アプリケーション起動
python main.py
```

## 5. 既存データの移行（必要に応じて）

### データエクスポート（旧DB）
```bash
# PostgreSQLの場合
pg_dump [OLD_DATABASE_URL] > backup.sql
```

### データインポート（Supabase）
```bash
# Supabaseにインポート
psql [SUPABASE_DATABASE_URL] < backup.sql
```

## 6. パフォーマンス設定

### Supabase接続プール設定
- **Pool Size**: 20接続
- **Max Overflow**: 30接続
- **Total Max**: 50接続
- **Pre-ping**: 有効
- **Recycle**: 1時間

### 監視項目
- 接続数
- クエリ実行時間
- エラー率
- レスポンス時間

## 7. トラブルシューティング

### 接続エラー
```bash
# 接続テスト
python -c "from app.core.database import engine; print(engine.execute('SELECT 1').fetchone())"
```

### 権限エラー
- Supabaseダッシュボードでテーブル権限を確認
- RLS（Row Level Security）の設定を確認

### パフォーマンス問題
- 接続プール設定を調整
- インデックスの追加を検討
- クエリの最適化

## 8. 本番環境での注意点

1. **セキュリティ**:
   - RLS（Row Level Security）を有効化
   - APIキーの適切な管理
   - 接続文字列の暗号化

2. **監視**:
   - Supabaseダッシュボードでメトリクス監視
   - アラート設定
   - ログ監視

3. **バックアップ**:
   - 自動バックアップの確認
   - 復旧手順の準備
   - データ移行計画

## 9. 移行後の確認項目

- [ ] ユーザー登録・ログイン
- [ ] 録音機能
- [ ] 要約生成
- [ ] 決済処理
- [ ] ファイルアップロード
- [ ] 履歴表示
- [ ] エクスポート機能
