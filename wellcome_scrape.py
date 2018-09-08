#!/usr/bin/python2.7 -tt

import sys
import urllib2
import re
import commands
import os
import codecs
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
import HTMLParser
import time

def get_dept(url):
	## get file-like object for url
	browser = get_new_browser()
	
  	browser.get(url)
  	
  	data = browser.page_source

	browser.quit()
	
	filename = get_url_file_name(url)
	
	#get the current directory
	curnt_dir = os.path.abspath(os.path.curdir)
	
	#create a new file for the main index.html in the current directory
	new_file = os.path.join(curnt_dir, filename)
	create_new_file(new_file)
	
	#write the index.html markup to the new file
	write_data_to_file(new_file, data)
	
	#readout the data from the new file
	pagedata = get_file_data(new_file)
	
	#soupify the data from the file (parse)
	soup = soupify(pagedata)
	
	#write the soupified prettified text to a file.
	soupfilename = filename.replace('.html', '') + '_parsed.html'
	create_new_file(soupfilename)
	write_data_to_file(soupfilename, soup.prettify())

	#get the child links (<a>) of list items <li> of class type .subNavItem
	soup1 = soup.select('.subNavItem > a')
	
	#extract the base url from the main (parent) index.html full url
	html_parser = HTMLParser.HTMLParser()
	unescaped = html_parser.unescape(url)
	baseurl = unescaped[0:findnth(unescaped ,'/'  ,2)]
	
	#create a folder called dept (short for department)
	dept_dir = os.path.join(curnt_dir, 'dept')
	create_dir(dept_dir)
	
	#create a file in the dept folder to hold the list of urls we iterate over
	url_file_path = os.path.join(dept_dir , 'url_index.txt')
	create_new_file(url_file_path)
		
	#loop through the list of urls and download their contents to an html file in dept folder
	for s1 in soup1:
		url = s1.get('href')
	
		#append url to url_file
		write_line_to_file(url_file_path, baseurl + url)
		
	#open the url file and loop through department urls it downloading each page (just the raw data)
	f = codecs.open(url_file_path, 'r', 'utf-8')

	

	for line in f:
  	
		browser = get_new_browser()
		
  		browser.get(line)
		
  		bypass_splash_screen(browser)
		
		browser.get(line)
  		browser.refresh()
		
		#get the source code from the page  	
  		data = browser.page_source

		match = re.search('^.*hs_dept_id=(\d+).*$' , line)
		
		dept_code = ('00' + match.group(1))[-3:]

		#create a folder for each department
		dept_folder = os.path.join(dept_dir , dept_code)
		create_dir(dept_folder)		
		
		#create the raw dept file
		dept_file = os.path.join(dept_folder , dept_code + '_raw.html')
		
		#write the html to the html_file
		create_new_file(dept_file)
		write_data_to_file(dept_file, data)
		parse_raw_file(dept_file)
		
		#create a url_index.txt file for the current department in the current departments folder
		dept_url_file_path = os.path.join(dept_folder , 'url_index.txt')
		create_new_file(dept_url_file_path)

		#append the current url to the dept_url_file_path
		write_line_to_file(dept_url_file_path, line)
	
		get_dept_item_list(dept_folder, line, dept_code)

		#get item list data	
		item_list_path = os.path.join(dept_folder, 'item_list')
		get_item_url_list(item_list_path, dept_code, baseurl)
		get_item_img_list(item_list_path, dept_code, baseurl)
	
		#get item detail data
		items_path = os.path.join(item_list_path, 'items')
		get_item_detail_pages(items_path, dept_code, baseurl)

		browser.quit()
		
	
			
def parse_raw_file(file):
	#check that the file is a valid html file
	if (file[-8:] == 'raw.html'):
				
		#open the file and get the contents
		pagedata = get_file_data(file)
				
		#soupify the data from the file (parse)
		soup = soupify(pagedata)
				
		soupfilename = (file.replace('.html', '') + '_parsed.html')
		create_new_file(soupfilename)
		write_data_to_file(soupfilename, soup.prettify())
		
