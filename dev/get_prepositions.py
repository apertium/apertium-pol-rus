# -*- coding: utf-8 -*-

import urllib.request
import lxml
from lxml import etree
import codecs

req = urllib.request.urlopen('https://pl.wiktionary.org/wiki/Kategoria:J%C4%99zyk_polski_-_przyimki')
maintree = lxml.etree.fromstring(req.read())
prepositions = [line for par in maintree.xpath('.//div[@class="mw-category"]')[0] for line in par.xpath('.//a[@href]')]

def translation_verification(translation):
	with codecs.open('prepositions.txt', 'r', 'utf-8') as f:
		russian_preps = [line.strip()[1:len(line)-5] for line in f]
	if translation in russian_preps:
		return True
		
dictionary = codecs.open('test_dictioanry.xml', 'w', 'utf-8')
for el in prepositions:
	print(el.text)
	the_prep_page = urllib.request.urlopen('https://pl.wiktionary.org' + el.get('href')).read().decode('utf-8')

	poss_tr = lxml.etree.fromstring(the_prep_page).xpath('.//li')
	for hyp in poss_tr:
		if hyp.text is not None and hyp.text.startswith('rosyjski:'):
			print('got it!')
			for child in hyp:
				if translation_verification(child.text):
					dictionary.write('<e><p><l>' + el.text + '<s n="pr"/></l><r>' + child.text + '<s n="pr"/></r></p></e>\n')
					break

dictionary.close()

