# ----------------------------------------------------------------------------
# Name: repairplan_create_service.py
# Purpose: 長期修繕計画データ作成サービス
# ----------------------------------------------------------------------------


def create_repair_plan_from_basic_data(self, data_list, start_year, last_year, limmit_num=100):
    """
    長期修繕計画データを基本データから作成する
    - 工事名毎に最大100回分の工事予定を作成.
    """
    plan_list = []
    for row in data_list:
        # 最初の工事を行う年（西暦）
        yyyy = int(row[3])
        # 1つの工事項目についてlimmit_num回繰り返す
        for i in range(1, limmit_num):
            # 予定年度が最終計画年度以上になったら、次の工事名処理を行う.
            if yyyy >= last_year:
                break
            else:
                # 工事データをplan_listに追加して、次の工事予定年（西暦）を求める
                yyyy = self.add_planlist(row, yyyy, start_year, plan_list)
                # 周期（row[4]）が0なら1回だけの工事なのでbreakして抜ける
                if int(row[4]) < 1:
                    break
    return plan_list


def add_planlist(self, row, yyyy, start_year, plan_list):
    """
    修繕計画データリストに追加する処理
    """

    # rowリストをtmplistにコピー
    tmplist = row[:]
    # 不要データを削除
    del tmplist[3:5]
    tmplist.insert(1, yyyy)  # 施工予定年
    tmplist.insert(4, 1)  # 数量は「1」に固定
    tmplist.insert(5, "式")  # 数量単位は「式」に固定
    tmplist.insert(7, 0)  # 実績費用は「0」に固定
    # 計画初年度以降のデータをplan_listに追加
    if yyyy >= start_year:
        plan_list.append(tmplist)
    yyyy += int(row[4])

    # 次の施工予定年を返す.
    return yyyy


def fill_dummydata(self, plan_list, start_year, last_year):
    """
    抜けている年のデータ（ダミーデータ）を追加する
    - 長期修繕計画では期間中の工事予定が無い年のデータも必要
    """

    # 工事予定年だけのリストを作成
    year_list = []
    for i in plan_list:
        year_list.append(i[1])
    # 重複年を除去
    unique_year_list = list(set(year_list))
    # 重複を除去したリストを昇順にソート
    unique_year_list.sort()

    for cnt_year in range(start_year, last_year):
        # データが存在すればスキップする
        if cnt_year in unique_year_list:
            pass
        else:
            # 不足している年のダミーデータをplan_listに追加する
            dummy_data = [5, 0, "ダミー工事", "ダミー工事", 1, "式", 0, 0, ""]
            dummy_data[1] = cnt_year
            plan_list.append(dummy_data)
        cnt_year += 1

    return plan_list
