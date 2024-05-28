import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from progress_bars import start_progress_bar, update_progress_bar, finish_progress_bar
import os


def search_google_shopping(product_name):
    options = Options()
    # Uruchamianie przeglądarki z akceleracją GPU
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--enable-features=VaapiVideoDecoder")

    log_path = "nul" if os.name == 'nt' else "/dev/null"
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)
    search_results = {"search_term": product_name, "shops": {}}

    try:
        driver.get('https://www.google.com/shopping')
        wait = WebDriverWait(driver, 30)

        # Oczekiwanie na przycisk zgody i kliknięcie go
        agree_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button span.VfPpkd-vQzf8d")))
        agree_button.click()

        search_box = wait.until(
            EC.visibility_of_element_located((By.NAME, 'q')))
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.RETURN)

        # Czekaj na załadowanie wyników
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.sh-pr__product-results')))

        # Pobieranie danych o produktach
        products = driver.find_elements(By.CSS_SELECTOR, 'div.sh-dgr__content')
        task_id = start_progress_bar(len(products))
        for i, product in enumerate(products):
            try:
                title = product.find_element(By.CSS_SELECTOR, "h3.tAxDx").text
                price = product.find_element(
                    By.CSS_SELECTOR, "span.a8Pemb.OFFNJ").text
                shop = product.find_element(
                    By.CSS_SELECTOR, "div.aULzUe.IuHnof").text
                search_results["shops"][shop] = {
                    "title": title, "price": price}
                update_progress_bar(task_id, advance=1)
            except Exception as e:
                print(f'Error processing product {i}')
                update_progress_bar(task_id, advance=0)

    except Exception:
        print(f'Error processing {product_name}')
    finally:
        driver.quit()
        finish_progress_bar()

    return search_results


async def run_searches():
    with open('search_terms.txt', 'r', encoding='utf-8') as file:
        search_terms = [line.strip() for line in file]

    # Zwiększenie liczby wątków do 50
    with ThreadPoolExecutor(max_workers=20) as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(
            executor, search_google_shopping, term) for term in search_terms]
        results = await asyncio.gather(*tasks)

    # Zapis wyników do pliku JSON
    with open('grouped_results.json', 'w', encoding='utf-8') as file:
        json.dump({"results": results}, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(run_searches())
