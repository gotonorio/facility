import logging
import re

logger = logging.getLogger(__name__)


def translate_kurasel_text(note_text):
    """テキストをクリーンアップし、指定行数ごとのリストに変換する"""

    # 行毎に分割して、空行と文字前後の空白を除去したリストを内包表記で作成
    full_text_list = [line.strip() for line in note_text.splitlines() if line.strip()]

    # データの種類判定とヘッダ除去
    first_line = full_text_list[0]
    if first_line not in ("駐車場", "バイク置場", "自転車置場"):
        raise ValueError("ヘッダの「駐車場」または「自転車置場」「バイク置場」の行からコピーしてください")

    # 実データ部分の抽出のため、ヘッダ行（6行）をスキップ
    data_list = full_text_list[6:]

    # データをグループ化してリストを作成する
    result = []
    i = 0
    while i < len(data_list):
        no = data_list[i]
        okiba = data_list[i + 1]

        # 費用から数字だけを抽出 (例: ¥200(月) -> 200)
        hiyo_line = data_list[i + 2]
        hiyo_match = re.search(r"\d+", hiyo_line)
        hiyo = hiyo_match.group() if hiyo_match else "0"

        # 4項目目を取得
        next_line = data_list[i + 3]

        if next_line == "空き":
            room_no = ""
            status = "空き"
            i += 4
        else:
            # 部屋番号から数字だけを抽出 (例: 部屋番号 1311 -> 1311)
            room_match = re.search(r"\d+", next_line)
            room_no = room_match.group() if room_match else ""

            status = data_list[i + 4]
            i += 5

        # 結果を格納
        result.append([no, okiba, hiyo, room_no, status])

    return "bicycle", result


def execute_translator(form_data):
    """インポート処理のメイン関数"""

    year = form_data["year"]
    month = form_data["month"]

    context_result = {
        "year": year,
        "month": month,
    }

    try:
        # 1. テキスト解析
        data_kind, data_list = translate_kurasel_text(form_data["note"])

        # 2. 合計計算
        total = sum(int(d[2]) for d in data_list if d[4] != "空き")

        context_result.update(data_list=data_list, total=total, error_message="")

    except ValueError as e:
        context_result["error_message"] = str(e)
        return False, context_result

    return True, context_result
