# -*- coding: utf-8 -*-

import codecs
import re
import json
import copy


def paradigm_collector(gram_d): # working at this
	'''returns a dictionary, where keys are lemmas and values is a tuple of stem and frozenset of tuples of flections and frozensets of grammar tags'''
	morph_d = {lexeme : [el[0] for el in gram_d[lexeme]] for lexeme in gram_d}
	paradigms = {}
	for lemma in morph_d:
		stem_len = stem_finder(morph_d[lemma], lemma)
		stem = lemma[:stem_len]
		flections = frozenset([pair[0][stem_len:] + ' ' + pair[1] for pair in gram_d[lemma]])
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

def stem_finder_mod(forms, lemma):
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
	'''returns dictionary where keys are flections and grammar tags and values are lists of lexemes'''
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
	imp = {k:[] for k in info.keys()}
	pstact, pstpss, other = copy.deepcopy(imp), copy.deepcopy(imp), copy.deepcopy(imp)
	for lexeme in info:
		for wordform in info[lexeme]:
			if 'pstpss' in wordform[1]:
				pstpss[lexeme].append(wordform)
			elif 'pstact' in wordform[1]:
				pstact[lexeme].append(wordform)
			elif 'imp' in wordform[1]:
				imp[lexeme].append(wordform)
			else:
				other[lexeme].append(wordform)
	for d in pstpss, pstact, imp, other:
		for l in info:
			if d[l] == []:
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
	# import pickle
	# pickle.dump(similar_pstact, open( "save.p", "wb" ) )

	inventories = similar_pstact.values()
	greatest = sorted(inventories, key=len)[2]
	print('length of the greatest class: ' + str(len(greatest)))
	print('the greatest class: ')
	find_paradigm(greatest[0], inventories, similar_pstact)
	print(greatest)


main()
