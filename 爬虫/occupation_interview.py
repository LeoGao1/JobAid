#各种import， time，json, Review是另外一个class（原来这个东西是python 2.7的所以有新建class）
import time
import json
from bs4 import BeautifulSoup
import re
#selenium是爬一个网站多个subdirectory必备，它可以搞定登录这些事情，记得下载chromedriver这东西
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import csv

#这账号是我建的，直接用
username = "1002423907@qq.com" # your email here
password = "1234567890" # your password here

pages=2
occupation="Data Scientist"

def make_url(occupationName):
    origin="https://www.glassdoor.com/Interview/"
    occu=occupation.lower()
    occu=occu.replace(' ','-')
    print(occu)
    origin=origin+occu+"-interview-questions-SRCH_KO0,14"
    print(origin)
    return origin

#这里就是初始化driver
def init_driver():
    driver = webdriver.Chrome(executable_path = "./chromedriver")
    driver.wait = WebDriverWait(driver, 10)
    return driver
#enddef

def login(driver, username, password):
    driver.get("http://www.glassdoor.com/profile/login_input.htm")
    try:
		#注意那些located，这些都是直接进网站里面根据html attribute搞出来的
        user_field = driver.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        pw_field = driver.find_element_by_id("userPassword")
        #login_button = driver.find_element_by_class_name("gd-btn gd-btn-1 minWidthBtn")
        user_field.send_keys(username)
        user_field.send_keys(Keys.TAB)
        time.sleep(1)
        pw_field.send_keys(password)
        time.sleep(1)
        #login_button.click()
        driver.find_element_by_xpath('//button[@type="submit"]').click()

    except TimeoutException:
        print("TimeoutException! Username/password field or login button not found on glassdoor.com")
#enddef

def search(driver,occupationName):
    driver.get("https://www.glassdoor.com/Interview/index.htm")
    try:
        print("Start searching for "+occupation)
        search_field = driver.find_element_by_id("KeywordSearch")
        location_field=driver.find_element_by_id("LocationSearch")
        search_field.send_keys(occupationName)
        time.sleep(1)
        location_field.send_keys(" ")
        time.sleep(1)
        search_btn= driver.find_element_by_id("HeroSearchButton")
        search_btn.click()
        #return current url of driver
        print(driver.current_url)
        return driver.current_url
    except TimeoutException:
        print("TimeOut....")

def get_data(driver, URL, startPage, endPage, data, refresh):
    if (startPage > endPage):
        return data
	#endif
    print ("\nPage " + str(startPage) + " of " + str(endPage))
    currentURL = URL + "_IP" + str(startPage) + ".htm"
    driver.get(currentURL)
    time.sleep(2)
    HTML = driver.page_source
    soup = BeautifulSoup(HTML, "html.parser")
    questions =soup.find_all('div',id=lambda x: x and x.startswith('InterviewQuestionResult'))
    if questions:
        data=parse_questions_HTML(questions, data)
        print ("Page " + str(startPage) + " scraped.")
        if (startPage % 10 == 0):
            print ("\nTaking a breather for a few seconds ...")
            time.sleep(10)
		#endif
        get_data(driver, URL, startPage + 1, endPage, data, True)
    else:
        print ("Waiting ... page still loading or CAPTCHA input required")
        time.sleep(3)
        get_data(driver, URL, startPage, endPage, data, False)
    
    return data




def parse_questions_HTML(questions,data):
    for question in questions:
        company=''
        q='-'
        cs=	question.find_all("span", { "class" : "authorInfo"})
        if cs:
            text= cs[0].find('a').contents[0]
            aa=text.split()
            bb=aa.index('was')-aa.index('at')
            company=''
            for i in range (1,bb):
                company+=aa[aa.index('at')+i]
                #print(company)
        details = question.find("p", { "class" : "questionText h3"})
        if details:
            q=details.getText()
            #q=details.decode('utf-8')
            #print(q)
        
        r=(company,q)
        data.append(r)
    return data

def csv_export(data):
    with open(occupation+'.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['company Name','Question'])
        for row in data:
            csv_out.writerow(row)
    out.close()


if __name__ == "__main__":
	driver = init_driver()
	time.sleep(3)
	print ("Logging into Glassdoor account ...")
	login(driver, username, password)
	time.sleep(5)
	currentURL=make_url(occupation)
	time.sleep(1)
	print ("\nStarting data scraping ...")
	data = get_data(driver, currentURL, 1, pages, [], True)
	print ("\nExporting data to " + occupation + ".csv")
	csv_export(data)
	driver.quit()