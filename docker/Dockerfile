# warehouse用Dockerfile by N.Goto
# warehouseコンテナの作成
# 1. slimイメージを使うので、コンパイル用ライブラリをインストールする。
# 2. コンテナ内に /code ディレクトリを作成し、ルートディレクトリのファイルをコピーする。
# 3. pythonライブラリをインストールする。
# 4. appuser（UID=1001、GID=1001）を作成し、/code の権限者にする。
# 5. 最後にユーザを root から appuser に切り替える。
# 6. 最後の最後に collectstatic を実行するためのシェルスクリプトを entrypointに設定する。

# 使用するベースイメージ。（最新版の一つ前のバージョンとする）
FROM python:3.12-slim

# 1. 環境変数の設定
# stdoutへの出力をバッファリングさせない。(errorやlogを直ちに出力して欲しいから)
ENV PYTHONUNBUFFERED=1

# 2. システムライブラリのインストール（root権限が必要）
# build-essential（コンパイル用）とフォントをまとめてインストール
# pdf作成処理がある場合（WeasyPrintを使う）はnotoフォントをインストールする
RUN apt-get update && apt-get install -y \
    build-essential \
    # fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 3. /code/ディレクトリを作業用ディレクトリにする。
WORKDIR /code

# 4. Pythonライブラリのインストール
# 先にrequirementsだけコピーすると、コードを書き換えてもキャッシュが効いて高速です
COPY docker/requirements /code/requirements
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements/prod.txt

# 5. アプリケーションコードのコピー
# ホスト上の「django関連ファイル」を作業用ディレクトリ/code/にコピーする。
# データベースファイル、mediaなどは.djangoignoreで除外すること
# 注意することは、
# COPYコマンドは親ディテクトリはコピーできないので、compose.ymlのcontextをソース階層に設定する。
COPY . /code/

# 6. dockerコンテナのユーザ作成
ARG UID=1001
ARG GID=1001

# 7. ユーザ作成
RUN groupadd -g ${GID} appuser \
    && useradd -m -u ${UID} -g ${GID} appuser

# 8. /codeの所有者をrootからappuserに変更する。
RUN chown -R ${UID}:${GID} /code

# 9. collectstatic実行スクリプトに実行権限を付与
RUN chmod +x /code/entrypoint.sh

# 10. 最後にユーザの切り替え（COPYの後に切り替える)
USER appuser

# 11. 起動時に collectstatic などの初期化処理を行うシェルスクリプトをエントリポイントとして登録
ENTRYPOINT ["/code/entrypoint.sh"]
