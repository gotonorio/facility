#!/bin/bash
set -e

# 本番環境（product）の場合のみ collectstatic を実行
if [ "$APP_ENV" = "product" ]; then
    echo "Running collectstatic..."
    python manage.py collectstatic --noinput
fi

# DockerfileのCMD、またはcomposeのcommandで渡された内容を実行
exec "$@"
