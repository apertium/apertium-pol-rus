# -*- coding: utf-8 -*-


### NB: я заменяю prb на пустую строку в change_tags. пометить их как-то до этого.
### why on earh does this happen: pstpss+pstpss

import codecs
import re
import json
import copy
import time


def paradigm_collector(gram_d, secondary = True): # working at this
	'''returns a dictionary, where keys are lemmas and values is a tuple of stem and frozenset of tuples of flections and frozensets of grammar tags'''
	morph_d = {lexeme : [el[0] for el in gram_d[lexeme]] for lexeme in gram_d}
	# print('example of morph_d: ' + str(morph_d[list(morph_d.keys())[0]]))
	paradigms = {}
	for lemma in morph_d:
		new_lemma = choose_lemma(gram_d[lemma])
		if new_lemma is not None:
			stem_len = stem_finder(morph_d[lemma], new_lemma)
			stem = lemma[:stem_len]
			flections = frozenset([pair[0][stem_len:] + ' ' + change_tags(pair[1], secondary) for pair in gram_d[lemma]])
			paradigms[lemma] = (stem, flections)
	# print('example of paradigms: ' + str(paradigms[list(paradigms.keys())[0]]))
	return paradigms

def change_tags(grammar_tags, secondary = True):
	grammar_tags = grammar_tags.replace(' use/ant', '').replace('pstpss pstpss ', 'pstpss ')
	if secondary:
		grammar_tags = grammar_tags.replace('v impf ', '').replace('v perf ', '').replace('tv ', '').replace('iv ', '').replace(' prb', '')
	return grammar_tags

def choose_lemma(lexeme):
	'''takes a list of forms amd grammar tags and returns a lemma'''
	if 'pstact' in lexeme[0][1] or 'pstpss' in lexeme[0][1] or 'prsact' in lexeme[0][1] or 'prspss' in lexeme[0][1]:
		for arr in lexeme:
			if 'nom' in arr[1] and 'sg' in arr[1] and 'msc' in arr[1]:
				return arr[0]
	else:
		for arr in lexeme:
			if 'inf' in arr[1]:
				return arr[0]
		print('no lemma', end = ': ')
		print(lexeme)


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
	'''returns dictionary where keys are flections and grammar tags and values are lists of lexemes'''
	similar = {}
	for lemma in paradigms:
		flecs = final_tags(paradigms[lemma][1])
		if flecs not in similar:
			similar[flecs] = [lemma]
		else:
			similar[flecs].append(lemma)

	# for inventory in similar:
	# 	print(str(inventory))
	# 	print(str(similar[inventory]))
	print('number of paradigms: ' + str(len(similar)))
	return similar

def final_tags(frozen_info):
	'''replaces tags'''
	replacer = {'msc' : 'm', 'anin': 'an', 'fem' : 'f', 'inan' : 'nn', 'anim' : 'aa', 'neu' : 'nt', 'pred' : 'short'}
	new_info = []
	for wordform in frozen_info:
		for replacement in replacer:
			wordform = wordform.replace(replacement, replacer[replacement])
		new_info.append(wordform)
	return frozenset(new_info)

# info = forms_collector('../../stuffs') #../../stuffs # someverbs.txt

# with codecs.open('../../verbs_z_experiment.json', 'w', 'utf-8')as f:
#     json.dump(info, f, ensure_ascii=False, indent=2)

def par_splitter(info):
	pstact = {k:[] for k in info.keys()}
	pstpss, prsact, prspss, other = copy.deepcopy(pstact), copy.deepcopy(pstact), copy.deepcopy(pstact), copy.deepcopy(pstact)
	for lexeme in info:
		for wordform in info[lexeme]:
			if 'pstpss' in wordform[1] and 'pred' not in wordform[1]:
				pstpss[lexeme].append(wordform)
			elif 'pstact' in wordform[1] and 'adv' not in wordform[1]:
				pstact[lexeme].append(wordform)
			elif 'prsact' in wordform[1] and 'adv' not in wordform[1]:
				prsact[lexeme].append(wordform)
			elif 'prspss' in wordform[1]:
				prspss[lexeme].append(wordform)
			else:
				other[lexeme].append(wordform)
	for d in pstpss, pstact, prsact, prspss, other:
		for l in info:
			if d[l] == []:
				d.pop(l)
	return pstpss, pstact, prsact, prspss, other

