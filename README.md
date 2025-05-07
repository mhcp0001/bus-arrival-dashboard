# 自宅最寄バス停リアルタイム到着情報ダッシュボード

バス停（野崎）発の小田急バスの発車予定時刻と到着予定時刻をリアルタイムで取得し、Webダッシュボードに表示するアプリケーションです。

## 機能

- 小田急バス情報システムからデータを取得（API優先、スクレイピングは代替手段）
- 各目的地（三鷹駅、吉祥寺駅、武蔵境駅南口、調布駅北口）ごとのバス情報を表示
- REST APIによるデータ提供
- レスポンシブなフロントエンドダッシュボード
- 定期自動更新機能
- エラーハンドリングとロギング機能

## 技術スタック

- バックエンド: Python, Flask
- データベース: SQLite (開発環境), PostgreSQL (本番環境オプション)
- フロントエンド: HTML, CSS, JavaScript
- スケジューラ: APScheduler
- コンテナ化: Docker, Docker Compose
- Webサーバー: Nginx, Gunicorn

## セットアップ

### 開発環境

1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/bus-arrival-dashboard.git
cd bus-arrival-dashboard
```

2. 仮想環境を作成し、依存関係をインストール
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 開発サーバーを実行
```bash
python app/main.py
```

4. ブラウザで http://localhost:5000 にアクセス

### Docker環境

1. リポジトリをクローン
```bash
git clone https://github.com/yourusername/bus-arrival-dashboard.git
cd bus-arrival-dashboard
```

2. Docker Composeでビルドして実行
```bash
docker-compose up -d
```

3. ブラウザで http://localhost にアクセス

## プロジェクト構造

```
bus-arrival-dashboard/
├── app/                        # アプリケーションコード
│   ├── api/                    # API エンドポイント
│   ├── models/                 # データベースモデル
│   ├── services/               # サービス層（データ取得など）
│   ├── static/                 # 静的ファイル（CSS, JS）
│   ├── templates/              # HTML テンプレート
│   ├── tests/                  # テストコード
│   ├── utils/                  # ユーティリティ関数
│   ├── __init__.py            # アプリケーション初期化
│   └── main.py                # アプリケーションエントリーポイント
├── data/                       # データファイル（SQLite DBなど）
├── logs/                       # ログファイル
├── nginx/                      # Nginx設定
│   ├── conf.d/                 # サイト設定
│   └── ssl/                    # SSL証明書
├── .gitignore
├── docker-compose.yml         # Docker Compose設定
├── Dockerfile                 # Dockerファイル
├── requirements.txt           # Pythonパッケージ一覧
├── README.md
└── wsgi.py                    # WSGI エントリーポイント
```

## API仕様

### バス情報取得

```
GET /api/bus-info
```

レスポンス例:
```json
{
  "update_time": "2025-05-08 12:30:45",
  "system_status": {
    "data_source": "API",
    "last_successful_update": "2025-05-08 12:30:40",
    "health": "OK"
  },
  "destinations": [
    {
      "destination": "三鷹駅",
      "bus_number": "鷹５２",
      "stop_number": "4",
      "scheduled_departure_time": "12:37",
      "predicted_departure_time": "12:44",
      "scheduled_arrival_time": "12:57",
      "predicted_arrival_time": "13:04",
      "estimated_departure_minutes": 13,
      "is_next_bus": true,
      "delay_status": "DELAYED"
    },
    // 他の目的地
  ]
}
```

## ライセンス

MIT License