
# facility

## 公開用ファイルについて

🔳 ファイル構成
```
ホスト（Rocky Linux）
 │
 ├─warehouse （管理組合ホームページ）
 │
 ├─ opt（データ共有領域。shared_data/まであらかじめ手動で作成しておく）
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

🔳 compose.ymlのマウント設定

- ホスト共有の公開用ディレクトリは /home/sophiag_master/bulma/opt/shared_data/
    - あらかじめ mkdir しておくこと。
- 公開用ディレクトリをコンテナの /code/outputs/ にマウントする。
    - /code は Dockerfileで作成しておく。

```
    volumes:
      - ../static:/code/static
      - ../fac.sqlite3:/code/fac.sqlite3
      - /home/sophiag_master/bulma/opt/shared_data:/code/outputs

```

🔳 settings.pyの設定

```
# BASE_DIR はプロジェクトルートに設定
BASE_DIR = Path(__file__).resolve().parent.parent

# html、イメージの保存場所を分ける
HTML_OUTPUT_ROOT = BASE_DIR / "outputs" / "html_data"
IMAGE_OUTPUT_ROOT = BASE_DIR / "outputs" / "image_data"
```

🔳 nginxの配信設定

- nginx 公開ディレクトリはデフォルトでは /usr/share/nginx/html になっている。

```
default.conf でドメインサーバに以下の設定をしておくことで、
http://sophiagardens.org/html_data/htmlファイル名」でアクセスできる。
add_headerはキャッシュ禁止のため

    location /html_data/ {
        alias /usr/share/nginx/html/html_data/;
        add_header Cache-Control "no-cache, must-revalidate";
    }
    location /image_data/ {
        alias /usr/share/nginx/html/image_data/;
        add_header Cache-Control "no-cache, must-revalidate";
    }
```
