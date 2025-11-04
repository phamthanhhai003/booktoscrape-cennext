import requests
import random
import pandas as pd

def get_countries():
    url = "https://restcountries.com/v3.1/independent?status=true"
    response = requests.get(url)
    
    if response.status_code == 200:
        countries = response.json()
        return [country['name']['common'] for country in countries]
    else:
        print(f"Failed to fetch countries. Status code: {response.status_code}")
        return []


def run():
 countries = get_countries()
 df = pd.read_csv('books.csv')
 df['publisher_country'] = [random.choice(countries) for _ in range(len(df))]
 df.to_csv('books_with_country.csv', index=False)
