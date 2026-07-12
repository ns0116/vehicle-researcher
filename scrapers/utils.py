import pandas as pd


def pivot_spec_fields(
    spec_fields: list[tuple[str, str, str]],
    matched_cars: list[tuple[int, dict]],
) -> pd.DataFrame:
    """Pivot a spec field definition list into a comparison DataFrame."""
    rows = []
    for category, key, label in spec_fields:
        row_dict = {"カテゴリ": category, "項目": label}
        for _cid, car in matched_cars:
            car_label = f"{car['series_name']} ({car['car_name']})"
            row_dict[car_label] = car["info"].get(key, "-")
        rows.append(row_dict)
    return pd.DataFrame(rows)
