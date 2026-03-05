import logging

import pandas as pd

from repair_plan.models import KoujiName

# from repair_plan.services.table_formatter import add_totals, build_pivot, build_repair_plan_data

logger = logging.getLogger(__name__)


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

    return pivot_df


def sort_year_columns(pivot_df):
    """列（column）が整数型ならば、その列を昇順に並び替える"""

    year_cols = sorted([col for col in pivot_df.columns if isinstance(col, int)])
    # pivot_dfから「kouji_type」と「kouji_name」の列だけを取り出して、「年」の列を追加する
    pivot_df = pivot_df[["kouji_type__master_name", "kouji_name"] + year_cols]

    return pivot_df


def rename_headers(pivot_df):
    """ヘッダ名変更"""

    pivot_df = pivot_df.rename(
        columns={
            "kouji_type__master_name": "工事種別",
            "kouji_name": "工事名",
        }
    )

    return pivot_df


def add_total_bottom(pivot_df):
    """ピボットテーブルの最下行に合計行を追加"""

    # ピボットテーブルの最後列に行合計を追加(axis=1は行方向の合計)
    year_columns = pivot_df.columns[2:]
    pivot_df["合計"] = pivot_df[year_columns].sum(axis=1)

    # ピボットテーブルの最下行に年ごとの合計を追加(axis=0は列方向の合計)
    year_totals = pivot_df[year_columns].sum(axis=0)
    # ピボットテーブルの総合計を計算(年ごとの合計の合計)
    grand_total = pivot_df["合計"].sum(axis=0)

    total_row = {
        "工事種別": "",
        "工事名": "総合計",
        **year_totals.to_dict(),
        "合計": grand_total,
    }
    # ピボットテーブルの最下行に合計行を追加
    pivot_df = pd.concat([pivot_df, pd.DataFrame([total_row])], ignore_index=True)

    return pivot_df
