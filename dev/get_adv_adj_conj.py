# -*- coding: utf-8 -*-
'''for the purpose of adding some words which don't need the specification of grammatical catiegories
apart from the part of speech to the pol-rus dictionary I exported all the such words with this:
lt-expand apertium-pol.pol.dix | grep -o ':[a-zżź]\+<*pos_tag*>' | sort -u > *pos_name*.txt
from the pol dictionary and then used the online dictionary on https://glosbe.com to get the russian 
translations for them. the program creates a file with the translations in an appropriate format'''


import urllib.request
import urllib.parse
import lxml
import lxml.html
import codecs
import time

def translation_getter(word, dictionary):
	time.sleep(1)
	link_word = urllib.parse.quote(word)
	word_page = urllib.request.urlopen('https://glosbe.com/pl/ru/' + link_word).read().decode('utf-8')
	translations = lxml.html.fromstring(word_page).xpath('.//strong[@class=" phr"]')
	for tr in translations:
		dictionary.write('    <e><p><l>' + word + '<s n="num"/></l><r>'
		 + tr.text.replace(' ', '<b/>') + '<s n="num"/></r></p></e>\n')

def writer(fname):
	with codecs.open(fname, 'r', 'utf-8') as f:
		list_of_words = [line.strip()[1:len(line)-6] for line in f] # the 2nd integer depends on the length of the pos-tag
	dictionary = codecs.open('numerals.xml', 'w', 'utf-8')
	# dictionary.write('\n'*4)
	for word in list_of_words:
		try:
			translation_getter(word, dictionary)
			print(word)
		except:
			print(word + ': something gone wrong')
	dictionary.close()

writer('numerals.txt')




		
			