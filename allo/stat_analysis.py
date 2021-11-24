import math
import pandas as pd
import json


df = pd.read_csv('products_all.csv')

categories_list = []

print("Checking all the categories...")

for unique_category in df['category'].unique():
    total_count = df['category'].value_counts()[unique_category]

    available_count = len(df[(df['category'] == unique_category) & (df['availability'])])

    category_discounts = df[(df['category'] == unique_category) &
                            (~df['price'].isna()) & (~df['price'].isna()) & (df['price'] < df['price_regular'])]
    markdown_count = len(category_discounts)

    median_price = df[((df['category'] == unique_category) & (df['availability']))]['price'].median()

    regular_prices = category_discounts['price_regular']
    prices = category_discounts['price']
    median_markdown_percent = (((regular_prices - prices) / regular_prices) * 100).median()

    special_offers_df = df[(df['category'] == unique_category)].special_offers
    special_offers_lists = [json.loads(json_str) for json_str in special_offers_df]
    offers_list = [item for sublist in special_offers_lists for item in sublist]
    unique_special_offers = list(dict.fromkeys(offers_list))

    categories_dict = {'category': unique_category,
                       'total_count': total_count,
                       'available_count': available_count,
                       'markdown_count': markdown_count,
                       'median_price': median_price,
                       'unique_special_offers': json.dumps(unique_special_offers, ensure_ascii=False)}
    if not math.isnan(median_markdown_percent):
        categories_dict.update({'median_markdown_percent': round(median_markdown_percent)})
    categories_list.append(categories_dict)

whole_site_dict = {
    'total_count': df.shape[0],
    'available_count': len(df[df['availability']]),
    'markdown_count': len(df[(~df['price'].isna()) & (~df['price'].isna()) & (df['price'] < df['price_regular'])]),
    'median_price': df[(df['availability'])]['price'].median()
}
categories_list.append(whole_site_dict)

print("Creating new df...")
df_analysis = pd.DataFrame(categories_list)

print("Saving into csv...")
df_analysis.to_csv('stat_analysis.csv', index=False)
