import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time
import random
import datetime
import os

def scrap_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    items=soup.find_all('article', class_='prd _fb _p col c-prd')
   
    products = []
    for soup_item in  items:
        stock = float(soup_item.find("div", class_ = "stk").text.split()[0]) if soup_item.find("div", class_="stk") else 0
        #stock = float(stock.split()[0])
        for item in soup_item.find_all('div', class_='info'):
            
            # Extract Name (h3 tag)
            name = item.find('h3', class_='name').text.strip() if item.find('h3', class_='name') else "None"
            
            # Extract Current Price
            price_raw = item.find('div', class_='prc')
            # Clean price: remove 'KSh' and ','
            price = int(price_raw.text.replace('KSh', '').replace(',', '').split('-')[0].strip()) if item.find('div', class_='prc') else 0
            
            # Extract Old Price (may not exist)
            old_price_tag = item.find('div', class_='old')
            old_price = int(old_price_tag.text.replace('KSh', '').replace(',', '').split('-')[0].strip()) if old_price_tag else 0 
        
            # Extract Discount %
            discount_tag = item.find('div', class_='bdg _dsct _sm')
            discount = int(discount_tag.text.replace('%', '').strip()) if discount_tag else 0
            
            # Extract Rating & Review Count
            rev_div = item.find('div', class_='rev')
            if rev_div:
                # The text before the "(" is the rating (e.g., "3.9 out of 5")
                rating = list(rev_div.stripped_strings)[0]
                rating = float(rating.split()[0])
                # The text inside the "()" is the review count
                # We strip the parentheses and convert to int
                reviews = rev_div.text.split('(')[-1].replace(')', '').strip()
            else:
                rating, reviews = 0,0

            products.append({
                'datetime':datetime.datetime.now(),
                "name": name,
                "price": price,
                "old_price": old_price,
                "discount": discount,
                "rating": rating,
                "reviews": int(reviews),
                "stock_left": stock
            })
    page_links = soup.find("div", class_="pg-w -ptm -pbxl")
    next_page_url = None
    if page_links:
        next_tag = page_links.find('a', attrs={'aria-label': 'Next Page'})
        if next_tag:
            next_page_url = urljoin("https://www.jumia.co.ke", next_tag.get('href'))
            
    return products, next_page_url
   
    
def main():
    base_url = "https://www.jumia.co.ke/flash-sales/"
    current_url = base_url
    
    while current_url:
        wait_time = random.uniform(1, 5) 
        print(f"Waiting for {wait_time:.2f} seconds...")
        time.sleep(wait_time)
        print(f"Scraping: {current_url}")
        products, next_page_url = scrap_page(current_url)
        
        if products:
            df = pd.DataFrame(products)
            folder_path = "scripts/data"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
                file_path = os.path.join(folder_path, "Jumiaproducts.csv")
        
                header = not os.path.exists(file_path)
                df.to_csv(file_path, mode='a', index=False, header=header)

        
        current_url = next_page_url

if __name__ == "__main__":
    try:
        main()
        print("Scraping completed successfully!")
    except KeyboardInterrupt:
        print("\nScraper stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
