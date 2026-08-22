import pytest

from ..models import KoujiName, MasterKoujiType, MasterPlan, MasterUnit


# -----------------------------------------------------------------------------
# 修繕計画表示用工事データの作成
# -----------------------------------------------------------------------------
@pytest.fixture
def master_plan():
    return MasterPlan.objects.create(
        version=1,
        first_year=2026,
        final_year=2060,
        balance=1000,
    )


@pytest.fixture
def master_kouji_type():
    return MasterKoujiType.objects.create(
        sequense=1,
        master_name="大規模修繕",
    )


@pytest.fixture
def master_unit():
    return MasterUnit.objects.create(unit_name="式")


@pytest.fixture
def kouji_name(master_plan, master_unit, master_kouji_type):
    data = KoujiName.objects.create(
        version=master_plan,
        kouji_type=master_kouji_type,
        kouji_name="外壁塗装",
        kouji_quantity=1,
        unit=master_unit,
        unit_price=1000,
        kouji_year=2040,
    )
    data = KoujiName.objects.create(
        version=master_plan,
        kouji_type=master_kouji_type,
        kouji_name="外壁補修",
        kouji_quantity=1,
        unit=master_unit,
        unit_price=2000,
        kouji_year=2040,
    )
    return data
