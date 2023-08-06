from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import json
import time

# Define start of the program
start = time.time()

# Define the products and their URLs
with open ('products.json') as f:   
    products = json.load(f)

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without opening a browser window)

# Set the path to the chromedriver executable
webdriver_service = Service('/usr/local/bin')  

# Create an empty list to store the prices
new_prices = []

df = pd.read_csv('prices.csv')
df['Old_Price'] = df['New_Price']
# print(df)
product_list = list(df['Product'])
# print(product_list)
# Loop through each product
i = 1
for product in products:

    # Create a new Selenium WebDriver instance
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    # Load the product page
    driver.get(product["url"])
    
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
                # check if current price is minimum
                if df.iloc[df.index[df['Product'] == product['name']], 4].sum() > new_price:
                    df.iloc[df.index[df['Product'] == product['name']], 4] = new_price
                    df.iloc[df.index[df['Product'] == product['name']], 6] = 'Minimum is updated'
                else:
                    if df.iloc[df.index[df['Product'] == product['name']], 5].sum() == 0:
                        df.iloc[df.index[df['Product'] == product['name']], 6] = 'It is known minimum, you can buy'
                    else:
                        df.iloc[df.index[df['Product'] == product['name']], 6] = '-'
            else:
                df.loc[len(df)] = {
                        'Product': product['name'], 
                        'Old_Price': new_price, 
                        'New_Price': new_price, 
                        'Difference': 0, 
                        'Minimum_Price': new_price, 
                        'Difference_Minimun':0, 
                        'Comment': 'New',
                        'Percentage': 0
                    }
            break
    i += 1

    driver.quit()

product_names = [p['name'] for p in products]
for product in product_list:
    if product not in product_names:
        df.iloc[df.index[df['Product'] == product], 6] = 'Product was removed from tracking'
    else:
        df.iloc[df.index[df['Product'] == product], 6] = '-'
# Update the difference betweeen New and Old prices in our file 
df['Difference'] = df['New_Price'] - df['Old_Price']
df['Difference_Minimum'] = df['New_Price'] - df['Minimum_Price']
df['Percentage'] = round(100 * df['Difference_Minimum'] / df['Minimum_Price'], 2)
df.sort_values(['New_Price'], inplace=True, ignore_index=True, ascending=True)
print('\n--------------------------------------------Full table-------------------------------------------------\n')    
print(df)
print('\n---------------------------------------------Favorite--------------------------------------------------\n')    
print(df[(df.Percentage < 10) & (df.Percentage > 0)])
print('\n------------------------------------------Min As Current-----------------------------------------------\n')    
print(df[df.Percentage == 0])

df.to_csv('prices.csv', index=False)

total_time = time.time() - start
print(f"TIME: {int(total_time//60):d} min and {total_time%60:.2f} sec")
#TODO: add time and CPU check
#TODO: update README.md