import logging

import pandas as pd

from repair_plan.models import KoujiName

logger = logging.getLogger(__name__)


def get_repair_plan_table_data(ver, is_simple=False):
    """
    指定バージョンの修繕計画テーブルデータと計算結果を返す
    """
    # 期間の取得
    range_data = KoujiName.objects.get_year_range(ver)
    start_year = range_data.get("start_year")
    end_year = range_data.get("end_year")

    if start_year is None or end_year is None:
        return None

    # 修繕計画データの抽出
    qs_list = KoujiName.objects.get_repair_plan_list(ver, start_year, end_year, is_simple)

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


def get_pandas_table_data(ver):
    """
    指定バージョンの修繕計画テーブルデータをpandasで処理して返す
    """
    qs = KoujiName.objects.filter(version__version=ver).values(
        "kouji_type__master_name",
        "kouji_type__sequense",
        "kouji_name",
        "kouji_year",
        "unit_price",
    )
    df = pd.DataFrame(list(qs))
    return df


def get_pivot_table_data(df):
    """
    指定バージョンの修繕計画テーブルデータをpandasで処理してピボットテーブル形式で返す
    """
    # ---------------------------
    # pivotへ変換
    # ---------------------------
    pivot_df = (
        df.sort_values(["kouji_type__sequense", "kouji_name"])
        .pivot_table(
            index=["kouji_type__master_name", "kouji_name"],
            columns="kouji_year",
            values="unit_price",
            aggfunc="sum",
            fill_value=0,
            sort=False,
        )
        .reset_index()
    )

    # 列（column）が整数型ならば、その列を昇順に並び替える
    year_cols = sorted([col for col in pivot_df.columns if isinstance(col, int)])
    # pivot_dfから「kouji_type」と「kouji_name」の列だけを取り出して、「年」の列を追加する
    pivot_df = pivot_df[["kouji_type__master_name", "kouji_name"] + year_cols]

    # ヘッダ名変更
    pivot_df = pivot_df.rename(
        columns={
            "kouji_type__master_name": "工事種別",
            "kouji_name": "工事名",
        }
    )

    return pivot_df
