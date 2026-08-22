import pytest

from ..models import KoujiName


@pytest.mark.django_db
def test_get_repair_plan_list(kouji_name):
    """モデル関数（get_repair_plan_list）の単体テスト 詳細版（simple=False）"""

    qs = KoujiName.get_repair_plan_list(ver=kouji_name.version, start_year=2039, end_year=2041, simple=False)
    results = list(qs)

    assert len(results) == 2

    # 1件目: 外壁塗装 (2040年)
    row1 = results[0]
    assert row1[0] == "大規模修繕"
    assert row1[1] == "外壁塗装"
    assert row1[2] == 0  # 2039年は工事なし
    assert row1[3] == 1000  # 2040年は大規模修繕
    assert row1[4] == 0  # 2041年は工事なし
    assert row1[5] == 1000  # total

    # 2件目: 外壁補修 (2040年)
    row2 = results[1]
    assert row2[0] == "大規模修繕"
    assert row2[1] == "外壁補修"
    assert row2[2] == 0  # 2039年は工事なし
    assert row2[3] == 2000  # 2040年は大規模修繕
    assert row2[4] == 0  # 2041年は工事なし
    assert row2[5] == 2000  # total


@pytest.mark.django_db
def test_get_repair_plan_list_simple(kouji_name):
    """モデル関数（get_repair_plan_list）の単体テスト 配布版（simple=True）"""

    qs = KoujiName.get_repair_plan_list(ver=kouji_name.version, start_year=2039, end_year=2041, simple=True)
    results = list(qs)

    assert len(results) == 1

    # 1件目: 外壁塗装 (2024年)
    row1 = results[0]
    assert row1[0] == "大規模修繕"
    assert row1[1] == 0  # 2039年は工事なし
    assert row1[2] == 3000  # 2040年は大規模修繕（外壁塗装1000 + 外壁補修2000）
    assert row1[3] == 0  # 2041年は工事なし
    assert row1[4] == 3000  # total
