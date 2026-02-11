# Makefile

# 初回だけキャッシュクリアしてコンテナ起動する
up-initial:
	docker compose -f docker/compose.yml --env-file .env build --no-cache
	docker compose -f docker/compose.yml --env-file .env up -d

# 運用中はキャッシュを有効にしてコンテナ起動する
up:
	docker compose -f docker/compose.yml --env-file .env build
	docker compose -f docker/compose.yml --env-file .env up -d

# .envファイルによって設定された環境変数を表示する
config:
	docker compose -f docker/compose.yml --env-file .env config

# 静的ファイルを変更した時にcollectstaticを実行する
collectstatic:
	docker compose -f docker/compose.yml exec facility python manage.py collectstatic --noinput

# 開発環境では、常にキャッシュクリアする
up-dev:
	docker compose -f docker/compose_dev.yml --env-file .env_dev build --no-cache
	docker compose -f docker/compose_dev.yml --env-file .env_dev up -d

config-dev:
	docker compose -f docker/compose_dev.yml --env-file .env_dev config