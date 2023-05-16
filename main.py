import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd

# Define the products and their URLs
products = [
    {'name': 'Arkham Horror: Dunwich - Investigators', 'url': 'https://www.amazon.de/dp/B09M4F9P5V'},
    {'name': 'Arkham Horror: Dunwich - Campaign', 'url': 'https://www.amazon.de/dp/B09M4GQVH5'},
    {'name': 'Arkham Horror: Carcosa - Investigators', 'url': 'https://www.amazon.de/dp/B09V1TLZD2'},
    {'name': 'Arkham Horror: Carcosa - Capmaign', 'url': 'https://www.amazon.de/dp/B09V1V2MZW'},
    {'name': 'Arkham Horror: Forgotten Age - Expansion', 'url': 'https://www.amazon.de/dp/B07B8SJ31L'},
    {'name': 'Arkham Horror: The Circle Undone - Expansion', 'url': 'https://www.amazon.de/dp/B07MZCWJMP'}
]

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without opening a browser window)

# Set the path to the chromedriver executable
webdriver_service = Service('/usr/local/bin')  # Replace 'path_to_chromedriver' with the actual path

# Create an empty list to store the prices
new_prices = []

df = pd.read_csv('prices.csv')
df['OldPrice'] = df['NewPrice']
# print(df)
product_list = list(df['Product'])
# print(product_list)
# Loop through each product
i = 1
for product in products:
    # print(f"---------------{product['name']}------------------")

    # Create a new Selenium WebDriver instance
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    # Load the product page
    driver.get(product['url'])
    
    html = driver.page_source

    soup = BeautifulSoup(html, features="html.parser")
    with open(f'html/html{i}.txt' , 'w') as f:
        f.write(soup.prettify())
    # soup.prettify()

    asection = soup.select('div.a-section')
    for a in asection:
        # print(a.text)
        if "priceAmount" in a.text:
            # print('priceAmount found')
            # print(a.text.index("priceAmount"))
            # print(a.text.index("currencySymbol"))
            new_price = float(a.text[a.text.index("priceAmount") + 13:a.text.index("currencySymbol") - 2])
            # print(new_price)
            new_prices.append(new_price)
            if product['name'] in product_list:
                # print('In')
                df.iloc[df.index[df['Product'] == product['name']], 2] = new_price
                # print(df.iloc[df.index[df['Product'] == product['name']], 4])
                if df.iloc[df.index[df['Product'] == product['name']], 4].sum() > new_price:
                    df.iloc[df.index[df['Product'] == product['name']], 4] = new_price
            else:
                # print('New')
                dict_add = {'Product': product['name'], 'OldPrice': new_price, 'NewPrice': new_price, 'Difference': 0, 'Minimum': new_price}
                df.loc[len(df)] = dict_add
            break
    i += 1
    # Quit the WebDriver
    driver.quit()
    # print('----------------------------------')


# Create a Pandas DataFrame with the product names and prices

df['Difference'] = df['NewPrice'] - df['OldPrice']

print(df)

df.to_csv('prices.csv', index=False)