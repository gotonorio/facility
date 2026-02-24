
# 公開用ファイルの作成

ファイル構成
```
ホスト（Rocky Linux）
 │
 ├─warehouse （管理組合ホームページ）
 │
 ├─ opt（データ共有領域）
 │      └─ shared_data
 │             ├─ html_data（htmlファイル保存）
 │             └─ image_data（imageファイル保存）
 │ 
 ├─  facility（共有設備・長期修繕計画アプリケーション）
 │       ├─ outputs
 │       │      ├─ html_data（駐車場空き状況図）
 │       │      └─ image_data（長期修繕計画収支グラフ）
 │       └─  docker
 │              ├─ compose.yml
 │              └─ Dockerfile
 │ 
 ├─  nginx（プロキシサーバ）
 │       ├─ compose.yml
 │       └─ conf.d
 │              └─ default.conf

```

- /home/sophiag_master/bulma/opt/shared_data/facility_data/html_data(image_dara)

sophiagardens.orgで配信するファイルは

1. 駐車場利用状況図（最新年月のデータ）
2. 長期修繕計画の収支グラフ

## 設定

### settings.pyの設定

```python
# BASE_DIR はプロジェクトルートに設定
BASE_DIR = Path(__file__).resolve().parent.parent

# html、イメージの保存場所を分ける
HTML_OUTPUT_ROOT = BASE_DIR / "outputs" / "html_data"
IMAGE_OUTPUT_ROOT = BASE_DIR / "outputs" / "image_data"
```

### compose.yml
