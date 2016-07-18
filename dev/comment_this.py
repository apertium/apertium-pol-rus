# -*- coding: utf-8 -*-

import codecs
import re

def find_words_to_comment(corpus_fd, mistakes):
	with codecs.open(corpus_fd, 'r', 'utf-8') as f1:
		words_in_corpus = set([line.split(' ')[0].strip('*,.!?') for line in f1.readlines()])
	with codecs.open(mistakes, 'r', 'utf-8') as f2:
		errors = f2.read()
		lexemes = set(re.findall('\[\\\\\^(.+?)<', errors))
	not_in_corpus = lexemes.difference(words_in_corpus)
	for w in not_in_corpus:
		print(w)
	return not_in_corpus

def commenting_out(bidix, to_comment_out):
	to_comment_out = find_words_to_comment('../../wikinews_fd.csv', '../../errors')
	with codecs.open(bidix, 'r', 'utf-8') as f:
		lines = f.readlines()
	new_lines = ['<!-- ' + line[:-1] + '  : not in pol corpus-->\n' 
				 if len(re.findall('<e><p><l>(.+?)<', line)) != 0
				 and re.findall('<e><p><l>(.+?)<', line)[0] in to_comment_out
				 else line for line in lines]
	with codecs.open(bidix + '.new', 'w', 'utf-8') as new_file:
		for line in new_lines:
			new_file.write(line)

commenting_out('../apertium-pol-rus.pol-rus.dix', ['ktokolwiek'])