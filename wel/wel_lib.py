import sys
import urllib2
import re
import commands
import os
import codecs
import ConfigParser, os
import datetime
import csv
import hashlib

from abc import ABCMeta, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

#this class defines the structure of the base class
class helper_def:
	__metaclass__ = ABCMeta

	def __init__(self):
		return
		
	#generic method is used to load a configuration file	
	def load_config(self, file):
		config = ConfigParser.ConfigParser()
		config.readfp(open(file))
		if (config.has_section('url')):
			if(config.has_option('url', 'url_base')):
				self.url_base = config.get('url', 'url_base')
				print 'loading url_base: ' + self.url_base
			if(config.has_option('url', 'url_index')):
				self.url_index = config.get('url', 'url_index')
				print 'loading url_index: ' + self.url_index
		
		if (config.has_section('path')):
			if(config.has_option('path', 'dir_base')): 
				self.dir_base = config.get('path', 'dir_base')
		
			
		if(config.has_section('filename')):
			if(config.has_option('filename', 'dept_url_file')):
				self.dept_url_file = config.get('filename', 'dept_url_file')
				
			if(config.has_option('filename', 'dept_cd_file')):
				self.dept_cd_file = config.get('filename', 'dept_cd_file')	
				
			if(config.has_option('filename', 'page_url')):
				self.page_url = config.get('filename', 'page_url')
				
			if(config.has_option('filename', 'location_list')):
				self.location_list = config.get('filename', 'location_list')	
		


