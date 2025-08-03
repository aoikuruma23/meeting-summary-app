# Google OAuth設定ガイド

このガイドでは、Meeting Summary AppでGoogleログインを有効にするための手順を説明します。

## 前提条件

- Googleアカウントが必要です
- Google Cloud Consoleへのアクセス権限が必要です

## 手順

### 1. Google Cloud Consoleでの設定

#### 1.1 プロジェクトの作成
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. Googleアカウントでログイン
3. 新しいプロジェクトを作成または既存のプロジェクトを選択
   - プロジェクト名: `meeting-summary-app`
   - プロジェクトID: `meeting-summary-app-xxxxx`（自動生成）

#### 1.2 OAuth 2.0クライアントIDの作成
1. 左側のメニューから「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」ボタンをクリック
3. 「OAuth 2.0クライアントID」を選択
4. アプリケーションの種類で「ウェブアプリケーション」を選択
5. 以下の情報を入力：
   - 名前: `Meeting Summary App`
   - 承認済みのJavaScript生成元:
     - `http://localhost:3000`
     - `https://meeting-summary-app.onrender.com`
   - 承認済みのリダイレクトURI:
     - `http://localhost:3000/auth/callback`
     - `https://meeting-summary-app.onrender.com/auth/callback`

#### 1.3 クライアントIDとシークレットの取得
1. 作成後に表示されるクライアントIDとシークレットをコピー
2. これらの情報は後で環境変数に設定します

### 2. 環境変数の設定

#### 2.1 バックエンドの設定
`backend/.env`ファイルを作成し、以下の内容を追加：

```env
# Google OAuth設定
GOOGLE_CLIENT_ID=your-actual-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
```

#### 2.2 フロントエンドの設定
`frontend/.env`ファイルを作成し、以下の内容を追加：

```env
# Google OAuth設定
VITE_GOOGLE_CLIENT_ID=your-actual-google-client-id.apps.googleusercontent.com
```

### 3. 本番環境での設定

#### 3.1 Render.comでの環境変数設定
1. Render.comのダッシュボードにアクセス
2. プロジェクトを選択
3. 「Environment」タブを選択
4. 以下の環境変数を追加：
   - `GOOGLE_CLIENT_ID`: Google Cloud Consoleで取得したクライアントID
   - `GOOGLE_CLIENT_SECRET`: Google Cloud Consoleで取得したシークレット

#### 3.2 フロントエンドの環境変数設定
1. フロントエンドプロジェクトの環境変数に以下を追加：
   - `VITE_GOOGLE_CLIENT_ID`: Google Cloud Consoleで取得したクライアントID

### 4. 動作確認

#### 4.1 ローカル環境でのテスト
1. バックエンドを起動: `cd backend && python main.py`
2. フロントエンドを起動: `cd frontend && npm run dev`
3. ブラウザで `http://localhost:3000` にアクセス
4. 「Googleでログイン」ボタンをクリック
5. Googleアカウントでログイン

#### 4.2 本番環境でのテスト
1. アプリケーションをデプロイ
2. 本番URLにアクセス
3. 「Googleでログイン」ボタンをクリック
4. Googleアカウントでログイン

## トラブルシューティング

### よくある問題

#### 1. "Google OAuth設定が完了していません"エラー
- 環境変数が正しく設定されているか確認
- Google Cloud ConsoleでクライアントIDが正しく作成されているか確認

#### 2. "リダイレクトURIが一致しません"エラー
- Google Cloud Consoleで承認済みリダイレクトURIが正しく設定されているか確認
- 開発環境と本番環境の両方のURIが設定されているか確認

#### 3. "無効なクライアントID"エラー
- クライアントIDが正しくコピーされているか確認
- 環境変数が正しく読み込まれているか確認

### デバッグ方法

#### 1. ログの確認
バックエンドのログで以下の情報を確認：
```
DEBUG: GOOGLE_CLIENT_ID設定確認 - Key exists: True
DEBUG: GOOGLE_CLIENT_ID値: your-actual-google-client-id.apps.googleusercontent.com
```

#### 2. ブラウザの開発者ツール
- Networkタブでリクエストの詳細を確認
- Consoleタブでエラーメッセージを確認

## セキュリティ注意事項

1. **クライアントシークレットの保護**
   - クライアントシークレットは絶対に公開しないでください
   - 環境変数として安全に管理してください

2. **HTTPSの使用**
   - 本番環境では必ずHTTPSを使用してください
   - Google OAuthはHTTPSでのみ動作します

3. **リダイレクトURIの制限**
   - 承認済みリダイレクトURIは必要最小限に制限してください
   - 不正なリダイレクトを防ぐためです

## 参考リンク

- [Google OAuth 2.0 ドキュメント](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) 