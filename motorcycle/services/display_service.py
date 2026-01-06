from facility.services import select_period

from motorcycle.models import MotorCycleSpace


def get_motorcycle_summary(year, month):
    """
    指定年月のバイク駐車場のリストと統計情報を取得する
    """
    # 抽出期間の取得
    tstart, tend = select_period(year, month)

    # 区画リストの取得
    qs = MotorCycleSpace.objects.filter(date__range=[tstart, tend]).order_by("no")

    # 統計計算
    count_all = qs.count()
    count_use = qs.filter(status_of_use="使用中").count()

    return {
        "motorcycle_list": qs,
        "count_all": count_all,
        "count_use": count_use,
    }
