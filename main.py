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
    {'name': 'The Cartographers', 'url': 'https://www.amazon.de/dp/B07ZQPY1TX'},
    {'name': 'Codenames Duet', 'url': 'https://www.amazon.de/dp/B072J234ZF'},
    {'name': 'Welcome To', 'url': 'https://www.amazon.de/dp/B09T3K5TZL'},
    {'name': 'Pixel Tactics', 'url': 'https://www.amazon.de/dp/B015482LJU'},
    {'name': 'Sagrada', 'url': 'https://www.amazon.de/dp/B07CLRY89M'},
    {'name': 'Boss Monster', 'url': 'https://www.amazon.de/dp/B01BLNVW24'},
    {'name': 'Splendor', 'url': 'https://www.amazon.de/dp/B00ORBVDNQ'},
    {'name': 'Terra Nova', 'url': 'https://www.amazon.de/dp/B0B2TW65CK'},
    {'name': 'Boss Monster - Big Box', 'url': 'https://www.amazon.de/dp/B09T3LCP1B'}
]

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without opening a browser window)

# Set the path to the chromedriver executable
webdriver_service = Service('/usr/local/bin')  

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
    with open(f'html/html{i}.txt', 'w') as f:
        f.write(soup.prettify())
    # soup.prettify()

    asection = soup.select('div.a-section')
    for a in asection:

        data = a.text

        if "priceAmount" in a.text:

            # Find new price in the parsed document ('priceAmount':xx.xx) and add it to new prices
            new_price = float(data[data.index("priceAmount") + 13:data.index("currencySymbol") - 2])
            new_prices.append(new_price)

            # check if data if product is in the file or no
            if product['name'] in product_list:
                df.iloc[df.index[df['Product'] == product['name']], 2] = new_price
                if df.iloc[df.index[df['Product'] == product['name']], 4].sum() > new_price:
                    df.iloc[df.index[df['Product'] == product['name']], 4] = new_price
            else:
                dict_add = {'Product': product['name'], 'OldPrice': new_price, 'NewPrice': new_price, 'Difference': 0, 'Minimum': new_price}
                df.loc[len(df)] = dict_add
            break
    i += 1

    # Quit the WebDriver
    driver.quit()

# Update the difference betweeen New and Old prices in our file 
df['Difference'] = df['NewPrice'] - df['OldPrice']

# Show the result df
print(df)

# Save df to csv
df.to_csv('prices.csv', index=False)