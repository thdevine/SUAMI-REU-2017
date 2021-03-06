#meeting.py
#email: ...............

from pandas_datareader import data as web
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
import time

#filepath removed
def setup_driver():
	chrome_path = "................"
	driver  = webdriver.Chrome(chrome_path)

	return driver


def scrape_company_list( driver ):
	
	companies = []

	driver.get("http://money.cnn.com/data/dow30/")
	time.sleep(2)

	for i in range(2, 32):							
		ingredient = driver.find_element_by_xpath("""//*[@id="wsod_indexConstituents"]/div/table/tbody/tr[""" + str(str(str(i))) + """]/td[1]/a""")
		companies.append( ingredient.text )
	
	time.sleep(2)


	for c in companies:
		print c

	return companies



def scrape_derivatives_data( driver, companies ):
	k_list, k_s = [], []
	p_list, p_s = [], []

	for ticker in companies:
		driver.get( "https://finance.yahoo.com/quote/" +str(ticker)+ "/options?p=" +str(ticker) )
		time.sleep(2)
		time.sleep(2)
		driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/div/div[1]/select/option[5]""").click() #select an exp date
		time.sleep(3)
		driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/section[2]/div[2]/table/thead/tr/th[10]""").click() #click on open interest twice
		time.sleep(2)
		driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/section[2]/div[2]/table/thead/tr/th[10]""").click()

		for i in range(1, 6):
			#get strike prices 
			juice  = driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/section[2]/div[2]/table/tbody/tr[""" +str(i)+ """]/td[3]/a""")							
			k_s.append( juice.text )

			#get option prices
			sauce  = driver.find_element_by_xpath("""//*[@id="quote-leaf-comp"]/section/section[2]/div[2]/table/tbody/tr[""" +str(i)+ """]/td[4]""")
			p_s.append( sauce.text )									

		k_list.append(k_s)
		p_list.append(p_s)

		time.sleep(3)

	print "k_list is\n", k_list
	print "p_list is\n", p_list

	return k_list, p_list



def scrape_stock_prices( driver, companies):

	date = '2017-7-24'
	prices = pd.DataFrame( web.DataReader(companies, 'google', date, date)['Close'] )

	return prices



def main():

	driver    		= setup_driver()
	
	companies 		= scrape_company_list( driver )

	stock_prices  	= scrape_stock_prices( driver, companies )

	k_list, plist   = scrape_derivatives_data( driver, companies )

	

main()

