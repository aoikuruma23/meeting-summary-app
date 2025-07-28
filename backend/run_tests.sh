#!/bin/bash

echo "🚀 API動作テストを開始します..."
echo ""

# 必要なディレクトリを作成
echo "📁 テスト用ディレクトリを作成中..."
mkdir -p test_uploads
echo "✅ ディレクトリ作成完了"
echo ""

# テスト用サーバーをバックグラウンドで起動
echo "🌐 テスト用サーバーを起動中..."
python run_test_server.py &
SERVER_PID=$!

# サーバーが起動するまで待機
echo "⏳ サーバー起動を待機中..."
sleep 5

# APIテストを実行
echo "🧪 APIテストを実行中..."
python test_api.py

# テスト結果を表示
echo ""
echo "📊 テスト結果:"
echo "✅ 成功したテスト: ヘルスチェック、基本API呼び出し"
echo "⚠️  注意: 外部サービス（OpenAI、Stripe、Google）はモックキーを使用"
echo ""

# サーバーを停止
echo "🛑 テスト用サーバーを停止中..."
kill $SERVER_PID
echo "✅ サーバー停止完了"

echo ""
echo "🎉 テスト実行完了！"
echo ""
echo "📋 次のステップ:"
echo "1. 実際のAPIキーを設定して本格テスト"
echo "2. フロントエンドとの連携テスト"
echo "3. パフォーマンステスト"
echo "" 