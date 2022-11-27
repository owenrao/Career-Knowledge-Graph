from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import numpy as np
import json
import time
from string import punctuation
from concurrent.futures import ThreadPoolExecutor
#from functools import partial

def wait_for_element(driver, locator, t=3):
    try:
        element = WebDriverWait(driver, t).until(
            EC.presence_of_element_located(locator)
        )
        return element
    except: return False

def shorten(txt):
    txt = txt.strip()
    if (txt[0] in punctuation):
        txt = txt.strip(txt[0])
        return txt
    if (txt[-1] in punctuation):
        txt = txt.strip(txt[-1])
        return txt
    return " ".join(txt.split(" ")[1:])

def driver_setup():
    options = Options()
    options.headless = True
    options.add_argument('window-size=1400,600')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--allow-insecure-localhost")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    #options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(options=options)
    return driver


def Indeed_Crawl(title_list, driver):
  url = "https://www.indeed.com/career/network-engineer"
  for title_info in title_list:
    title_name = title_info["name"]
    title_name = title_name.replace(".Net","Dotnet")
    for word in taboo:
        if word in title_name:
            return False
        
    print(f"[Log]Crawling {title_name}")
    print(f"{len(checkpoint)/len(title_list)*100:.2f}")
    #try:
    driver.get(url)
    problem = 0
    # if server error wait for an hour
    if problem>=3:
        print(f"[Log]Skipped {problem} times... Sleeping")
        #time.sleep(720)
        print(f"[Log]Restarting...")
        return False
    
    #check if page has a search box
    retry = 0
    while retry<4:
        if wait_for_element(driver, (By.ID, 'input-title-autocomplete')):
            #print("found")
            break
        print("[Log]Search box not found...reloading...")
        driver.get(url)
        retry += 1
    if retry>=3:
        print(f"[Log]Retried {retry} times...Skipping")
        problem += 1
        return False

    #search box
    search_box = driver.find_element(By.ID, 'input-title-autocomplete')
    #clear search
    clear_button = driver.find_elements(By.ID, 'clear-title-localized')
    if len(clear_button)>0:
        clear_button = clear_button[0]
        clear_button.click()
    # clear + search for title name
    search_key = title_name
    search_box.send_keys(search_key)

    #search button
    search_button = driver.find_element(By.ID, 'title-location-search-btn')
    search_button.click()
    #check if the title is valid
    while wait_for_element(driver, (By.XPATH, '//div[text()="Please enter a valid job title"]'),t=1):
        driver.find_element(By.ID, 'clear-title-localized').click()
        if len(search_key.split(" "))<=1:
            print(f"[Log]All search keys are invalid...")
            return False
        search_key = shorten(search_key)
        print(f"[Log]Search key invalid...shortening to {search_key}")
        search_box.send_keys(search_key)
        search_button.click()
    time.sleep(1)

    #check if page is loaded
    retry = 0
    while wait_for_element(driver, (By.XPATH, '//h1[@text="How to become a Network Engineer"]')) and retry<3:
        time.sleep(1)
        retry+= 1
    if retry>=3:
        return False
    if not wait_for_element(driver, (By.ID, 'overview')):
        print(f"[Log]{title_name} Cannot Load Overview Tab")
        salaries_tab = driver.find_element(By.ID, 'salaries')
        salaries_tab.click()
        descrpt = None

        retry = 0
        while not wait_for_element(driver, (By.TAG_NAME, 'h1')) and retry<3:
            time.sleep(1)
            retry+= 1
        Title = driver.find_element(By.TAG_NAME, 'h1').text
        Title = " ".join(Title.split(" ")[:-4])
        responsibility = None

    else:
        #changing to overview page
        overview_tab = driver.find_element(By.ID, 'overview')
        overview_tab.click()
        if not wait_for_element(driver, (By.XPATH, '//div[@data-testid="what-does-text"]/p')):
            print(f"[Log]{title_name} Failed...Cannot Load Overview Page")
            return False

        ## check if the page actually changes
        time.sleep(1)
        retry = 0
        while driver.find_element(By.XPATH, '//span[@aria-live="assertive"]').text != "Content has loaded" and retry<3:
            time.sleep(1)
            retry+= 1
        Title = driver.find_element(By.TAG_NAME, 'h1').text
        Title = " ".join(Title.split(" ")[3:-1])

        descrpt = driver.find_element(By.XPATH, '//div[@data-testid="what-does-text"]/p').text
        responsibility = driver.find_element(By.XPATH, '//div[h2[starts-with(text(),"Working as")]]/div/ul').text
    salary = driver.find_element(By.XPATH, '//div[@data-testid="avg-salary-value"]').text.strip("$").replace(",","")\
        +" "+Select(driver.find_element(By.XPATH, '//select[@id="pay-period-selector"]')).first_selected_option.get_attribute("value")

    #change page
    career_advice_tab = driver.find_element(By.ID, 'career-advice')
    career_advice_tab.click()
    #check if page is loaded
    if not wait_for_element(driver, (By.XPATH, '//div[@data-testid="job-skills"]/div/ul')):
        print(f"[Log]{title_name} Failed...Cannot Load Career Advice Page")
        required_skills = []
        related_titles = []
    else:
        retry = 0
        while driver.find_element(By.XPATH, '//span[@aria-live="assertive"]').text != "Content has loaded" and retry<3:
            time.sleep(1)
            retry+= 1
        required_skills = driver.find_element(By.XPATH, '//div[@data-testid="job-skills"]/div/ul').text.split("\n")
        related_titles = [ele.text for ele in driver.find_elements(By.XPATH, '//a[@data-a11y-tabtest="related-title-career-advice"]')]

    title_info["Indeed_record"] = {}
    if Title != 'Network Engineer':
        title_info["Indeed_record"]["name"] = Title
        title_info["Indeed_record"]["description"] = descrpt
        title_info["Indeed_record"]["responsibility"] = responsibility
        title_info["Indeed_record"]["salary"] = salary
        title_info["Indeed_record"]["related_titles"] = related_titles
        title_info["Indeed_record"]["required_skills"] = required_skills
    
    # save
    with open("indeed_title_extract.jsonl","a") as file:
        json.dump(title_info,file)
        file.write("\n")
    print(f"[Log]{title_name} Success!")
    # checkpoint
    with open("indeed_title_checkpoint.txt","a") as file:
        file.write(title_name+"\n")
    time.sleep(3)
    #except:
        #return False
    return True
    
def main():

    with open("data/lightcast_all_titles.json") as file:
        title_list = json.loads(file.read())

    taboo = ["Assistant","Intern","Support","Team","Lead"]

    with open("indeed_title_checkpoint.txt") as file:
        checkpoint = set(file.read().strip().split("\n"))

    title_list = [i for i in title_list if i["name"] not in checkpoint]

    N = 5
    drivers = [driver_setup() for _ in range(N)]
    chunks = np.array_split(title_list,N)

    with ThreadPoolExecutor(max_workers=N) as executor:
        executor.map(Indeed_Crawl, chunks, drivers)

    [driver.quit() for driver in drivers]

main()