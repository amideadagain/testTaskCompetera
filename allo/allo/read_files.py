import pandas as pd


def read_csv():
    category_links = pd.read_csv('C:/Users/USER/Documents/py_practice/testTaskCompetera/allo/category_pages.csv')
    return category_links['category_url'].values.tolist()
