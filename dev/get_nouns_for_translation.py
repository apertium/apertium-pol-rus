# -*- coding: utf-8 -*-
'''for the purpose of adding some nouns to the pol-rus dictionary I exported all the nouns existing in pol dictionary
and then used the online dictionary on https://glosbe.com to get the russian translations for them.
after that the program creates a file with the translations in an appropriate format'''


import urllib.request
import lxml
import lxml.html
import codecs
import time
import re

def translation_getter(noun, tags, dictionary):
	time.sleep(1)
	link_noun = urllib.parse.quote(noun)
	noun_page = urllib.request.urlopen('https://glosbe.com/pl/ru/' + link_noun).read().decode('utf-8')
	translations = lxml.html.fromstring(noun_page).xpath('.//strong[@class=" phr"]')
	for tr in translations:
		if verifier(tr.text) is not None:
			dictionary.write('<e><p><l>' + noun + tags + '</l><r>' 
				+ tr.text.replace(' ', '<b/>') + '<s n="n"/>' + verifier(tr.text) + '</r></p></e>\n')


def writer(nouns_from_pol):
	dictionary = codecs.open('nouns_add_to_dictionary3.xml', 'w', 'utf-8')
	not_in_d = False
	for noun in nouns_from_pol:
		if not_in_d:
			try:
				translation_getter(noun, nouns_from_pol[noun], dictionary)
				print(noun)
			except:
				print('something is wrong: ' + noun)
		if noun == 'dowód':
			not_in_d = True
	dictionary.close()

def verifier(translation):
	nouns_from_rus = tags_getter('russian_nouns.txt')
	if translation in nouns_from_rus:
		return nouns_from_rus[translation]
	

def tags_getter(fname):
	with codecs.open(fname, 'r', 'utf-8') as f:
		nouns_and_tags = {}
		for line in f:
			noun = line.split('<n>', 1)[0]
			tags = re.findall('.(<.+)\n', line)[0]
			tags = tags.replace('<', '<s n="').replace('>', '"/>')
			# print(noun + ' : ' + tags)
			nouns_and_tags[noun] = tags
	return nouns_and_tags

# writer(nouns_from_pol)
writer(tags_getter('nouns.txt'))