class helper(helper_def):
	
	current_day = None
	lang = None
	 
	def __init__(self, file, language):
		self.load_config(file)
		global current_day 
		global lang 
		global status_file_name
		global region
		global suburb
		
		current_day = datetime.date.today().strftime(u'%Y%m%d')
		lang = language
		
		if(lang == u'cn'):
			region = u'香港島'
			suburb = u'香港仔'
			
		elif(lang == u'en'):
			region = u'Hong Kong Island'
			suburb = u'Aberdeen'
		
		status_file_name = 'status_' + lang + '.log'
		
		self.dir_base = os.path.join(self.dir_base, current_day)
		if(not os.path.exists(self.dir_base)):
			print u'creating: ' + self.dir_base
			self.create_dir(self.dir_base)
			
		if(not os.path.isfile(os.path.join(self.dir_base, status_file_name))):
			print u'creating: ' + status_file_name
			self.create_new_file(os.path.join(self.dir_base, status_file_name))
		
	
	def load_config(self, file):
		return super(helper, self).load_config(file)

	def create_base_dir(self):
		return create_dir(super(helper, self).dir_base)

	def create_dir(self, path):
		try:
			if(os.path.exists(path)):
				return path
			else:
				os.makedirs(path)
		except IOError:
			print u'problem creating folder/file :', path
	
	def create_new_file(self, filename):
		try:
			print u'creating a new file named: ' + filename
			f = open(filename, 'w')
			f.close()
			return f
		except IOError:
			print u'problem creating file: ', filename
			return
	
	def write_line_to_file(self, filename, data):
		try:
			f = codecs.open(filename, u'a')
			f.write(data + u'\n')
			f.close()
		except IOError:
			print u'problem writing to file :', filename
			return

	def get_file_data(self, filename):
		try:
			f = codecs.open(filename, 'r', 'utf-8')
			return f
		except IOError:
			print 'problem reading data from file :', filename

	def write_data_to_file(self, filename, data):
		try:
			f = codecs.open(filename, 'w', 'utf-8')
			f.write(data)
			f.close()
		except IOError:
			print 'problem writing to file :', filename
	
	def change_lang(self, b):
		
		#expects a b b
		print u'changing language to ' + lang
		try:
			element = WebDriverWait(b, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, u'btnLang')))
			if lang.strip().lower() == u'cn':
				if element:
					if element.text.strip() == u'中文版':
						print u'clicking on element: ' + u'btnLang'
						element.click()	
			elif lang.strip().lower() == u'en':	
				if element:
					if element.text.strip() == u'ENG VERSION':
						print u'clicking on element: ' + u'btnLang'
						element.click()	
		except:
			pass
	
	def should_skip(self, location, specifier):
		if specifier.lower() == u'all':
			print u'processing all regions'
			return 0
				
		elif location.lower() == specifier.lower(): 	
			print u'processing ' + location.lower()
			return 0
		elif location.lower() <> specifier.lower():
			return 1
		
	def is_number(self, s):
		try:
			float(s)
			return True
		except ValueError:
			return False
	
	def list_to_csv(self, file_path, lst, mode=u'wb'):
		#this function expects a list of lists, or a list of tuples, just like a csv
		with codecs.open(file_path, mode) as csvfile:
			for line in lst:
				alist = list(line)
				writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
				writer.writerow([x.encode('utf-8') for x in alist])
		csvfile.close()	
	
	def tuple_to_csv(self, file_path, tuple, mode=u'wb'):
		#this function expects a list of lists, or a list of tuples, just like a csv
		with codecs.open(file_path, mode) as csvfile:
			alist = list(tuple)
			writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
			writer.writerow([x.encode('utf-8') for x in alist])
		csvfile.close()	

	def csv_to_list(self, file_path):
		#returns a list of lists for a given csv
		lst = []
		with codecs.open(file_path, u'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',', quotechar='"')
			for row in reader:
				uniList = [x.decode('utf-8') for x in row]
				lst.append(uniList)		
		csvfile.close()
		return lst
	
	def is_processed(self, department, page):
		print 'checking: ' + region + ', ' +  suburb + ', ' +  department + ', ' +  page
		status_log = os.path.join(self.dir_base, status_file_name)
		if os.path.exists(status_log):
			log_list = self.csv_to_list(status_log)
			
			for row in log_list:
				if row[0].lower().strip() == region.lower().strip() and row[1].lower().strip() == suburb.lower().strip() and row[2].lower().strip() == department.lower().strip() and row[3].lower().strip() == page.lower().strip():
					return 1	
			return 0
		
			
	def post_check(self,checksum):
		print 'checking: ' + checksum
		status_log = os.path.join(self.dir_base, status_file_name)
		if os.path.exists(status_log):
			log_list = self.csv_to_list(status_log)
			
			for row in log_list:
				if row[4].lower().strip() == checksum.lower().strip():
					return 1	
			return 0				
										
	def get_dept_url_list(self):
		link_file_path = os.path.join(self.dir_base, self.dept_url_file)
		link_file = self.create_new_file(link_file_path)
		
		b = self.get_new_browser()
		b.get(self.url_index)
		data = b.page_source
		soup = BeautifulSoup(data)
		page_links = soup.select(u'.menu > a')
		dept_list = []
		
		for link in page_links:
			dept_link = link.get(u'href')
			match = re.search( '&sp=(\d+)', dept_link.strip())
			dept_cd = ''
			if match:
				dept_cd = match.group(1)
				tuple = dept_cd, dept_link
				dept_list.append(tuple)
		
		self.list_to_csv(link_file_path, dept_list)
		b.quit()
		
		
	def get_location_list(self, ):
		#open the first link in the department list
		link_file_path = os.path.join(self.dir_base, self.dept_url_file)
		link_file = self.csv_to_list(link_file_path)
		
		
		#get the first link in the file
		link = link_file[0][1]
		b = self.get_new_browser()
		
		print 'fetching: ' + self.url_index
		b.get(self.url_index)
		
		print 'fetching: ' + link
		b.get(link)
		
		#change the language
		self.change_lang(b)
		
		data = b.page_source
		soup = BeautifulSoup(data)
		region_elements = soup.select(u'div.sideMenu > div.level-1 > a')
		
		loc_file = os.path.join(self.dir_base, 'locations_' + lang + '.txt')
		self.create_new_file(loc_file)
		
		for element in region_elements:
			print 'going back to depatment index page'
			print 'fetching: ' + link
			b.get(link)
		
			print u'processing: ' + element.get_text()
			
			region_name = element.get_text()
			
			region_element = b.find_element_by_link_text(region_name)
			match = re.search(u'callmenu\((.*)\)', str(element))
			if not match:
				continue
			
			region_id = match.group(1).replace(u"'", u"")
			region_element.click()
			data = b.page_source
			soup = BeautifulSoup(data)
			lookup = u'div#' + region_id + ' a'
			suburb_elements = soup.select(lookup)
		
			lst = []
		
			for s1 in suburb_elements:
				tuple = region_name, s1.get_text().strip(), s1.get('href').strip()
				lst.append(tuple)
		
				lookup = u'div#' + region_id + ' a'
				suburb_elements = soup.select(lookup)
	
			self.list_to_csv(loc_file, lst, 'ab')
			
		b.quit()
			
		
		
	def get_dept_init_page(self, region = u'all', suburb = u'all'):

		
		#get the locations from the locations file
		loc_file_path = os.path.join(self.dir_base, 'locations_' + lang + '.txt')
		loc_file = self.csv_to_list(loc_file_path)
			
		file = self.csv_to_list(os.path.join(self.dir_base, self.dept_url_file))
		
		
		#for each location
		for loc in loc_file:
		
			#check if we should be skipping this locations
			if self.should_skip(loc[0], region)==1:
				continue
			
			if self.should_skip(loc[1], suburb)==1:
				continue
				
			#create the location directory
			loc_dir = os.path.join(os.path.join(self.dir_base, loc[0]), loc[1])
			self.create_dir(loc_dir)
			
			#get a new b
			b = self.get_new_browser()
			
			#go to the index page
			b.get(self.url_index)
			
			#change the language of the browser for the session
			self.change_lang(b)
			
			#for each department
			for line in file:
				dir = os.path.join(loc_dir, line[0])
				self.create_dir(dir)
				
				#get the page
				b.get(line[1])
				
				#get the page a second time
				b.get(line[1])
				
				#get the page source
				print 'getting the page source'
				data = b.page_source
				
				#bypass the splash screen
				self.bypass_splash(data, b, loc[0].strip(), loc[1].strip())	
				
				#get the page a third time (defaults to index after changing language)
				print u'fetching: ' + line[1]
				b.get(line[1])
	
				#get the page source
				print 'getting the page source'
				data = b.page_source
				
				#soup that data
				soup = BeautifulSoup(data)
			
				newfile = u'1_' + lang + '.html'
				self.write_page_to_file(dir, newfile, soup.prettify())
				self.write_page_to_file(dir, u'1.txt', line[1])
				
				self.log_status(loc[0], loc[1], line[0], newfile)	
				
			b.quit()
	
		
	def get_item_data(self, page_no = 1, region = u'all', suburb = u'all', delta = 1, output_file_name='product_list.csv'):
		#get the locations from the locations file
		loc_file_path = os.path.join(self.dir_base, 'locations_' + lang + '.txt')
		file = self.csv_to_list(loc_file_path)
		
		output = os.path.join(self.dir_base, output_file_name)
		self.create_new_file(output)
		tuple = u'department', u'product_id', u'product_brand', u'product_desc', u'product_size',u'retail_price', u'special_price', u'promotion', u'product_url'
		self.tuple_to_csv(output, tuple, u'ab')
		
		for line in file:
			if self.should_skip(line[0], region)==1:
				continue
			
			if self.should_skip(line[1], suburb)==1:
				continue
			
			loc_path = os.path.join(self.dir_base, os.path.join(line[0], line[1]))
			print 'processing path: ' + loc_path
			
			
			for root, dirs, files in os.walk(loc_path):
				
				for dir in dirs:
					path = os.path.join(loc_path,dir)
					for root, dirs, files in os.walk(path):
						for file in files:
							if file[-5:] == '.html':
								html_file_path = os.path.join(path, file)
								print u'processing file: ' + html_file_path
								html_data = self.get_file_data(html_file_path)
								soup = BeautifulSoup(html_data)
								html_data.close()
								
								department = soup.find('h1', class_='left_menu_list_title').get_text(strip=True)

								result = soup.select(u'div.productRow > div.productCol')
	
								for line in result:
									retail_found = 0
									
									product_url 	= u''
									product_id 		= u''
									product_brand 	= u''
									product_desc 	= u''
									retail_price 	= u''
									special_price 	= u''
									product_size 	= u''
									product_promo	= u''

									
									product_brand = line.dl.dt.strong.get_text(strip=True)
									det_list = line.dl.dt.get_text("|",strip=True).split("|")
									product_desc = det_list[len(det_list)-2].strip()
																
									for el in line.dl.dd.find_all('a'):
										product_url = el.get('href')
										match = re.search('&sp=([a-z]\d+)', product_url)
										if match:
											product_id = match.group(1)	
										
									retail_price = None
									try:
										retail_price = line.dl.findNextSibling().dd.b.get_text(strip=True)
									except:
										pass
										
									if retail_price:
										retail_found = 1
								
									if retail_found == 1:
										special_price =  line.dl.findNextSibling().dd.strong.get_text(strip=True)
									else:
										retail_price = line.dl.findNextSibling().dd.strong.get_text(strip=True)
								
					
									product_size = line.dl.dt.find("span", class_="colorGray").get_text(strip=True)
									
									promo = line.find("dl", class_="SpecialPro")
									if promo:
										product_promo = line.find("dl", class_="SpecialPro").dd.get_text(strip=True)
								
									tuple = department, product_id, product_brand, product_desc, product_size, retail_price, special_price, product_promo, product_url
									
									self.tuple_to_csv(output, tuple, u'ab')
							
									
		
		
												
	def get_all_pages(self, page_no = 1, region = u'all', suburb = u'all', delta = 1):
		b = self.get_new_browser()
		
		#go to the index page
		b.get(self.url_index)
		
		#change the language of the browser for the session
		self.change_lang(b)
		
		#get the locations from the locations file
		loc_file_path = os.path.join(self.dir_base, 'locations_' + lang + '.txt')	
		file = self.csv_to_list(loc_file_path)

		for line in file:
			if self.should_skip(line[0], region)==1:
				continue
			
			if self.should_skip(line[1], suburb)==1:
				continue
				
			loc_path = os.path.join(self.dir_base, os.path.join(line[0], line[1]))
				
			for root, dirs, files in os.walk(loc_path):
				for dir in dirs:
					path = os.path.join(loc_path,dir)
					durl = self.get_dept_url(str(dir))
						
					for root, dirs, files in os.walk(path):
						for file in files:
							if str(page_no) + u'.txt' == file.strip():
								
								url_file_path = os.path.join(path, str(page_no) + u'.txt')
								urls = self.get_file_data(url_file_path)
								url = ''
								for i in urls:
									url = i
									break
								urls.close()
								#first get to the department page
								b.get(durl)
								#get past the index redirect
								b.get(durl)
								#get the page source
								data = b.page_source
								#bypass the splash screen
								self.bypass_splash(data, b, line[0], line[1])
								
								#get the next page
								b.get(url)
								
								#bypass the 404 error page
								b.get(url)

								#get the source containing the items
								data = b.page_source
								
								#get source file but do not write it
								html_file = str(page_no) + u'_' + lang + '.html'
								html_path = os.path.join(root, html_file)	
									
								self.next(root, str(dir), durl, html_path, b, page_no, 1, line[0], line[1], delta, 0)		
					
		b.quit()			
				
	
	def get_next_link(self, soup, page_no):
		print 'getting next link' 
		all_links = soup.select('#setpage_1 > a') 
		
		next_page_link = soup.select('#setpage_1 > a') 
		return_link = None
		
		for link in all_links:
			if (str(page_no) == link.get_text(strip=True)):
				return_link = link.get('href')	
				break		
		
		if return_link == None:
			for link in all_links:
				if link:
					if link.get('class'):
						if ('iconNext' == link.get('class')[0]):
							return_link = link.get('href')	
		if return_link:
			print u'found: ' + return_link
			return return_link
		else:
			print 'no link found'
			return
	
	def next(self, dir, dept_cd, durl, filepath, b, page_no, attempt, delta = 1, last=0):
		try:
			print 'processing region: ' + region + ' suburb: ' + suburb + ' department: ' + dept_cd + ' page: ' + str(page_no)
		
			next_page_no = page_no+1
		
			newfilename = str(next_page_no) + u'_' + lang + '.html'
		
			data = self.get_file_data(filepath)
			soup = BeautifulSoup(data)
			data.close()
		
			next_page_link = soup.select('#setpage_1 > a') 
			link = None
			skip = 0
		
			#skip what we dont need
			print 'delta = ' + str(delta)
			if delta == 1:
				if(self.is_processed(dept_cd, newfilename) == 1):
					skip = 1
					print newfilename + ' already processed; skipping'
				else:
					print newfilename + ' not processed, continuing to process'
				
			link = self.get_next_link(soup, next_page_no)
			
		
			if link:
				if skip == 0:
					url = self.url_base + link
					print u'link found'
					print 'link: ' + url

					print u'fetching: ' +  url
					b.get(url)
				
					print u'getting page source'
					data = b.page_source
				
					self.bypass_splash(data, b)
				
					print u're-fetching: ' + url
					b.get(url)
			
					print u'getting page source'
					data = b.page_source
	
					print u'writing data to ' + newfilename				
					self.write_page_to_file(dir, newfilename , data)
					
					newfilepath = os.path.join(dir, newfilename)
					data = self.get_file_data(newfilepath)
					soup = BeautifulSoup(data)
					data.close()
					checksum = hashlib.md5(str(soup.select('div.productRow'))).hexdigest()
				
					if self.post_check(checksum) == 1:
						print 'Body checksum already processed'
						print 'We are in some kind of infinite loop'
						return
				
					self.log_status(dept_cd, newfilename, checksum, u's')
				
					#write the url
					print u'writing url to ' + str(next_page_no) + u'.txt'
					self.write_page_to_file(dir, str(next_page_no) + u'.txt', url)	
				
					#get the next page
					print u'get next page'
			else:
				print 'No link found, processing next department'
				return
	
			self.next(dir, dept_cd, durl, os.path.join(dir, newfilename), b, next_page_no, 1, delta, last)
			
		except:
			attempt += 1
			if attempt <= 4:
				print u'something went wrong trying again this is attempt no. ' + str(attempt)
				self.next(dir, dept_cd, durl, filepath, b, page_no, attempt, delta)
			else:
				print u'giving up on this .... pass'
				return
			
	def get_item_detail(self, csv_file_path):
		b = self.get_new_browser()		
		with codecs.open(csv_file_path, u'rb') as csv_file:
			reader = csv.reader(csv_file, delimiter=',', quotechar='"')
			#skip the header
			next(reader)
			row = next(reader)
			productList = [x.decode('utf-8') for x in row]
			url = productList[8]
			b.get(url)
			data = b.page_source
			self.bypass_splash(data, b)
			b.get(url)
			data = b.page_source
			soup = BeautifulSoup(data)
			elements = soup.select('div.htmlPath')
			if elements: 
				for item in elements:
					list = item.get_text("|",strip=True).split("|")
					cats = list[len(list)-2] + ' ' + list[len(list)-1]
					print cats
					
			for row in reader:
				productList = [x.decode('utf-8') for x in row]
				url = productList[8]
				b.get(url)
				data = b.page_source
				soup = BeautifulSoup(data)
				elements = soup.select('div.htmlPath')
				if elements: 
					for item in elements:
						list = item.get_text("|",strip=True).split("|")
						cats = list[len(list)-2] + ' ' + list[len(list)-1]
						print cats
						
			csv_file.close()
		
		#b.get(product_url)
		#data = b.page_source
		#self.bypass_splash(data, b, region, suburb)	
		#b.get(product_url)
		#product_
		#product_soup = BeautifulSoup(product_data)
		#hierarchy_elements = product_soup.select('div.htmlPath')
		#if hierarchy_elements:
		#for item in hierarchy_elements:
		#	hierarchy_list = item.get_text("|",strip=True).split("|")
		#	hierarchy = hierarchy_list[len(hierarchy_list)-2] + ' ' + hierarchy_list[len(hierarchy_list)-1]
						
	
	def log_status(self, dept_cd, filename=u'', checksum=u'', status = u's'):
		log_file = os.path.join(self.dir_base, status_file_name)
	
		if(not os.path.exists(log_file)):
			self.create_new_file(log_file)
			
		tuple = region, suburb, dept_cd, filename, checksum, status, datetime.datetime.now().strftime(u'%Y%m%d_%H%M')

		self.tuple_to_csv(log_file, tuple, u'ab')
				
	def get_dept_url(self,dept_code):
		link_file_path = os.path.join(self.dir_base, self.dept_url_file)
		data = self.csv_to_list(link_file_path)
		for line in data:
			if line[0] == str(dept_code).strip():
				return line[1]
	
	def write_page_to_file(self, dir, filename, data):
		newfile = os.path.join(dir, filename)
		self.create_new_file(newfile)
		self.write_data_to_file(newfile, data)	
		
		
	def get_new_browser(self):
		profile = webdriver.FirefoxProfile()
		profile.set_preference('permissions.default.image', 2)
		profile.set_preference('dom.max_chrome_script_run_time', 0)
		profile.set_preference('dom.max_script_run_time', 0)
		profile.set_preference('permissions.default.stylesheet', 2)
		b = webdriver.Firefox(profile)
		b.set_page_load_timeout(120)   
		return b
			
	
	def bypass_splash(self, data, b):
		if data:
			print u'bypassing the splash screen'
			isSplash = 0
			soup = BeautifulSoup(data)
			deliv = soup.select(u'.heading')
			if len(deliv) == 0:
				return 
			
			if deliv[0].get_text().strip() == u'GUEST VISIT' or deliv[0].get_text().strip() == u'未登記用戶瀏覽':
				print u'found: ' + deliv[0].get_text().strip()
				isSplash = 1
					
			if isSplash == 1:
				try:
					print u'trying to find ' + region
					element = WebDriverWait(b, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, region)))
					if element:
						print u'clicking on element: ' + region
						element.click()	
					else:
						print u'could not find element ' + region
				
					print u'trying to find ' + suburb
					element = WebDriverWait(b, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, suburb)))
					if element:
						print u'clicking on element: ' + suburb
						element.click()	
					else:
						print u'could not find element ' + suburb
				except:
					pass
		else:
			print u'There is no data'

		
helper_def.register(helper)
x = helper('./config.ini', 'en')
x.get_dept_url_list()
x.get_location_list()
x.get_dept_init_page(u'Hong Kong Island', u'Aberdeen')
x.get_all_pages(1, u'Hong Kong Island', u'Aberdeen', 1)
x.get_item_data( 1, u'Hong Kong Island', u'Aberdeen', 1, output_file_name='product_list_en.csv')
x.get_item_detail(r'./product_list_en.csv')

#x = helper('./config.ini', 'cn')
#x.get_dept_url_list()
#x.get_location_list()
#x.get_dept_init_page(u'香港島', u'香港仔')
#x.get_all_pages(1, u'香港島', u'香港仔', 1)
#x.get_item_data( 1, u'香港島', u'香港仔', 1, output_file_name='product_list_cn.csv')



