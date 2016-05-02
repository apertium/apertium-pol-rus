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
import random

def translation_getter(noun, tags, dictionary):
	# time.sleep(random.choice(range(10)))
	link_noun = urllib.parse.quote(noun)
	noun_page = urllib.request.urlopen('https://glosbe.com/pl/ru/' + link_noun).read().decode('utf-8')
	translations = lxml.html.fromstring(noun_page).xpath('.//strong[@class=" phr"]')
	for tr in translations:
		if verifier(tr.text) is not None:
			dictionary.write('<e><p><l>' + noun + tags + '</l><r>' 
				+ tr.text.replace(' ', '<b/>') + verifier(tr.text) + '</r></p></e>\n')


def writer(nouns_from_pol, top_frequent):
	with codecs.open('nouns2dictionary_top.xml', 'r', 'utf-8') as f:
		hyp = [re.findall('<l>(\\w+)<s', line) for line in f]
		already_there = set([h[0] for h in hyp if len(h) > 0])
		# already_there = set([line.split('<s n="n"/>')[0].strip('    <e><p><l>') for line in f])
	dictionary = codecs.open('nouns2dictionary_300_2.xml', 'w', 'utf-8')
	for noun in nouns_from_pol:
		if noun not in already_there and noun in top_frequent:
			try:
				translation_getter(noun, nouns_from_pol[noun], dictionary)
				print(noun)
			except:
				print('something is wrong: ' + noun)
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
##			print(noun + ' : ' + tags)
			nouns_and_tags[noun] = tags
	return nouns_and_tags

with codecs.open('after_freq_300.txt', 'r', 'utf-8') as f:
        top_frequent = [line.strip() for line in f]
# writer(nouns_from_pol)
writer(tags_getter('nouns.txt'), top_frequent)