def secondary_par_maker(similar, pos):
	text = '\n\n'
	for infl_class in similar:
		text += '<pardef n="BASE__' + similar[infl_class][0] + '__' + pos + '">\n'
		for item in infl_class:
			item = item.split()
			text += '  <e><p><l>' + item[0]
			for tag in item[2:]:
				if tag in ['leng', 'use/ant']:	
					text = text.rsplit('\n', 1)[0] + '\n' + text.rsplit('\n', 1)[1].replace('<e>', '<e r="LR">')
					continue
				text += '<s n="' + tag + '"/>'
			text += '</r></p></e>\n'
		text += '</pardef>\n\n'
	return text

def whole_par(similar):
	labels = {}
	text = '\n\n'
	for infl_class in similar:
		label = similar[infl_class][0]
		labels[label] = similar[infl_class]
		text += '<pardef n="' + label + '__vblex">\n'
		for item in infl_class:
			item = item.split()
			text += '  <e><p><l>' + item[0]
			for tag in item[2:]:
				if tag in ['leng', 'use/ant']:	
					text = text.rsplit('\n', 1)[0] + '\n' + text.rsplit('\n', 1)[1].replace('<e>', '<e r="LR">')
					continue
				text += '<s n="' + tag + '"/>'
			text += '</r></p></e>\n'
		text += '</pardef>\n\n'
	return text, labels

def lexeme_spliter(info):
	tochange = {}
	for lexeme in info:
		infinitives = []
		for wordform in info[lexeme]:
			if 'inf' in wordform[1] and 'pass' not in wordform[1]:  # куча глаголов с пассивами ВАЩЕТ!
				infinitives.append(wordform)
		if len(infinitives) > 1:
			lexemes = split_correctly_mod(info[lexeme])
			tochange[lexeme] = lexemes
	for lemma in tochange:
		info.pop(lemma)
		for i in range(len(tochange[lemma])):
			info[lemma + str(i + 1)] = tochange[lemma][i]
			# print(lemma + str(i + 1) + ' : ' +  str(tochange[lemma][i]))
	return info

# def find_criterion(infinitives): # it's easier to find griteria of distinction between two things
# 	info = [set(inf[1].split()) for inf in infinitives]
# 	print('info for criterion: ' + str(info))
# 	criterion = info[0].difference(info[1])
# 	if len(criterion):
# 		print(criterion)
# 		return list(criterion)[0]
# 	else:
# 		print('zero difference: ' + str(infinitives))

# def split_correctly(lexeme, infinitives):
# 	if len(infinitives) == 2:
# 		criterion = find_criterion(infinitives)
# 		lexemes = [], []
# 		for i in range(len(lexeme)):
# 			if criterion in lexeme[i][1]:
# 				lexemes[0].append(lexeme[i])
# 			else:
# 				lexemes[1].append(lexeme[i])
# 		print('lexemes ' + str(lexemes[1]))
# 		return lexemes
# 	elif len(infinitives) > 2:
# 		pass


def split_correctly_mod(lexeme):  # отдебажить
	perf_iv, perf_tv, impf_iv, impf_tv = [], [], [], []
	for wordform in lexeme:
		if 'impf iv' in wordform[1]:
			impf_iv.append(wordform)
		elif 'perf iv' in wordform[1]:
			perf_iv.append(wordform)
		elif 'impf tv' in wordform[1]:
			impf_tv.append(wordform)
		elif 'perf tv' in wordform[1]:
			perf_tv.append(wordform)
		else:
			print(wordform)
	lexemes = [perf_iv, perf_tv, impf_iv, impf_tv]
	lexemes = [arr for arr in lexemes if arr != []]
	# if len(lexemes) != 2:
	# 	print(lexemes)
	# 	quit()
	return lexemes



