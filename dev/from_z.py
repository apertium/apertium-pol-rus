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
	forms = duplicate_killer(forms)
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

def delete_duplicates(forms): # works too long
	n = list(range(len(forms)))
	for i in n:
		for ii in n:
			print(i)
			if i < len(forms):
			    if ii != i and forms[i] == forms[ii]:
			    	forms.pop(ii)
			    	n.pop(-1)
	return forms

def duplicate_killer(forms): # also works too long, the best algorithm is in cleaner.py
	'''deletes repeting lines and lines that are the repetiotions of lines without jo'''
	forms = set(forms)
	withjo = forms.difference(set([line.replace('ё', 'е') for line in forms]))
	print('len of withjo: ' + str(len(withjo)))
	withjo = set([line.replace('ё', 'е') for line in withjo])

	forms = list(forms)
	n = list(range(len(forms)))
	for i in n:
		if i%1000 == 0:
			print('1000 more')
		for l in withjo:
			if forms[i] == l:
				forms.pop(i)
				n.pop(-1)

								# withjo_ind = [ind for ind in range(len(forms)) if 'ё' in forms[ind]]
								# new_forms = list(set([line.replace('ё', 'е') for line in forms]))
								# print('len of new_forms: ' + str(len(new_forms)))
								# for ind in withjo_ind:
								# 	for i in range(len(new_forms)):
								# 		if forms[ind].replace('ё', 'е') == new_forms[i]:
																	# 			new_forms[i] = forms[ind]
												# n = list(range(len(forms)))
												# for i in n:
												# 	if forms[i].replace('ё', 'е') == forms[i -1]:
												# 		print('yes')
												# 		forms.pop(i - 1)
												# 		n.pop(-1)
	# for line in withjo:
	# 	print(line)
	return forms

def paradigm_collector(gram_d): # working at this
	'''returns a dictionary, where keys are lemmas and values is a tuple of stem and a tuple of flections and a tuple of grammar tags'''
	# morph_d = {lexeme : gram_d[lexeme].keys() for lexeme in gram_d}
	morph_d = {}
	for lexeme in gram_d:
		# if isinstance(gram_d[lexeme], dict):
		morph_d[lexeme] = gram_d[lexeme].keys()
		# else:
			# print(str(gram_d[lexeme]))
	paradigms = {}
	for lemma in morph_d:
		# print(lemma)
		stem_len = stem_finder(morph_d[lemma], lemma)
		# for form in morph_d[lemma]:
		# 	print(form[:stem_len] + ' : ' + form[stem_len:], end = ', ')
		# print('\n')
		stem = lemma[:stem_len]
		flections = frozenset([(form[stem_len:], frozenset(gram_d[lemma][form])) for form in morph_d[lemma]])
		# flections = frozenset([form[stem_len:] for form in morph_d[lemma]])
		paradigms[lemma] = (stem, flections)
	return paradigms

def stem_finder(forms, lemma):
	'''finds length of the stem, returns an integer. called in paradigm_collector'''
	min_len = len(min(forms, key = len))
	stems_len = min_len
	for form in forms:
		for i in range(min_len):
			if lemma[i:i+1] != form[i:i+1]:
				# print(form[i:], end = ', ')
				if i < stems_len:
					stems_len = i
					break
	return stems_len

def find_similar(paradigms):
	'''returns dictionary where keys are flections and values are lexemes'''
	similar = {}
	for lemma in paradigms:
		flecs = frozenset(paradigms[lemma][1])
		if flecs not in similar:
				similar[flecs] = [lemma]
		else:
			similar[flecs].append(lemma)

	# for inventory in similar:
	# 	print(str(inventory))
	# 	print(str(similar[inventory]))
	print('number of paradigms: ' + str(len(similar)))
	return similar

# info = forms_collector('../../stuffs') #../../stuffs # someverbs.txt

# with codecs.open('../../verbs_z_experiment.json', 'w', 'utf-8')as f:
#     json.dump(info, f, ensure_ascii=False, indent=2)


def par_splitter(info):
	imp = {k:{} for k in info.keys()}
	pstact, pstpss, other = copy.deepcopy(imp), copy.deepcopy(imp), copy.deepcopy(imp)
	for lexeme in info:
		for wordform in info[lexeme]:
			if 'pstpss' in info[lexeme][wordform]:
				pstpss[lexeme][wordform] = info[lexeme][wordform]
			elif 'pstact' in info[lexeme][wordform]:
				pstact[lexeme][wordform] = info[lexeme][wordform]
			elif 'imp' in info[lexeme][wordform]:
				imp[lexeme][wordform] = info[lexeme][wordform]
			else:
				other[lexeme][wordform] = info[lexeme][wordform]
	for d in pstpss, pstact, imp, other:
		for l in info:
			if d[l] == {}:
				d.pop(l)
	return pstpss, pstact, imp, other

def pstpss_par_maker(classes):
	pass

def pstact_par_maker(classes):
	pass

def imp_par_maker(classes):
	pass				

def whole_par(classes, pstpss_par, pstact_par, imp_par):
	pass

def find_paradigm(word, inventories, similar):

	for inventory in inventories:
		if word in inventory:
			wordclass = inventory


	for key in similar:
		if similar[key] == wordclass:
			print(key)


def main():
	with codecs.open('../../verbs_z.json', 'r', 'utf-8')as f:
	    info = json.load(f)
 	
	pstpss, pstact, imp, other = par_splitter(info)
	similar_pstact = find_similar(paradigm_collector(pstact))
	# similar_pstact = find_similar(paradigm_collector_old(pstact))
	inventories = [similar_pstact[inventory] for inventory in similar_pstact]
	print('length of the greatest class: ' + str(len(sorted(inventories, key=len)[-1])))
	print(sorted(inventories, key=len)[-1])
	find_paradigm('промахнуться', inventories, similar_pstact)


# for line in pstact:
# 	print(str(line) + ':')
# 	for wordform in pstact[line]:
# 		print(str(wordform), end = ' : ')
# 		for el in pstact[line][wordform]:
# 			print(el, end = ',')
# 		print('')
# 	print('\n'*2)

main()
