import requests, os, argparse
import re as regex
from bs4 import BeautifulSoup
from pathlib import Path
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class DoujinDownloader():
	
	"""
		This class is for downloading doujins with nhentai.net
	"""
	
	def __init__(self, string, path=''):

		if len(string) == 6:
			self.url = 'https://nhentai.net/g/%s' % (string)
		elif regex.search('^http://', string):
			self.url = regex.sub('http://', 'https://', string)
		elif not regex.search('^https://', string):
			self.url = 'https://%s' % (string)
		else:
			self.url = string

		if len(path) != 0:
			self.path = Path(path)
		else:
			self.path = Path(os.getcwd())

		self.session = requests.session()
		self.page = self.session.get(self.url, verify=False)
		self.soup = BeautifulSoup(self.page.text, 'html.parser')

	def getTitle(self):
		title = self.soup.find('h1', {'class': 'title'}).get_text()
		title = regex.sub('[^a-zA-z]\\s', '', title)
		return title

	def getImages(self):
		images = self.soup.find('div', {'class': 'thumbs'})
		images = images.find_all('img', {'class': 'lazyload'})
		images = [regex.sub('^https://t.', 'https://i.', image.get('data-src')) for image in images]
		images = [regex.sub('[0-9]{1,5}t', '%s' % (count + 1), image) for count, image in enumerate(images)]
		return images

	def download(self):
		title = self.getTitle()
		images = self.getImages()
		print('Downloading %s...' % (title))
		for count, link in enumerate(images):
			image = self.session.get(link, verify=False)
			if image.status_code != 200:
				print('trouble downloading %s ' % (link))
			if not os.path.exists('%s/%s' % (self.path, title)):
				os.makedirs('%s/%s' % (self.path, title))
			file = "%s/%s/%s.jpg" % (self.path, title, count+1)
			open(file, 'wb+').write(image.content)
		print('Finished Downloading %s ' % (title))

		
def main():
	parser = argparse.ArgumentParser(description='Download Doujins from https://nhentai.net without making an account!')
	parser._action_groups.pop()
	required = parser.add_argument_group('required arguments')
	optional = parser.add_argument_group('optional arguments')
	required.add_argument('-doujin', help='Doujin to be downloaded. \nex: https://nhentai.net/g/xxxxxx, xxxxxx, nhentai.net/g/xxxxxx')
	optional.add_argument('-path', default='', help='Path to store the downloaded doujin. \n[default] is the current path.')

	args = parser.parse_args()

	if args.doujin is None:
		parser.print_help()
		return
	else:
		downloader = DoujinDownloader(args.doujin, args.path)
		downloader.download()

if __name__ == '__main__':
	main()