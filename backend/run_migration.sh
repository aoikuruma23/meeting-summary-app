#!/bin/bash

echo "データベースマイグレーションを実行します..."
cd backend
python run_migration.py

if [ $? -eq 0 ]; then
    echo "✅ マイグレーションが正常に完了しました"
else
    echo "❌ マイグレーションに失敗しました"
    exit 1
fi 