# -*- coding: utf-8 -*-

import codecs
import re
import json
import copy

def forms_collector(fname):
	'''opens a file with smthn from Zaliznyak, reads it and makes a dictionary where keys are lexemes and values are dictionaries with wordforms and morph analysis'''
	with codecs.open(fname, 'r', 'utf-8') as f:
		forms = [line.replace(chr(769),'').replace(chr(768),'') for line in f]
	print(len(forms))
	forms = kill_duplicates(forms)
	print(len(forms))
	forms = [form.split('+', 1) for form in forms]

	gram_d = {}
	for line in forms:
		pair = line[0].split(':')
		lexeme = pair[1]
		wordform = pair[0]
		if lexeme not in gram_d:
			gram_d[lexeme] = {wordform : line[1][:-1].split('+')}
		else:
			gram_d[lexeme][wordform] = line[1][:-1].split('+')
	return gram_d


def kill_duplicates(forms):
	'''deletes repeting lines and lines that are the repetiotions of lines without jo'''
	table = {}
	for line in forms:
		if line not in table:
			table[line.replace('ё', 'е')] = line
	forms = [table[key] for key in table]
	print(len(forms))
	forms = list(forms)
	return forms



info = forms_collector('someverbs.txt') #../../stuffs # someverbs.txt

with codecs.open('../../verbs_z_experiment.json', 'w', 'utf-8')as f:
    json.dump(info, f, ensure_ascii=False, indent=2)