def parse_raw_files(folder):
	#parse all the pages in the dept folder
	for root, dirs, files in os.walk(folder):
		for name in files:
			#check that the file is a valid html file
			if (name[-8:] == 'raw.html'):
				
				#open the file and get the contents
				pagedata = get_file_data(os.path.join(folder, name))
				
				#soupify the data from the file (parse)
				soup = soupify(pagedata)
				
				soupfilename = os.path.join(folder, name.replace('.html', '') + '_parsed.html')
				create_new_file(soupfilename)
				write_data_to_file(soupfilename, soup.prettify())
	
	
def get_item_url_list(item_list_dir, dept_code, baseurl):
	print item_list_dir

	#create a folder to hold all the item data
	items_path = create_dir(os.path.join(item_list_dir, 'items'))
	
	#create a file in the items folder to hold the urls
	url_file_path = os.path.join(items_path , 'url_index.txt')
	create_new_file(url_file_path)

	#open the file and get the contents
	parsed_item_list = os.path.join(item_list_dir, dept_code + '_item_list_raw_parsed.html')
	pagedata = get_file_data(parsed_item_list)
	if pagedata:
		#the file has already been parsed therefore just get the links to product details
		
		#soupify the data from the file (parse)
		soup = soupify(pagedata)		
		
		#get the child links (<a>) of div with class type .brand
		soup1 = soup.select('.brand > a')
		
		#loop through the list of urls and download their contents to an html file in dept folder
		for s1 in soup1:
			url = s1.get('href')
	
			#append url to url_file
			write_line_to_file(url_file_path, baseurl + url)
		

def get_item_detail_pages(items_path, dept_code, baseurl):
	#open the url_index.txt file and iterate through it
	url_file_path = os.path.join(items_path , 'url_index.txt')
	
	#open the url file for reading
	f = codecs.open(url_file_path, 'r', 'utf-8')
	
	#create a new browser
	browser = get_new_browser()
	
	counter = 0
	
	for line in f:
		print line
		match = re.search('pdt_id=(\d+)$', line)
		if match:
			product_id = match.group(1)
		
			#create a folder for the product
			create_dir(os.path.join(items_path, product_id))
				
			#get the html file from the url
			browser.get(line)
			
			if (counter == 0):
				bypass_splash_screen(browser)
		
			#after bypassing the splash screen the site will take us back to index.html so we need to go back to the product page
			browser.get(line)
			#time.sleep(2)
		
			#get the source code from the page  	
  			data = browser.page_source
  						
			#create the raw item list file
			item_file = os.path.join(os.path.join(items_path, product_id) , product_id + '_raw.html')
			write_data_to_file(item_file, data)
			
			counter += 1
				
			#browser.quit()		
					
			parse_raw_file(item_file)



def get_item_img_list(item_list_dir, dept_code, baseurl):
	print item_list_dir

	#create a folder to hold all the item data
	items_path = create_dir(os.path.join(item_list_dir, 'items'))
	
	#create a file in the items folder to hold the urls
	img_file_path = os.path.join(items_path , 'img_index.txt')
	create_new_file(img_file_path)

	#open the file and get the contents
	parsed_item_list = os.path.join(item_list_dir, dept_code + '_item_list_raw_parsed.html')
	pagedata = get_file_data(parsed_item_list)
	if pagedata:
		#the file has already been parsed therefore just get the links to product details
		
		#soupify the data from the file (parse)
		soup = soupify(pagedata)		
		
		#get the child links (<a>) of div with class type .brand
		soup1 = soup.select("div.item-img-container.productImg > a > img" )	
		
		#loop through the list of urls and download their contents to an html file in dept folder
		for s1 in soup1:
			print s1.get('src')
			write_line_to_file(img_file_path, baseurl + s1.get('src'))		
		
		
					
