# Exchanges Manager

暗号通貨取引所との連携を管理するシステム

## 機能

- 複数取引所のアクセストークン管理
- APIレート制限の実装
- Redisを使用したキャッシュ管理
- ロギングシステム
- YAML形式での設定管理

## セットアップ

1. 必要な依存関係のインストール
```bash
pip install -r requirements.txt
```

2. 設定ファイルの準備
- `src/config/settings.yml` を設定

3. Redisサーバーの起動

4. アプリケーションの実行

## ディレクトリ構造

```
src/
├── config/         # 設定ファイル
├── core/           # コア機能
├── documentation/  # ドキュメント
├── logs/          # ログファイル
├── test/          # テストコード
└── utilities/     # ユーティリティ機能