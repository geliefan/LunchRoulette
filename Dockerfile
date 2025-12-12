# Lunch Roulette Dockerfile
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新と必要なツールのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係ファイルをコピー
COPY requirements.txt .

# Pythonパッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY src/ ./src/
COPY run.py .

# データベース用のディレクトリを作成
RUN mkdir -p /app/data

# 非rootユーザーでの実行（セキュリティ向上）
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# ポート5000を公開
EXPOSE 5000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

# アプリケーション起動
CMD ["python", "run.py"]