def get_dept_item_list(dept_dir, dept_url, dept_code):
	#testing
	#python ./wellcome_scrape.py '/Users/danielmackie/Desktop/scrape/wellcome/dept/003'
	
	for root, dirs, files in os.walk(dept_dir):
		for name in files:
			#check that the file is a parsed html file
			if (name[-11:] == 'parsed.html'):
				
				#open the file and get the contents
				pagedata = get_file_data(os.path.join(dept_dir, name))
				
				#create a folder called items 
				dept_cd_dir = os.path.join(dept_dir, 'item_list')
				create_dir(dept_cd_dir)
				
				#create a file in the items folder to hold the url
				url_file_path = os.path.join(dept_cd_dir , 'url_index.txt')
				create_new_file(url_file_path)
				
				#the default product page url for wellcome
				url = dept_url.strip() + '#/hs_rec_per_page=10000&hs_sort=popularity&hs_srch_page_no=1&hs_dept_id=' + str(int(dept_code)) 
				
				#the url should be formatted in standard html encoding
				html_parser = HTMLParser.HTMLParser()
				unescaped = html_parser.unescape(url)
				
					
				#append url to url_file
				write_line_to_file(url_file_path, unescaped)
				
			 	#open the url file and loop through product list pages downloading each page (just the raw data)
				f = codecs.open(url_file_path, 'r', 'utf-8')
				
				for line in f:
					#create a new browser
					browser = get_new_browser()
				
					#get the html file from the url
					browser.get(line)
					bypass_splash_screen(browser)
		
					#after bypassing the splash screen the site will take us back to index.html so we need to go back to the product page
  					time.sleep(5)	
					browser.get(line)
					print line
  					#browser.refresh()
  					
  					#we need to allow time for the pages javascript to render all the content (30 seconds should be enough)
  					time.sleep(30)	
		
					#get the source code from the page  	
  					data = browser.page_source
  						
					#create the raw item list file
					dept_item_list_file = os.path.join(dept_cd_dir , dept_code + '_item_list_raw.html')
					write_data_to_file(dept_item_list_file, data)
				
					browser.quit()		
					
					parse_raw_file(dept_item_list_file)
		
	
def soupify(data):
	soup = BeautifulSoup(data)
	return soup
    
def get_new_browser():
	profile = webdriver.FirefoxProfile()
	
	profile.set_preference("permissions.default.image", 2)
	profile.set_preference("dom.max_chrome_script_run_time", 0)
	profile.set_preference("dom.max_script_run_time", 0)
	profile.set_preference("permissions.default.stylesheet", 1)
	browser = webdriver.Firefox(profile)
	browser.maximize_window()
	browser.set_page_load_timeout(30)   
	return browser
    
def bypass_splash_screen(browser):
	try:
		element = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'hk')))
		if element:
			element.click()
  			
		element = WebDriverWait(browser, 10).until(	EC.element_to_be_clickable((By.ID, 'district_7')))
		if element:
			element.click()
	except:
		pass
	
def main():
	#get_dept_item_list(sys.argv[1], sys.argv[2], sys.argv[3])
	#get_item_url_list(sys.argv[1], sys.argv[2], sys.argv[3])
	#get_item_img_list(sys.argv[1], sys.argv[2], sys.argv[3])
	#get_item_detail_pages(sys.argv[1], sys.argv[2], sys.argv[3])
	get_dept(sys.argv[1])
	
def findnth(haystack, needle, n):
    parts= haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)
	

def get_url_file_name(url):
	match = re.search(r'(?:.(?!\/))+$', url)
	filename = match.group()[1:] 
	filename = filename.replace('.html', '') + '.html'
	return filename
	
	
def create_dir(path):
	try:
		if(os.path.exists(path)):
			return path
		else:
			os.mkdir(path)
	except IOError:
		print 'problem creating folder/file :', path
	
	return path
		

def create_new_file(filename):
	try:
		print 'creating a new file named: ' + filename
		f = open(filename, 'w')
		f.close()
		return f
	except IOError:
		print 'problem creating file: ', filename
	
	
def write_data_to_file(filename, data):
	try:
		f = codecs.open(filename, 'w', 'utf-8')
		f.write(data)
		f.close()
	except IOError:
		print 'problem writing to file :', filename
		
def write_line_to_file(filename, data):
	try:
		f = codecs.open(filename, 'a')
		f.write(data + '\n')
		return f
	except IOError:
		print 'problem writing to file :', filename
		
def get_file_data(filename):
	try:
		f = codecs.open(filename, 'r')
		a = f.read()
		return a
	except IOError:
		print 'problem reading data from file :', filename
				
#If this is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
	main()