def find_paradigm(word, inventories, similar):

	for inventory in inventories:
		if word in inventory:
			wordclass = inventory


	for key in similar:
		if similar[key] == wordclass:
			print(key)


def cleaner(info):
	cleaned_info = {}
	for lexeme in info:
		wordforms = [[wordform[0], wordform[1].replace(' fac', '')] for wordform in info[lexeme]]
		cleaned_info[lexeme] = wordforms
	new_blistatj = [w for w in info['блистать'] if not w[0].startswith('и') and not w[0].startswith('е')]
	cleaned_info['блистать'] = new_blistatj
	return cleaned_info

def fun_debugging_time(similar):
	inventories = similar.values()
	greatest = sorted(inventories, key=len)[-1]
	print('length of the greatest class: ' + str(len(greatest)))
	print('three words from the greatest wordclass: ' + greatest[0] + ', ' + greatest[1] + ', ' + greatest[2])
	find_paradigm(greatest[0], inventories, similar)
	print('----------------')
	second = sorted(inventories, key=len)[-2]
	print('length of the second greatest class: ' + str(len(second)))
	print('three words from the second greatest wordclass: ' + second[0] + ', ' + second[1] + ', ' + second[2])
	find_paradigm(second[0], inventories, similar)
	print('----------------')
	third = sorted(inventories, key=len)[-3]
	print('length of the third greatest class: ' + str(len(third)))
	print('three words from the second greatest wordclass: ' + third[0] + ', ' + third[1]) # + ', ' + third[2])
	find_paradigm(third[0], inventories, similar)
	print('----------------')
	fourth = sorted(inventories, key=len)[-4]
	print('length of the fourth greatest class: ' + str(len(fourth)))
	print('three words from the second greatest wordclass: ' + fourth[0]) # + ', ' + third[2])
	find_paradigm(fourth[0], inventories, similar)


def entries_maker(similar, labels):
	text = '\n'*4
	for wordclass in similar:
		# t1 = time.clock()
		for verb in similar[wordclass]:
			thereis = False
			for label in labels:
				if verb in labels[label]:
					text += '    <e lm="' + verb + '"><i>' + verb + '</i><par n="' + label + '"/></e>\n'
					thereis = True
			if not thereis:
				text += '    <e lm="' + verb + '"><i>' + verb + '</i><par n="' + 'AAAAAA' + '"/></e>\n'
		# t2 = time.clock()
		# print('one wordclass: ' + str(t2 - t1))
	return text


def main():
	with codecs.open('../../verbs_z.json', 'r', 'utf-8')as f:
	    info = json.load(f)

	info = cleaner(info)
	lexeme_spliter(info)

	pstpss, pstact, prsact, prspss, other = par_splitter(info)
	similar_pstact = find_similar(paradigm_collector(pstact))
	similar_pstpss = find_similar(paradigm_collector(pstpss))
	similar_prsact = find_similar(paradigm_collector(prsact))
	similar_prspss = find_similar(paradigm_collector(prspss))
	similar_other = find_similar(paradigm_collector(other, secondary = False))

	russian_verbs = codecs.open('russian_verbs.dix', 'w')
	russian_verbs.write(secondary_par_maker(similar_pstpss, 'pstpss'))
	russian_verbs.write(secondary_par_maker(similar_pstact, 'pstact'))
	russian_verbs.write(secondary_par_maker(similar_prsact, 'prsact'))
	russian_verbs.write(secondary_par_maker(similar_prspss, 'prspss'))
	entries, labels = whole_par(similar_other)
	russian_verbs.write(entries)

	russian_verbs.write(entries_maker(similar_other, labels))
	russian_verbs.close()
	
	# import pickle
	# pickle.dump(similar_pstact, open( "save.p", "wb" ) )

	fun_debugging_time(similar_other)




main()
