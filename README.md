
# システム構成

🔲 ファイル構成
```
ホスト（Rocky Linux）
 │
 ├── warehouse → 共有領域から読込み（貸借対照表・駐車場状況図）
 │
 ├── /opt（共有領域）
 │     └─ shared_data
 │           ├─ balance_sheets（貸借対照表）
 │           └─ parking_maps（駐車場状況図）
 │
 ├── passbook/ → 共有領域に出力（貸借対照表）
 │     ├─ outputs
 │     │     └─ balance_sheets
 │     └─ docker
 │           ├─ compose.yml
 │           └─ Dockerfile
 │ 
 ├── facility/ → 共有領域に出力（駐車場状況図）
 │     ├─ outputs
 │     │     └─ parking_maps
 │     └─  docker
 │           ├─ compose.yml
 │           └─ Dockerfile





```

🔲 Django

```bash
# settings.pyで、コンテナ内でマウントした共有ディレクトリのパスを設定
SHARED_OUTPUT_ROOT = BASE_DIR / 'outputs' / 'parking_maps'

# projectルート（manage.pyと同じ階層）に出力用ディレクトリ 'outputs' を作成

# viewとして以下を作成
from django.template.loader import render_to_string
from django.conf import settings
import os

def generate_balance_sheet_html(context_data):
    # 1. HTMLを生成
    html_string = render_to_string("parking/parking_fig_output.html", context_data)
    
    # 2. 保存先のフルパスを作成
    filename = "parking_fig_latest.html"
    file_path = os.path.join(settings.SHARED_OUTPUT_ROOT, filename)

    # 共有領域ディレクトリが存在しない場合の処理
    os.makedirs(settings.SHARED_OUTPUT_ROOT, exist_ok=True)
    
    # 3. 書き出し
    # Rocky Linux + Dockerの権限問題を避けるため、mode='w' で上書き保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_string)
    
    return file_path

```
