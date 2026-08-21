import logging

# import pandas as pd
from repair_plan.models import KoujiName

logger = logging.getLogger(__name__)


def get_repair_plan_table_data(ver, is_simple=False):
    """
    指定バージョンの修繕計画テーブルデータと計算結果を返す
    """
    # 期間の取得
    range_data = KoujiName.get_year_range(ver)
    start_year = range_data.get("start_year")
    end_year = range_data.get("end_year")

    if start_year is None or end_year is None:
        return None

    # 修繕計画データの抽出
    qs_list = KoujiName.get_repair_plan_list(ver, start_year, end_year, is_simple)

    # 年毎の支出合計を保持するListの初期化
    # (start_yearからend_yearまでの年数 + アルファ)
    year_total = [0 for _ in range(start_year, end_year + 3)]

    # シンプル版か詳細版かでデータの開始列(index)が異なる
    start_idx = 1 if is_simple else 2

    # 合計計算ロジック
    for row in qs_list:
        for i in range(start_idx, len(year_total)):
            try:
                year_total[i] += row[i]
            except (IndexError, TypeError):
                continue

    # 計画期間全体の支出合計
    all_total = sum(year_total[start_idx:])

    return {
        "repairplan_list": list(qs_list),
        "year_total": year_total,
        "all_total": all_total,
        "start_year": start_year,
        "end_year": end_year,
        "years": [i for i in range(start_year, end_year + 1)],
    }
