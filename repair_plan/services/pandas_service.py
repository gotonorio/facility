import logging

import pandas as pd

from repair_plan.models import KoujiName

# from repair_plan.services.table_formatter import add_totals, build_pivot, build_repair_plan_data

logger = logging.getLogger(__name__)


def get_pandas_dadaframe(ver):
    """
    指定バージョンの修繕計画データを抽出して、データフレームとして返す
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


def get_pandas_pivottable(df):
    """
    指定バージョンの修繕計画テーブルデータをソートしてピボットテーブル形式で返す
    - index   : 元データの列名を指定。結果の行見出しとなる。（工事種別名と工事名）
    - columns : 元データの列名を指定。結果の列見出しとなる。(西暦年)
    - values  : 元データの列名（unit_price）を指定。「工事種別名+工事名」毎の西暦年毎の合計値が計算される。
    - aggfunc : valuesの処理方法を指定。合計（sum）を指定。
    - fill_value : valuesが存在しない場合は「0」とする。
    - sort    : 集計した行・列のインデックスが勝手にソートされないようにFalseを設定。
    - reset_index() : pivot_table()で作成したピボットテーブルでは「kouji_type__master_name」「kouji_name」が
                    行インデックとなっているので、これを普通の列へ戻すためにリセットする。
    """
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
    """列（column）が整数型ならば、その列を昇順に並び替える
    - データフレームの並び順List = ["kouji_type__master_name", "kouji_name", 2024, 2025, 2026, ...]
    - pivot_df = pivot_df[データフレームの並び順List]で、その指定した順番通りに並んだデータフレームにして返す
    """
    year_cols = sorted([col for col in pivot_df.columns if isinstance(col, int)])
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


def add_total_df(pivot_df):
    """データフレームの最下行と最後列に合計を追加"""

    # dfの最後列に行合計を追加(axis=1は行方向の合計)
    # 金額は3列目以降
    year_columns = pivot_df.columns[2:]
    pivot_df["合計"] = pivot_df[year_columns].sum(axis=1)

    # dfの最下行に年ごとの合計を追加
    # 列合計のデータフレームを作成する（axis=0は列方向の合計）
    year_totals = pivot_df.sum(numeric_only=True, axis=0)

    # 行タイトルと合計行を辞書化した辞書を作成
    total_row = {
        "工事種別": "修繕支出合計",
        "工事名": "",
        **year_totals.to_dict(),
    }
    # dfの最下行に合計行データフレームを追加
    pivot_df = pd.concat([pivot_df, pd.DataFrame([total_row])], ignore_index=True)

    return pivot_df


def pivottable_to_htmltable(pivot_df):
    """pivot_tableからtemplate出力用のhtml_tableを生成する"""

    # 1. カンマ区切り関数
    def comma_format(val):
        try:
            # valを数値として扱えるか試し、3桁区切りの文字列にする
            return f"{int(val):,}"
        except (ValueError, TypeError):
            # 文字列（""など）や、変換できない値の場合はそのまま返す
            return val

    # 2. 数値列のリスト
    numeric_cols = list(pivot_df.columns[2:])

    # 3. フォーマット辞書を生成
    formatter_dict = {col: comma_format for col in numeric_cols}

    # 4. テンプレートに渡すために HTML 文字列（<table>）に変換
    # classes で bulma の CSS クラスを付与する
    html_table = pivot_df.to_html(
        index=False,
        classes="table is-striped is-narrow is-hoverable repair-table",
        index_names=False,
        formatters=formatter_dict,  # ここでカンマ区切りを適用
        border=1,  # tableの外枠
    )

    return html_table
