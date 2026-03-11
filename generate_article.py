#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import re
import string
import unicodedata
from datetime import datetime

import google.generativeai as genai
import requests

# --- 設定 ---
ARTICLES_DIR = "articles"

# --- Gemini API設定 ---
try:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    raise RuntimeError("環境変数 `GEMINI_API_KEY` が設定されていません。")

# --- ヘルパー関数 ---
def slugify(value):
    """記事のスラッグを生成する"""
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"[^a-z0-9\-_]", "", value)
    if len(value) < 12:
        padding = "".join(random.choices(string.ascii_lowercase + string.digits, k=12 - len(value)))
        value = f"{value}-{padding}"
    return value[:50]

def search_topic():
    """Web検索でニッチな技術トピックを見つける（ダミー実装）"""
    # 本来は search ツール等で動的にトピックを取得する
    topics = [
        "Pythonの underrated な標準ライブラリ 'collections.deque'",
        "Rustの 'Turbofish' シンタックスの使いどころ",
        "CSSの新しい擬似クラス ':has()' の実践的活用法",
        "Go言語のジェネリクスを効果的に使うためのパターン",
        "TypeScript 5.2の 'using' 宣言によるリソース管理",
    ]
    return random.choice(topics)

def create_article(topic):
    """Gemini APIを使って記事を生成する"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    あなたは優秀なテクニカルライターです。
    以下のトピックについて、Zenn.devに投稿するための高品質な技術解説記事を日本語のMarkdown形式で生成してください。

    **トピック:** {topic}

    **記事の構成要件:**
    - 読者がすぐに行動できるよう、具体的で実践的なコード例を豊富に含めること。
    - 導入部分で、この記事が解決する課題やメリットを明確に提示すること。
    - ライブラリや機能の基本的な使い方だけでなく、応用的なテクニックやベストプラクティスにも言及すること。
    - 全体の構成は、「導入」「主な特徴」「インストール方法」「基本的な使い方」「実践的なコード例」「まとめ」とすること。
    - ZennのMarkdown仕様に準拠すること。

    それでは、記事の生成を開始してください。
    """
    response = model.generate_content(prompt)
    return response.text

def save_article(content):
    """生成された記事をファイルに保存する"""
    # Markdownからタイトルを抽出
    title_match = re.search(r"^#\s(.+)", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled"

    slug = slugify(title)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{slug}.md"
    filepath = os.path.join(ARTICLES_DIR, filename)

    # Zenn用のフロントマター
    frontmatter = f"""---
title: "{title}"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
published: true
---

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter + content)

    return filepath

# --- メイン処理 ---
if __name__ == "__main__":
    print("1. ニッチな技術トピックを検索中...")
    selected_topic = search_topic()
    print(f"   -> トピック選定: {selected_topic}")

    print("2. AIによる記事生成を開始...")
    article_content = create_article(selected_topic)
    print("   -> 記事生成完了。")

    print("3. 記事をファイルに保存中...")
    saved_path = save_article(article_content)
    print(f"   -> 保存完了: {saved_path}")

    print("\n🎉 全てのプロセスが完了しました！")
