# -*- coding: utf-8 -*-
'''for the purpose of adding some nouns to the pol-rus dictionary I exported all the nouns existing in pol dictionary
and then used the online dictionary on https://glosbe.com to get the russian translations for them.
after that the program creates a file with the translations in an appropriate format'''


import urllib.request
import urllib
import lxml
import lxml.html
import codecs
import time
import re
import random

def classes_dealer(noun):
	letters = 'aąbcćdeęfghijklłmnńoóprsśtuwyzźż'
	letters = {letters[i]:str(i+1) for i in range(len(letters))}
	link = 'http://www.classes.ru/all-polish/dictionary-polish-russian.htm?letter=' + letters[noun[0]]
	print('num of first letter: ' + letters[noun[0]])
	this_letter = urllib.request.urlopen(link)
	this_letter = this_letter.read().decode('utf-8')
	print(this_letter)
	list_of_words = lxml.html.fromstring(this_letter).xpath('.//div[@class="NavLang"]')

	print(len(list_of_words))
	for el in list_of_words:
		print(el.get('class'))
	

def translation_getter_classes(noun, tags, dictionary):
	# time.sleep(random.choice(range(10)))
	classes_dealer('kot')
	exit()



def translation_getter_globse(noun, tags, dictionary):
	# time.sleep(random.choice(range(10)))
	link_noun = urllib.parse.quote(noun)
	noun_page = urllib.request.urlopen('https://glosbe.com/pl/ru/	' + link_noun).read().decode('utf-8')
	translations = lxml.html.fromstring(noun_page).xpath('.//strong[@class=" phr"]')
	for tr in translations:
		if verifier(tr.text) is not None:
			dictionary.write('<e><p><l>' + noun + tags + '</l><r>' 
				+ tr.text.replace(' ', '<b/>') + verifier(tr.text) + '</r></p></e>\n')

def translation_getter_babla(noun, tags, dictionary):
	# time.sleep(random.choice(range(10)))
	link_noun = urllib.parse.quote(noun)
	noun_page = urllib.request.urlopen('http://pl.bab.la/slownik/polski-rosyjski/' + link_noun).read().decode('utf-8')
	translations = lxml.html.fromstring(noun_page).xpath('.//a[@class="result-link"]')
	for tr in translations:
		print(tr.text)
		if verifier(tr.text) is not None:
			dictionary.write('<e><p><l>' + noun + tags + '</l><r>' 
				+ tr.text.replace(' ', '<b/>') + verifier(tr.text) + '</r></p></e>\n')
		else:
			dictionary.write('<e><p><l>' + noun + tags + '</l><r>' 
						+ tr.text.replace(' ', '<b/>') + '<s n="n"/></r></p></e>\n')


def translation_getter_wiki(noun, tags, dictionary):
	# time.sleep(random.choice(range(10)))
	link_noun = urllib.parse.quote(noun)
	print(link_noun)
	noun_page = urllib.request.urlopen('https://pl.wiktionary.org/wiki/' + link_noun + '#pl').read().decode('utf-8')
	translations = lxml.html.fromstring(noun_page).xpath('.//li')
	# poss_tr = lxml.etree.fromstring(the_prep_page).xpath('.//li')
	for hyp in translations:
		if hyp.text is not None and hyp.text.startswith('rosyjski:'):
			print('got it!')
			for tr in hyp:
				print(tr.text)
				if verifier(tr.text) is not None:
					dictionary.write('<e><p><l>' + noun + tags + '</l><r>' 
						+ tr.text.replace(' ', '<b/>') + verifier(tr.text) + '</r></p></e>\n')
				else:
					dictionary.write('<e><p><l>' + noun + tags + '</l><r>' 
						+ tr.text.replace(' ', '<b/>') + '<s n="n"/></r></p></e>\n')



def writer(nouns_from_pol, top_frequent):
	with codecs.open('../apertium-pol-rus.pol-rus.dix', 'r', 'utf-8') as f:
		hyp = [re.findall('<l>(\\w+)<s n="n"/>', line) for line in f]
		already_there = set([h[0] for h in hyp if len(h) > 0])
		# already_there = set([line.split('<s n="n"/>')[0].strip('    <e><p><l>') for line in f])
	dictionary = codecs.open('nouns2dictionary_07.07.xml', 'w', 'utf-8')
	for noun in nouns_from_pol:
		if noun not in already_there: #and noun in top_frequent:
			try:
				translation_getter_wiki(noun, nouns_from_pol[noun], dictionary)
				print('wiki' + noun)
			except Exception as e:
				print(e)
				try:
					translation_getter_babla(noun, nouns_from_pol[noun], dictionary)
					print('babla')
				except Exception as e:
					print(e)
					try:
						translation_getter_globse(noun, nouns_from_pol[noun], dictionary)
						print('classes')
					except Exception as e:
						print('something is wrong: ' + noun)
						print(e)
	dictionary.close()

def verifier(translation):
	'''cheks that the translation is present in russian dictionary'''
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

with codecs.open('added.txt', 'r', 'utf-8') as f:
        top_frequent = [line.strip() for line in f]
# writer(nouns_from_pol)
writer(tags_getter('nouns.txt'), top_frequent)
