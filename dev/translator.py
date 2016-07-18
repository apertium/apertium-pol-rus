# -*- coding: utf-8 -*-

import urllib.request
import urllib
import lxml
import lxml.html
import codecs
import time
import re
import random

# tags = '<s n="vblex"/><s n="perf"/>'
tags1 = '<s n="vblex"/><s n="perf"/>'
tags2 = '<s n="vblex"/><s n="perf"/>'

def translation_getter_globse(noun, dictionary):
	# time.sleep(random.choice(range(10)))
	print('entered globse')
	link_noun = urllib.parse.quote(noun)
	noun_page = urllib.request.urlopen('https://glosbe.com/pl/ru/	' + link_noun).read().decode('utf-8')
	translations = lxml.html.fromstring(noun_page).xpath('.//strong[@class=" phr"]')
	for tr in translations:
		dictionary.write('<e><p><l>' + noun + tags1 + '</l><r>' 
			+ tr.text.replace(' ', '<b/>') + tags2 + '</r></p><par n="agr_n"/></e>\n')

def translation_getter_babla(noun, dictionary):
	# time.sleep(random.choice(range(10)))
	print('entered babla')
	link_noun = urllib.parse.quote(noun)
	noun_page = urllib.request.urlopen('http://pl.bab.la/slownik/polski-rosyjski/' + link_noun).read().decode('utf-8')
	translations = lxml.html.fromstring(noun_page).xpath('.//a[@class="result-link"]')
	for tr in translations:
		print(tr.text)
		if tr.text is not None:
			if tr.text[0] not in 'qwertyuiopasdfghjklzxcvnm':
				got_it = True
				dictionary.write('<e><p><l>' + noun + tags1 + '</l><r>' 
							+ tr.text.replace(' ', '<b/>') + tags2 + '</r></p><par n="agr_n"/></e>\n')
	got_it


def translation_getter_wiki(noun, dictionary):
	# time.sleep(random.choice(range(10)))
	print('entered wiki')
	link_noun = urllib.parse.quote(noun)
	print(link_noun)
	noun_page = urllib.request.urlopen('https://pl.wiktionary.org/wiki/' + link_noun + '#pl').read().decode('utf-8')
	translations = lxml.html.fromstring(noun_page).xpath('.//li')
	# poss_tr = lxml.etree.fromstring(the_prep_page).xpath('.//li')
	for hyp in translations:
		if hyp.text is not None and hyp.text.startswith('rosyjski:'):
			got_it = True
			print('got it!')
			for tr in hyp:
				print(tr.text)
				dictionary.write('<e><p><l>' + noun + tags1 + '</l><r>' 
					+ tr.text.replace(' ', '<b/>') +  tags2 + '</r></p><par n="agr_n"/></e>\n')
	got_it


def writer(nouns_from_pol):
	print('entered writer')
	with codecs.open('../apertium-pol-rus.pol-rus.dix', 'r', 'utf-8') as f:
		hyp = [re.findall('<l>(\\w+)<s n="n"/>', line) for line in f]
		already_there = set([h[0] for h in hyp if len(h) > 0])
	dictionary = codecs.open('nouns2dictionary_07.07.xml', 'w', 'utf-8')
	for noun in nouns_from_pol:
		if noun not in already_there:
			try:
				translation_getter_wiki(noun, dictionary)
				print('wiki: ' + noun)
			except Exception as e:
				print(e)
				try:
					translation_getter_babla(noun, dictionary)
					print('babla: ' + noun)
				except Exception as e:
					print(e)
					try:
						translation_getter_globse(noun, dictionary)
						print('classes')
					except Exception as e:
						print('something is wrong: ' + noun)
						print(e)
	dictionary.close()

with codecs.open('new.txt', 'r', 'utf-8') as f:
	lines = [line.strip() for line in f.readlines()]
writer(lines)
