from googlesearch import search
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from bs4.element import Comment
# from textblob import TextBlob
import boto3
import json
import sys
import asyncio
import concurrent.futures
import time

def get_reviews(query, numRes):
	list = []
	for j in search(query, tld="com", lang='en', num=numRes, stop=numRes, pause=2):
		list.append(j)
	return list

# attempts to get HTML/XML, returns text content, none otherwise
def get_url(url):
	try:
		with closing(get(url, stream=True)) as resp:
			if is_good_response(resp):
				return resp.content
			else:
				return None

	except RequestException as e:
		log_error('Error during requests to {0} : {1}'.format(url, str(e)))
		return None

# returns True if response seems to be HTML, False otherwise
def is_good_response(resp):
	content_type = resp.headers.get('Content-Type')
	if not content_type:
		return False
	content_type = content_type.lower()
	return (resp.status_code == 200 
			and content_type is not None 
			and content_type.find('html') > -1)

# prints errors
def log_error(e):
	print(e)

#returns True if tag is visible, False otherwise
def tag_visible(element):
	if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
		return False
	if isinstance(element, Comment):
		return False
	return True

def text_from_html(body):
	soup = BeautifulSoup(body, 'html.parser')
	texts = soup.findAll(text=True)
	visible_texts = filter(tag_visible, texts)
	return u" ".join(t.strip() for t in visible_texts)

def check_meta_review(soup):
	head = soup.find("head")
	if not head:
		return False
	metas = head.find_all("meta")
	for meta in metas:
		if 'content' in meta.attrs:
			content = meta['content']
			if (content.find('review') != -1 or content.find('Review') != -1) and not (content.find('preview') != -1 or content.find('Preview') != -1):
				return True
	return False

def get_pars(soup):
	pars = soup.find("body").find_all("p")

	allPars = []

	#for all p tags in the body, only retrieve those that meet the following criteria:
	for par in pars:
		if(len(par.attrs) == 0 and len(par.text) > 56 and (par.find("span") or par.find("a") or par.find("strong") or par.find("b") or par.find("i") or par.find("em") or (not par.findChild()))):
			allPars.append(par.text)
	return allPars

comprehend = boto3.client(service_name='comprehend', region_name='us-west-2')
def get_sent(pars):
	# async with boto3.client(service_name='comprehend', region_name='us-west-2') as comprehend:
	temp = []
	solution = []
	count = 0
	for text in pars:
		if not sys.getsizeof(text) > 5000:
			temp.append(text)
			count += 1
		if count == 25:
			solution += (comprehend.batch_detect_sentiment(TextList=temp, LanguageCode='en')['ResultList'])
			temp = []
			count = 0
	if count > 0:
		solution += (comprehend.batch_detect_sentiment(TextList=temp, LanguageCode='en')['ResultList'])
	return solution

def sent_caller(pars):
	t0 = time.time()
	results = get_sent(pars)
	t1 = time.time()
	print("async time: ", (t1-t0), "seconds")
	return results

# def prodSent(event=None, context=None):
def prodSent(query):
	query += " \"review\""
	numQuery = 10
	print("Query: ", query)
	urllist = get_reviews(query, numQuery)
	# print(urllist[5])

	# list of youtube links and other soupified links
	youtube = []
	souplist = []
	pars = []

	sentSum = 0
	validQueries = 0
	url_num = 0
	pars = []


	for url in urllist:
		# ignore if from youtube (for now)
		if 'www.youtube.com' in url:
			print('YOUTUBE: ', url)
			urllist.remove(url)
			youtube.append(url)
			continue

		html = get_url(url)
		if not html:
			print("url failed")
			continue
		soup = BeautifulSoup(html, features="html.parser")
		if check_meta_review(soup):
			souplist.append(soup)
			print(url)
			pars += get_pars(soup)
	solution = sent_caller(pars)
	for fullsentiment in solution:
		sentiment = fullsentiment["Sentiment"]
		sentiment_score = fullsentiment["SentimentScore"]
		# print(sentiment)
		avg = 0
		if sentiment == "POSITIVE":
			sentSum += sentiment_score["Positive"]
			avg += 1
			validQueries += 1
		elif sentiment == "NEGATIVE":
			sentSum -= sentiment_score["Negative"]
			validQueries += 1
	# print("avg sentiment: ", sentSum/validQueries)
	if validQueries == 0:
		return 0
	return sentSum/validQueries

def lambda_handler(event, context):
	#parse out query string params
	query = event['query']

	print(event)

	print("query: ", query)

	#construct the body of the response object
	transactionResponse = {}
	transactionResponse['query'] = query
	transactionResponse['sentiment'] = prodSent(query)
	transactionResponse['message'] = 'query processed successfully'

	#construct http response object
	responseObject = {}
	responseObject['statusCode'] = 200
	responseObject['headers'] = {}
	responseObject['headers']['Access-Control-Allow-Origin'] = "*"
	responseObject['headers']['Access-Control-Allow-Credentials'] = True
	responseObject['headers']['Content-Type'] = 'application/json'
	responseObject['body'] = json.dumps(transactionResponse)

	#return the response object
	return responseObject

# main:
# print("Here is the avg sentiment: ", prodSent("Apple MacBook Pro 2020"))
# event = {"query":"gshock"}
# print(lambda_handler(event, context = None))

# html = get_url("https://www.anandtech.com/show/7418/hp-chromebook-11-review")



