import requests
import re
import json
import pandas as pd

def scrape_dongchedi_specs(car_ids):
    """
    Scrape and compare vehicle specifications from Dongchedi by car/trim IDs.

    Args:
        car_ids (list of int/str): List of Dongchedi car IDs to compare.

    Returns:
        pd.DataFrame: pivoted specification table with categories and parameters.
    """
    if not car_ids:
        return pd.DataFrame()
    
    # Filter duplicate IDs and ensure they are numeric
    sanitized_ids = []
    for cid in car_ids:
        cid_str = str(cid).strip()
        if cid_str.isdigit() and cid_str not in sanitized_ids:
            sanitized_ids.append(cid_str)
            
    if not sanitized_ids:
        return pd.DataFrame()
        
    # Construct comparison URL (dash-separated)
    car_ids_str = "-".join(sanitized_ids)
    url = f"https://www.dongchedi.com/auto/params-carIds-{car_ids_str}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.dongchedi.com/",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        text = response.text
        
        match = re.search(r'<script[^>]*>(\{"props":.*?\})</script>', text)
        if not match:
            print("Dongchedi Scraper: No props script tag found in HTML response.")
            return pd.DataFrame()
            
        data = json.loads(match.group(1))
        raw_data = data.get("props", {}).get("pageProps", {}).get("rawData", {})
        
        car_info = raw_data.get("car_info", [])
        properties = raw_data.get("properties", [])
        
        if not car_info:
            print("Dongchedi Scraper: No car_info list found in rawData.")
            return pd.DataFrame()
            
        # Create a mapping of car_id -> display_name
        car_id_to_name = {}
        for car in car_info:
            series_name = car.get("series_name", "")
            car_name = car.get("car_name", "")
            display_name = f"{series_name} ({car_name})" if series_name and car_name else f"Car {car.get('car_id')}"
            car_id_to_name[int(car.get('car_id'))] = display_name
            
        rows = []
        current_category = ""
        
        for prop in properties:
            prop_type = prop.get("type")
            text_label = prop.get("text", "")
            key = prop.get("key", "")
            
            if prop_type == 0:
                current_category = text_label
                continue
                
            # If it's type 1 or 2, it's a single parameter
            if prop_type in [1, 2]:
                row_dict = {
                    "カテゴリ": current_category,
                    "項目": text_label
                }
                
                for car in car_info:
                    cid = int(car.get("car_id"))
                    name = car_id_to_name[cid]
                    val_obj = car.get("info", {}).get(key)
                    
                    val_str = "-"
                    if isinstance(val_obj, dict):
                        val_str = val_obj.get("value") or "-"
                    elif isinstance(val_obj, str):
                        val_str = val_obj
                        
                    row_dict[name] = val_str
                    
                rows.append(row_dict)
                
            # If it's type 3, it has sub items in sub_list
            elif prop_type == 3:
                sub_list = prop.get("sub_list") or []
                for sub in sub_list:
                    sub_text = f"{text_label} - {sub.get('text')}"
                    sub_key = sub.get("key")
                    
                    row_dict = {
                        "カテゴリ": current_category,
                        "項目": sub_text
                    }
                    
                    for car in car_info:
                        cid = int(car.get("car_id"))
                        name = car_id_to_name[cid]
                        val_obj = car.get("info", {}).get(sub_key)
                        
                        val_str = "-"
                        if isinstance(val_obj, dict):
                            val_str = val_obj.get("value") or "-"
                        elif isinstance(val_obj, str):
                            val_str = val_obj
                            
                        row_dict[name] = val_str
                        
                    rows.append(row_dict)
                
        df = pd.DataFrame(rows)
        return df
    except Exception as e:
        print(f"Dongchedi Spec Scraping Error: {e}")
        return pd.DataFrame()
