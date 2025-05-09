# バス到着情報ダッシュボード 仕様書

**文書バージョン:** 2.0  
**最終更新日:** 2025年5月8日  
**作成者:** MHCP0001

## 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [要件定義](#2-要件定義)
3. [アーキテクチャ設計](#3-アーキテクチャ設計)
4. [データモデル](#4-データモデル)
5. [API仕様](#5-api仕様)
6. [ユーザーインターフェース設計](#6-ユーザーインターフェース設計)
7. [エラーハンドリングとロギング](#7-エラーハンドリングとロギング)
8. [セキュリティ要件](#8-セキュリティ要件)
9. [テスト戦略](#9-テスト戦略)
10. [デプロイメントと運用](#10-デプロイメントと運用)
11. [拡張性と将来計画](#11-拡張性と将来計画)
12. [インストールと設定](#12-インストールと設定)
13. [参考資料](#13-参考資料)

## 1. プロジェクト概要

### 1.1 背景と目的

本プロジェクトは、自宅最寄りのバス停（野崎）発の小田急バスの発車予定時刻と到着予定時刻をリアルタイムで取得し、Webダッシュボードに表示するアプリケーションです。利用者が時間を効率的に管理できるよう、正確かつ直感的なバス運行情報を提供することを目的としています。

### 1.2 対象ユーザー

- 小田急バスを日常的に利用する通勤・通学者
- バス運行情報を確認する必要がある地域住民
- 自宅やオフィスでバス到着情報を常時表示したいユーザー

### 1.3 プロジェクトスコープ

#### 対象とする機能

- 野崎バス停発の小田急バス運行情報のリアルタイム取得と表示
- 主要目的地（三鷹駅、吉祥寺駅、武蔵境駅南口、調布駅北口）へのバス情報表示
- REST APIによるデータ提供
- レスポンシブなWeb UI
- 定期自動更新機能

#### 対象外

- ユーザー認証・認可機能
- バス予約機能
- 経路検索機能
- プッシュ通知機能

## 2. 要件定義

### 2.1 機能要件

#### 2.1.1 データ取得機能

- **小田急バス情報システムからのデータ取得**
  - API経由での取得（第一優先）
    - 小田急バスオープンAPI（存在する場合）からのデータ取得
    - リクエスト間隔：60秒（設定可能）
    - リクエストタイムアウト：10秒
    - リトライ回数：3回（5秒間隔）
  - Webスクレイピングによる取得（代替手段）
    - 小田急バス公式サイトからのデータスクレイピング
    - スクレイピング間隔：120秒（設定可能）
    - ページロードタイムアウト：15秒
    - リトライ回数：2回（10秒間隔）
    - ユーザーエージェント設定：標準的なブラウザ情報

#### 2.1.2 データ表示機能

- **ダッシュボード表示**
  - 全目的地のバス情報一覧表示
  - 目的地ごとの個別表示（タブ切り替え）
  - 表示情報：
    - バス番号
    - 停留所番号
    - 予定発車時刻
    - 予測発車時刻
    - 予定到着時刻
    - 予測到着時刻
    - 発車までの推定時間（分）
    - 次のバスかどうかの表示
    - 遅延状況（定時/遅延/早発）
  - 自動更新機能：30秒ごと（設定可能）
  - 最終更新日時の表示

#### 2.1.3 API機能

- **RESTful API提供**
  - バス情報取得エンドポイント（GET /api/bus-info）
  - システム状態取得エンドポイント（GET /api/system/status）
  - 目的地別バス情報（GET /api/bus-info/{destination}）
  - バス番号別情報（GET /api/bus-info/bus/{bus_number}）
  - JSON形式でのレスポンス
  - CORS対応

### 2.2 非機能要件

#### 2.2.1 パフォーマンス要件

- **レスポンス時間**
  - APIレスポンス：平均500ms以内、最大2秒
  - ページロード：初回3秒以内、キャッシュ利用時1秒以内
  - 同時接続：最大50ユーザー

- **可用性**
  - システム稼働率：99.5%以上
  - 計画的メンテナンス時間を除く
  - データ更新の継続性：ソースシステム障害時も最大24時間は最終取得データを表示

#### 2.2.2 アクセシビリティ要件

- WCAG 2.1 AA準拠
- スクリーンリーダー対応
- キーボードナビゲーション対応
- 高コントラストモード対応

#### 2.2.3 互換性要件

- **ブラウザ対応**
  - Chrome 90以上
  - Firefox 88以上
  - Safari 14以上
  - Edge 90以上
  - モバイルブラウザ（iOS Safari、Android Chrome）

- **デバイス対応**
  - デスクトップPC
  - タブレット
  - スマートフォン
  - 最小画面サイズ：320px幅

## 3. アーキテクチャ設計

### 3.1 システムアーキテクチャ

#### 3.1.1 全体構成

```
┌───────────────┐     ┌──────────────────┐     ┌────────────────┐
│  小田急バス   │     │                  │     │                │
│  情報システム  │◄────┤  バックエンド    │◄────┤  フロントエンド │
└───────────────┘     │  （Flask）       │     │  （HTML/JS）    │
                      └────────┬─────────┘     └────────────────┘
                               │
                      ┌────────▼─────────┐
                      │                  │
                      │  データベース    │
                      │  （SQLite/PG）   │
                      └──────────────────┘
```

#### 3.1.2 コンポーネント説明

- **データ取得コンポーネント**
  - APIクライアント：小田急バスAPIとの通信
  - Webスクレイパー：バス情報サイトからのデータ抽出
  - データ変換器：取得データの標準形式への変換

- **データ保存コンポーネント**
  - データベース：バス情報と履歴データの保存
  - キャッシュ：頻繁にアクセスされるデータのキャッシング

- **APIコンポーネント**
  - RESTfulエンドポイント：クライアント向けデータ提供
  - レート制限：API使用量の制限
  - エラーハンドラ：エラー状態の処理

- **ウェブUIコンポーネント**
  - ダッシュボード：バス情報の視覚的表示
  - 更新マネージャ：自動データ更新の制御

- **スケジューラコンポーネント**
  - タスクスケジューラ：定期的なデータ取得タスクの実行
  - ジョブキュー：非同期タスクの管理

### 3.2 技術スタック

#### 3.2.1 バックエンド

- **プログラミング言語**: Python 3.9+
- **Webフレームワーク**: Flask 2.2+
- **ORM**: SQLAlchemy 1.4+
- **データベース**:
  - 開発環境: SQLite 3.36+
  - 本番環境: PostgreSQL 14+
- **スケジューラ**: APScheduler 3.9+
- **スクレイピング**: BeautifulSoup4 4.10+, Requests 2.27+
- **キャッシュ**: Redis 6.2+ (オプション)
- **WSGI サーバー**: Gunicorn 20.1+

#### 3.2.2 フロントエンド

- **マークアップ**: HTML5, CSS3
- **スタイリング**: Bootstrap 5.1+
- **JavaScript**: ECMAScript 2021
- **ライブラリ**: 
  - jQuery 3.6+ (DOM操作)
  - Chart.js 3.7+ (データ可視化)
  - Moment.js 2.29+ (日時操作)
- **HTTP クライアント**: Axios 0.27+

#### 3.2.3 インフラストラクチャ

- **コンテナ化**: Docker 20.10+, Docker Compose 2.5+
- **Webサーバー**: Nginx 1.21+
- **SSL**: Let's Encrypt
- **監視**: Prometheus + Grafana (オプション)

## 4. データモデル

### 4.1 データベースモデル

#### 4.1.1 バス情報テーブル (BusInfo)

| フィールド名 | データ型 | 説明 | 制約 |
|------------|---------|------|------|
| id | INTEGER | 一意識別子 | PRIMARY KEY, AUTOINCREMENT |
| destination | VARCHAR(50) | 目的地名 | NOT NULL |
| bus_number | VARCHAR(20) | バス番号 | NOT NULL |
| stop_number | VARCHAR(10) | 停留所番号 | NOT NULL |
| scheduled_departure_time | TIME | 予定発車時刻 | NOT NULL |
| predicted_departure_time | TIME | 予測発車時刻 | NULL |
| scheduled_arrival_time | TIME | 予定到着時刻 | NOT NULL |
| predicted_arrival_time | TIME | 予測到着時刻 | NULL |
| is_next_bus | BOOLEAN | 次のバスかどうか | DEFAULT FALSE |
| delay_status | VARCHAR(20) | 遅延状態 | DEFAULT 'UNKNOWN' |
| created_at | TIMESTAMP | 作成日時 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | 更新日時 | DEFAULT CURRENT_TIMESTAMP |

#### 4.1.2 システム状態テーブル (SystemStatus)

| フィールド名 | データ型 | 説明 | 制約 |
|------------|---------|------|------|
| id | INTEGER | 一意識別子 | PRIMARY KEY, AUTOINCREMENT |
| data_source | VARCHAR(20) | データソース（API/Scraping） | NOT NULL |
| last_successful_update | TIMESTAMP | 最終成功更新時刻 | NULL |
| last_failed_update | TIMESTAMP | 最終失敗更新時刻 | NULL |
| failure_count | INTEGER | 連続失敗回数 | DEFAULT 0 |
| health | VARCHAR(20) | システム健全性（OK/WARNING/ERROR） | DEFAULT 'UNKNOWN' |
| created_at | TIMESTAMP | 作成日時 | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | 更新日時 | DEFAULT CURRENT_TIMESTAMP |

#### 4.1.3 データ履歴テーブル (DataHistory)

| フィールド名 | データ型 | 説明 | 制約 |
|------------|---------|------|------|
| id | INTEGER | 一意識別子 | PRIMARY KEY, AUTOINCREMENT |
| data_type | VARCHAR(50) | データタイプ | NOT NULL |
| data_json | TEXT | JSONデータ | NOT NULL |
| source | VARCHAR(20) | データソース | NOT NULL |
| created_at | TIMESTAMP | 作成日時 | DEFAULT CURRENT_TIMESTAMP |

### 4.2 データフロー

1. **データ取得フロー**
   ```
   データソース（API/Web）→ データ取得コンポーネント → データ変換 → データベース保存
   ```

2. **APIリクエストフロー**
   ```
   クライアント → Nginx → Gunicorn → Flask → データベース読取 → JSONレスポンス → クライアント
   ```

3. **更新処理フロー**
   ```
   APScheduler → データ取得タスク起動 → データ更新 → WebSocketイベント → クライアント更新
   ```

## 5. API仕様

### 5.1 RESTful API エンドポイント

#### 5.1.1 全バス情報取得 (GET /api/bus-info)

**概要**: 全目的地のバス情報を取得する

**リクエストパラメータ**:
- なし

**レスポンス**: 200 OK
```json
{
  "update_time": "2025-05-08T12:30:45+09:00",
  "system_status": {
    "data_source": "API",
    "last_successful_update": "2025-05-08T12:30:40+09:00",
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
    {
      "destination": "吉祥寺駅",
      "bus_number": "吉０１",
      "stop_number": "2",
      "scheduled_departure_time": "12:45",
      "predicted_departure_time": "12:47",
      "scheduled_arrival_time": "13:05",
      "predicted_arrival_time": "13:07",
      "estimated_departure_minutes": 16,
      "is_next_bus": false,
      "delay_status": "ON_TIME"
    }
  ]
}
```

**エラーレスポンス**:
- 500 Internal Server Error: サーバー内部エラー
- 503 Service Unavailable: データソースが利用不可

#### 5.1.2 目的地別バス情報取得 (GET /api/bus-info/{destination})

**概要**: 特定の目的地へのバス情報を取得する

**パスパラメータ**:
- destination (string, required): 目的地名（三鷹駅、吉祥寺駅、武蔵境駅南口、調布駅北口）

**リクエストパラメータ**:
- limit (integer, optional): 取得するバスの数（デフォルト: 5）
- offset (integer, optional): スキップするバスの数（デフォルト: 0）

**レスポンス**: 200 OK
```json
{
  "update_time": "2025-05-08T12:30:45+09:00",
  "destination": "三鷹駅",
  "buses": [
    {
      "bus_number": "鷹５２",
      "stop_number": "4",
      "scheduled_departure_time": "12:37",
      "predicted_departure_time": "12:44",
      "scheduled_arrival_time": "12:57",
      "predicted_arrival_time": "13:04",
      "estimated_departure_minutes": 13,
      "is_next_bus": true,
      "delay_status": "DELAYED"
    }
  ],
  "total_buses": 1
}
```

**エラーレスポンス**:
- 400 Bad Request: パラメータ不正
- 404 Not Found: 指定された目的地が存在しない
- 500 Internal Server Error: サーバー内部エラー

#### 5.1.3 システム状態取得 (GET /api/system/status)

**概要**: システムの稼働状態を取得する

**リクエストパラメータ**:
- なし

**レスポンス**: 200 OK
```json
{
  "update_time": "2025-05-08T12:30:45+09:00",
  "data_source": "API",
  "last_successful_update": "2025-05-08T12:30:40+09:00",
  "last_failed_update": null,
  "failure_count": 0,
  "health": "OK",
  "version": "1.0.0",
  "uptime": 86400
}
```

**エラーレスポンス**:
- 500 Internal Server Error: サーバー内部エラー

### 5.2 API利用制限

- レート制限: 1分あたり60リクエスト (IP単位)
- キャッシュ有効期間: 30秒
- タイムアウト: 10秒

## 6. ユーザーインターフェース設計

### 6.1 画面構成

#### 6.1.1 メインダッシュボード

![メインダッシュボード](https://example.com/dashboard.png)

**構成要素**:
- ヘッダー: アプリケーションタイトル、最終更新時刻
- タブナビゲーション: 目的地別タブ（全て、三鷹駅、吉祥寺駅、武蔵境駅南口、調布駅北口）
- バス情報テーブル: 各バスの詳細情報
- フッター: システム状態、バージョン情報

#### 6.1.2 モバイル表示

![モバイル表示](https://example.com/mobile_dashboard.png)

**特徴**:
- 縦長レイアウト
- 縮小されたテーブル
- スワイプ操作による目的地切り替え
- タッチ対応UI

### 6.2 インタラクション設計

#### 6.2.1 更新処理

- 自動更新: 30秒ごとに自動更新（設定可能）
- 手動更新: 更新ボタンをクリックで即時更新
- 更新インジケータ: 更新中は読み込みアニメーション表示
- オフライン検出: ネットワーク切断時に通知

#### 6.2.2 フィルタリングと並べ替え

- 目的地フィルタ: タブによる目的地別表示
- バス番号フィルタ: 特定のバス番号で絞り込み
- 時間順並べ替え: 発車時刻の昇順/降順で並べ替え

#### 6.2.3 視覚的フィードバック

- 遅延状態表示:
  - 定時: 緑色
  - 遅延: 赤色
  - 早発: 黄色
- 次のバス強調表示: 次に到着するバスを強調
- 残り時間の色分け:
  - 5分未満: 赤色
  - 5〜15分: 黄色
  - 15分以上: 緑色

### 6.3 レスポンシブデザイン戦略

- **ブレークポイント**:
  - モバイル: 〜576px
  - タブレット: 577px〜992px
  - デスクトップ: 993px〜
- **コンテンツ適応**:
  - モバイル: 簡略化表示（主要情報のみ）
  - タブレット: 標準表示
  - デスクトップ: 拡張表示（全情報）
- **レイアウト変更**:
  - モバイル: 縦長1列レイアウト
  - タブレット: 2列レイアウト
  - デスクトップ: 多列レイアウト

## 7. エラーハンドリングとロギング

### 7.1 エラー処理戦略

#### 7.1.1 データ取得エラー

- **API接続エラー**:
  - 3回まで再試行（指数バックオフ）
  - スクレイピングへのフォールバック
  - 最終取得データの表示（24時間以内）
- **パース失敗**:
  - エラーログ記録
  - 部分的な正常データの表示
  - エラーカウンター増加
- **タイムアウト**:
  - 15秒を超えるリクエストは中断
  - システム状態の更新

#### 7.1.2 ユーザー向けエラー表示

- **データ取得エラー**:
  - エラーバナー表示
  - 最終更新時刻表示
  - 再試行ボタン提供
- **シンセム障害**:
  - メンテナンスページ表示
  - 代替情報源の案内
  - 予想復旧時間の表示

#### 7.1.3 障害回復機構

- ヘルスチェックによる自動回復
- 定期的な接続試行
- デグレード運転モード（限定機能での運用）

### 7.2 ロギング設計

#### 7.2.1 ログレベル

- **ERROR**: システム障害、データ処理失敗
- **WARNING**: 一時的な問題、パフォーマンス低下
- **INFO**: 通常運用、データ更新、API呼出し
- **DEBUG**: 詳細なデータ処理、開発用情報

#### 7.2.2 ログ出力先

- **ファイル**:
  - 開発環境: ./logs/app.log
  - 本番環境: /var/log/bus-dashboard/app.log
- **コンソール**: 開発環境のみ
- **監視システム**: Prometheus/Grafana（オプション）

#### 7.2.3 ローテーション設計

- ログサイズ: 最大10MB
- 保持期間: 30日
- ローテーション: 日次
- 圧縮: gzip形式

#### 7.2.4 ログフォーマット

```
[TIMESTAMP] [LEVEL] [MODULE] - Message
```

例:
```
[2025-05-08 12:30:45] [INFO] [api.bus_info] - Successfully fetched bus information from API
```

## 8. セキュリティ要件

### 8.1 データセキュリティ

- **転送中のデータ保護**:
  - HTTPS (TLS 1.3)による暗号化
  - 証明書: Let's Encrypt（90日更新）
- **保存データ保護**:
  - センシティブデータの最小化
  - データベースアクセス制限

### 8.2 アクセス制御

- **IPアドレス制限**:
  - 管理APIへのアクセス制限
  - ホワイトリストによるアクセス許可
- **APIアクセス制御**:
  - レート制限: 1分あたり60リクエスト（IP単位）
  - リクエストサイズ制限: 最大1MB

### 8.3 脆弱性対策

- **入力バリデーション**:
  - パラメータ検証
  - SQLインジェクション対策
  - XSS対策
- **依存パッケージ管理**:
  - 定期的な脆弱性スキャン
  - 自動更新の設定（開発環境のみ）
  - 本番環境は計画的更新

### 8.4 インフラセキュリティ

- **コンテナセキュリティ**:
  - 最小権限原則
  - ルートなしコンテナ実行
  - イメージ脆弱性スキャン
- **ネットワークセキュリティ**:
  - 必要なポートのみ公開
  - ファイアウォール設定
  - 内部ネットワークの分離

## 9. テスト戦略

### 9.1 テスト種類

#### 9.1.1 単体テスト

- **対象**: 個別クラス、関数、メソッド
- **フレームワーク**: pytest
- **カバレッジ目標**: コードカバレッジ80%以上
- **自動化**: CI/CDパイプラインで実行

#### 9.1.2 統合テスト

- **対象**: コンポーネント間の連携
- **フレームワーク**: pytest
- **モック利用**: 外部サービスのモック化
- **テストケース**: 主要データフローパス

#### 9.1.3 システムテスト

- **対象**: エンドツーエンドの機能
- **ツール**: Selenium、Cypress
- **テスト環境**: テスト用データベース、モックAPI
- **テスト項目**: ユースケースシナリオ全体

#### 9.1.4 パフォーマンステスト

- **対象**: レスポンス時間、スループット
- **ツール**: Locust
- **シナリオ**: 通常負荷、ピーク負荷
- **測定指標**: 平均応答時間、95パーセンタイル

### 9.2 テスト環境

- **開発環境**
  - ローカル開発マシン
  - SQLiteデータベース
  - モックAPIレスポンス

- **テスト環境**
  - CI/CDパイプライン
  - テスト用PostgreSQL
  - テスト用Webサーバー

- **本番環境**
  - 本番サーバー
  - 本番データベース
  - 本番APIエンドポイント

### 9.3 テスト自動化

- **継続的インテグレーション**:
  - プルリクエスト時の自動テスト実行
  - コードカバレッジレポート生成
  - 静的コード解析

- **回帰テスト**:
  - 主要機能の自動テスト
  - ナイトリービルドでの実行
  - 結果の自動通知

## 10. デプロイメントと運用

### 10.1 デプロイメント戦略

#### 10.1.1 環境設定

- **開発環境**
  - ローカルマシン
  - Docker Compose
  - SQLiteデータベース
  - デバッグモード有効

- **ステージング環境**
  - クラウドインスタンス
  - Docker Compose
  - PostgreSQLデータベース
  - 本番同等設定

- **本番環境**
  - クラウドインスタンス
  - Docker Compose/Kubernetes
  - PostgreSQLデータベース
  - 高可用性設定

#### 10.1.2 デプロイメントプロセス

1. ビルドプロセス:
   - ソースコードのクローン
   - 依存パッケージのインストール
   - 静的ファイルの生成
   - Dockerイメージのビルド

2. テストプロセス:
   - 単体テスト実行
   - 統合テスト実行
   - コードカバレッジ検証
   - セキュリティスキャン

3. デプロイメントプロセス:
   - 新バージョンのデプロイ
   - ヘルスチェック
   - ブルー/グリーンデプロイメント
   - ロールバック手順

### 10.2 監視とアラート

#### 10.2.1 監視指標

- **システム指標**:
  - CPU使用率
  - メモリ使用率
  - ディスク使用率
  - ネットワークトラフィック

- **アプリケーション指標**:
  - リクエスト数/秒
  - レスポンス時間
  - エラー率
  - アクティブセッション数

- **ビジネス指標**:
  - 正常取得データ率
  - データ更新頻度
  - ユーザー利用数

#### 10.2.2 アラート設定

- **重大度レベル**:
  - 重大（Pager Duty）: システム停止、データ取得不能
  - 警告（Eメール）: パフォーマンス低下、遅延増加
  - 情報（ダッシュボード）: 閾値近接、通常外れ値

- **アラートチャネル**:
  - Eメール通知
  - Slack通知
  - SMS通知（重大アラートのみ）

### 10.3 バックアップと復旧

- **データバックアップ**:
  - 日次フルバックアップ
  - 4時間ごとの増分バックアップ
  - 30日間の保持期間

- **復旧プロセス**:
  - ポイントインタイムリカバリ
  - 手動復旧手順ドキュメント
  - 定期的な復旧訓練

## 11. 拡張性と将来計画

### 11.1 スケーラビリティ考慮点

- **水平スケーリング**:
  - ステートレスアーキテクチャ
  - ロードバランサー対応
  - セッション共有機構

- **垂直スケーリング**:
  - リソース要件の明確化
  - パフォーマンスチューニングポイント
  - データベース最適化

### 11.2 将来の機能拡張

- **機能拡張候補**:
  - 複数バス停対応
  - ユーザーアカウント機能
  - お気に入りルート保存
  - プッシュ通知機能
  - 経路検索機能

- **技術拡張候補**:
  - リアルタイムプッシュ更新（WebSocket）
  - PWA対応
  - オフラインモード
  - 多言語対応

### 11.3 メンテナンス計画

- **定期的なメンテナンス**:
  - 月次セキュリティアップデート
  - 四半期ごとの依存パッケージ更新
  - 年次アーキテクチャレビュー

- **技術的負債解消**:
  - コードリファクタリング計画
  - レガシーコンポーネント更新
  - パフォーマンス最適化

## 12. インストールと設定

### 12.1 開発環境セットアップ

#### 12.1.1 前提条件

- Python 3.9以上
- Docker, Docker Compose
- Git

#### 12.1.2 インストール手順

1. リポジトリをクローン
```bash
git clone https://github.com/mhcp0001/bus-arrival-dashboard.git
cd bus-arrival-dashboard
```

2. 仮想環境を作成し、依存関係をインストール
```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install -r requirements.txt
```

3. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集して必要な設定を行う
```

4. 開発サーバーを実行
```bash
python app/main.py
```

5. ブラウザでアクセス
```
http://localhost:5000
```

### 12.2 本番環境デプロイ

#### 12.2.1 Dockerを使用したデプロイ

1. リポジトリをクローン
```bash
git clone https://github.com/mhcp0001/bus-arrival-dashboard.git
cd bus-arrival-dashboard
```

2. 環境変数を設定
```bash
cp .env.example .env.prod
# .env.prodファイルを編集して本番環境設定を行う
```

3. Docker Composeでビルドして実行
```bash
docker-compose -f docker-compose.prod.yml up -d
```

4. ブラウザでアクセス
```
http://localhost
```

#### 12.2.2 SSL設定

1. Nginx設定ファイルを編集
```bash
vim nginx/conf.d/app.conf
```

2. Let's Encryptで証明書を取得
```bash
# certbotコマンドを使用
```

3. SSL設定を有効化し、サービスを再起動
```bash
docker-compose -f docker-compose.prod.yml restart nginx
```

## 13. 参考資料

### 13.1 関連ドキュメント

- [Flask ドキュメント](https://flask.palletsprojects.com/)
- [SQLAlchemy ドキュメント](https://docs.sqlalchemy.org/)
- [APScheduler ドキュメント](https://apscheduler.readthedocs.io/)
- [Bootstrap ドキュメント](https://getbootstrap.com/docs/)

### 13.2 API参考資料

- [小田急バスAPI仕様](https://example.com/odakyu-bus-api)（非公開の場合あり）
- [GTFS仕様](https://developers.google.com/transit/gtfs)

### 13.3 コーディング規約

- [PEP 8 -- Python コーディングスタイルガイド](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

**仕様書バージョン履歴**

- v2.0 (2025-05-08): 完全な仕様書に更新
- v1.0 (2025-05-01): 初版作成