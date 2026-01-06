from django.conf import settings
from django.utils import timezone

from .models import Shoukaki


def get_sorted_shoukaki_list(order_label):
    """表示順ラベルに基づいて並べ替えられた消火器リストを返す"""
    # ラベルとモデルフィールドの対応マップ
    order_mapping = {
        "製造年": "made_year",
        "設置日": "installation_date",
        "点検日": "inspection_date",
        "形式": "shoukaki__keisiki",
    }

    order_field = order_mapping.get(order_label, "code")
    return Shoukaki.objects.select_related("shoukaki").filter(alive=True).order_by(order_field)


def get_shoukaki_form_initial():
    """新規作成時の初期値を返す"""
    now = timezone.localtime(timezone.now())
    return {"installation_date": now, "made_year": now.year}


def get_disposable_shoukaki_list(target_year):
    """
    指定された年を基準に、交換期限（DISPOSAL_SHOUKAKI）を過ぎた消火器を取得
    """
    threshold_year = int(target_year) - settings.DISPOSAL_SHOUKAKI

    return (
        Shoukaki.objects.select_related("shoukaki")
        .filter(alive=True)
        .filter(made_year__lte=threshold_year)
        .order_by("made_year")
    )
