#!/bin/bash

# Render環境で日本語フォントをインストールするスクリプト

echo "日本語フォントのインストールを開始します..."

# システムの更新
sudo apt-get update

# 日本語フォントパッケージのインストール
echo "日本語フォントパッケージをインストール中..."
sudo apt-get install -y \
    fonts-ipafont \
    fonts-ipafont-gothic \
    fonts-ipafont-mincho \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-takao-gothic \
    fonts-takao-mincho \
    fonts-vlgothic \
    fonts-umeplus

# フォントキャッシュの更新
echo "フォントキャッシュを更新中..."
sudo fc-cache -fv

# インストールされたフォントの確認
echo "インストールされた日本語フォント:"
fc-list :lang=ja | head -20

echo "日本語フォントのインストールが完了しました。"
