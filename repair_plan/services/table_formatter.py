def build_pivot(df):
    df = df.sort_values(["kouji_type__sequense", "kouji_name"])

    return df.pivot_table(
        index=["kouji_type__master_name", "kouji_name"],
        columns="kouji_year",
        values="unit_price",
        aggfunc="sum",
        fill_value=0,
        sort=False,
    )


def add_totals(pivot_df):
    pivot_df["合計"] = pivot_df.sum(axis=1)

    yearly_total = pivot_df.sum(axis=0)

    return pivot_df, yearly_total


def build_repair_plan_data(df):
    pivot_df = build_pivot(df)
    pivot_df, yearly_total = add_totals(pivot_df)

    header_years = list(pivot_df.columns)

    categories = []

    current_type = None
    category_rows = []

    for (kouji_type, kouji_name), row in pivot_df.iterrows():
        if kouji_type != current_type:
            if current_type is not None:
                categories.append(
                    {
                        "name": current_type,
                        "rows": category_rows,
                    }
                )
            current_type = kouji_type
            category_rows = []

        category_rows.append(
            {
                "kouji_name": kouji_name,
                "values": row.tolist(),
            }
        )

    if current_type is not None:
        categories.append(
            {
                "name": current_type,
                "rows": category_rows,
            }
        )

    return {
        "header_years": header_years,
        "categories": categories,
        "yearly_total": yearly_total.tolist(),
    }
