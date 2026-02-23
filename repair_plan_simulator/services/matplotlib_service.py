import os

import matplotlib
from django.conf import settings

matplotlib.use("Agg")  # これを最初に追加！GUIを使わない設定にする
import japanize_matplotlib  # 日本語フォントを有効にするための設定
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter  # グラフの軸のフォーマットをカスタマイズするためのインポート


def generate_and_save_chart(raw_data, filename="simulate_graph_latest.png", current_year=None):
    # データの分解
    years = [row[0] for row in raw_data]
    income = [row[1] for row in raw_data]
    expense = [row[2] for row in raw_data]

    # グラフの構築
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # --- 単位を「万円」にするフォーマッタの設定 ---
    def yen_formatter(x, pos):
        """
        x: 現在の軸の値
        pos: 軸の位置（通常は無視してOK）
        """
        # 1万で割って、整数（または小数点1桁）にする
        return f"{int(x / 10000):,}万円"

    # Y軸に適用
    ax1.yaxis.set_major_formatter(FuncFormatter(yen_formatter))

    # 支出（棒グラフ）
    ax1.bar(years, expense, color="salmon", alpha=0.7, label="支出累計金額")

    # 収入（折れ線グラフ）- 右側の軸を使用
    ax1.plot(years, income, color="royalblue", marker="o", linewidth=2, label="収入累計金額")

    # 軸のラベル設定
    ax1.set_xlabel("年度")
    ax1.set_ylabel("金額")

    # メインタイトルとサブタイトルを個別に設定
    plt.suptitle(f"ソフィア・ガーデンズ川崎 長期修繕計画（{current_year}年）", fontsize=12, fontweight="bold")
    plt.title(
        "※ このグラフは長期修繕計画に基づく将来の収支シミュレーションです。\n実際の支出額は工事内容や物価変動等により変動する可能性があります。",
        fontsize=10,
        color="gray",
    )

    # 凡例を表示
    ax1.legend(loc="upper left")

    # Y軸の範囲を0からにする（マイナスがない）
    ax1.set_ylim(bottom=0)

    # 保存先のパス設定 (DjangoのMEDIA_ROOTなど)
    save_path = os.path.join(settings.IMAGE_OUTPUT_ROOT, filename)

    # ディレクトリがなければ作成
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # ファイル保存
    plt.savefig(save_path)
    plt.close()  # メモリ解放のために必ず閉じる

    return os.path.join(settings.IMAGE_OUTPUT_ROOT, filename)
