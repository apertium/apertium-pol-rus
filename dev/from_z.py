# -*- coding: utf-8 -*-


### todo: write a splitter which disambiguates between verbs with similar 
### infs but differnt meanings and other forms _before_ building paradigms

### NB: я заменяю prb на пустую строку в change_tags. пометить их как-то до этого.
### why on earh does this happen: pstpss+pstpss

import codecs
import re
import json
import copy
import time


def paradigm_collector(gram_d, secondary = True):
	'''returns a dictionary, where keys are lemmas and values is a tuple of stem and frozenset of tuples of flections and frozensets of grammar tags'''
	morph_d = {lexeme : [el[0] for el in gram_d[lexeme]] for lexeme in gram_d}
	gram_d = change_tags(gram_d, secondary)
	paradigms = {}
	for lemma in morph_d:
		new_lemma = choose_lemma(gram_d[lemma])
		if new_lemma is not None:
			stem_len = stem_finder(morph_d[lemma], new_lemma)
			if secondary:
				stem, lem_flection= stem_and_flection(gram_d[lemma], stem_len)
			else:
				stem, lem_flection = lemma[:stem_len], lemma[stem_len:]
			# flections = frozenset([pair[0][stem_len:] + ' ' + change_tags(pair[1], secondary) for pair in gram_d[lemma]])
			flections = frozenset([pair[0][stem_len:] + ' ' + pair[1] for pair in gram_d[lemma]])
			paradigms[lemma] = ((stem, lem_flection), flections)
	return paradigms	

def change_tags(gram_d, secondary = True):
	'''takes gram_d and returns it with tags changed'''
	for lexeme in gram_d:
		for wordform in gram_d[lexeme]:
			wordform[1] = wordform[1].replace('pstpss pstpss ', 'pstpss ')
			if secondary:
				wordform[1] = wordform[1].replace('v impf ', '').replace('v perf ', '').replace('tv ', '').replace('iv ', '').replace(' prb', '')
			elif lexeme in ['иметь1', 'иметь2']:
				wordform[1] = wordform[1].replace('v impf ', 'vbhaver impf ').replace('v impf ', 'vbhaver perf ')
			elif lexeme in ['мочь', 'хотеть']:
				wordform[1] = wordform[1].replace('v impf ', 'vbmod impf ').replace('v impf ', 'vbmod perf ')
	# gram_d['иметь1'] ## THERE ARE NO SUCH
	return gram_d

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

	print('number of paradigms: ' + str(len(similar)))
	return similar

def final_tags(frozen_info):
	'''replaces tags'''
	replacer = {'msc' : 'm', 'anin': 'an', 'fem' : 'f', 'inan' : 'nn', 'anim' : 'aa', 'neu' : 'nt', 'pred' : 'short', 'v' : 'vblex', 
	            'sg1' : 'p1 sg', 'sg2' : 'p2 sg', 'sg3' : 'p3 sg', 'pl1' : 'p1 pl', 'pl2' : 'p2 pl', 'pl3' : 'p3 pl',
	            'prs' : 'pres'}
	new_info = []
	for wordform in frozen_info:
		for replacement in replacer:
			wordform = wordform.split()
			wordform = [tag if tag not in replacer else replacer[tag] for tag in wordform]
			wordform = ' '.join(wordform)
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


def stem_and_flection(lexeme, stem_len):
	for wordform in lexeme:
		if 'msc anin sg nom' in wordform[1] and 'pass' not in wordform[1]:
			stem = wordform[0][:stem_len]
			flection = wordform[0][stem_len:]
			return stem, flection
	print('Something is wriong with stem_and_flection')
	print('lexeme: ' + str(lexeme))


def secondary_par_maker(similar, pos, paradigms):
	labels = {}
	text = '\n\n'
	for infl_class in similar:
		label = similar[infl_class][0]
		st_and_fl = paradigms[label][0]
		labels[label] = (st_and_fl, similar[infl_class])
		print('secondary_par_maker: ' + str(st_and_fl))
		# text += '    <pardef n="BASE__' + st_and_fl[0] + '/' + stem_len[1] + '__' + pos + '">\n'
		text += '    <pardef n="BASE__' + label + '__' + pos + '">\n'
		for item in infl_class:
			item = item.split()
			text += '        <e><p><l>' + item[0] + '</l><r>'
			for tag in item[2:]:
				if tag in ['leng', 'use/ant', 'use/obs']:	
					text = text.rsplit('\n', 1)[0] + '\n' + text.rsplit('\n', 1)[1].replace('<e>', '<e r="LR">')
					continue
				text += '<s n="' + tag + '"/>'
			text += '</r></p></e>\n'
		text += '    </pardef>\n\n'
	return text, labels

def make_stem(label, infl_class):
	for wordform in infl_class:
		if 'inf' in wordform and 'pass' not in wordform:
			inf_ending = wordform.split(' ')[0]
	addition = ''
	if label[-1] in '1234':
		addition += label[-1]
		label  = label[:-1]
	if label[-1] in '¹²³':
		addition = label[-1] + addition
		label = label[:-1]
	base = label.split(inf_ending)[0]
	return base, inf_ending + addition

def participle_pars(text, label, base_fin, ending):
	for el in ['pstpss', 'pstact', 'prsact', 'prspss']:
		text += '  <e><p><l>#' + base_fin + '#</l><r>' + ending + '<s n="vblex"/><s n="' + el + '"/></r></p><par n="@BASE REQUIRED@' + el  + '@' + label + '@"/></e>\n'
	return text

def whole_par(similar):
	labels = {}
	text = '\n\n'
	for infl_class in similar:
		label = similar[infl_class][0]
		labels[label] = similar[infl_class]
		base, ending = make_stem(label, infl_class)
		text += '<pardef n="' + base + '/' + ending + '__vblex">\n'
		for item in infl_class:
			item = item.split()
			text += '  <e><p><l>' + item[0] + 	'</l><r>' + ending
			for tag in item[1:]:
				if tag in ['leng', 'use/ant', 'use/obs']:	
					text = text.rsplit('\n', 1)[0] + '\n' + text.rsplit('\n', 1)[1].replace('<e>', '<e r="LR">')
					continue
				text += '<s n="' + tag + '"/>'
			text += '</r></p></e>\n'
		text = participle_pars(text, label, base, ending)
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
	print('three words from the second greatest wordclass: ' + third[0] + ', ' + third[1] + ', ' + third[2])
	find_paradigm(third[0], inventories, similar)
	print('----------------')
	fourth = sorted(inventories, key=len)[-4]
	print('length of the fourth greatest class: ' + str(len(fourth)))
	print('three words from the second greatest wordclass: ' + fourth[0] + ', ' + third[1] + ', ' + third[2])
	find_paradigm(fourth[0], inventories, similar)


def entries_maker(similar, labels, paradigms):
	print('building entries ...')
	text = '\n'*4
	for wordclass in similar:
		for verb in similar[wordclass]:
			thereis = False
			for label in labels:
				if verb in labels[label]:
					st_and_fl = paradigms[label][0]
					ending = st_and_fl[1]
					# ending = re.sub('[1234¹²]', '', st_and_fl[1]) # mb will help with pars with the same name
					verb = re.sub('[1234¹²³]', '', verb)
					text += '    <e lm="' + verb + '"><i>' + verb.split(ending)[0] + '</i><par n="' + label.split(ending)[0] + '/' + ending + '__vblex"/></e>\n'
					thereis = True
					break
			if not thereis:
				print('Something is wrong with entries_maker: ' + verb)
	return text


def find_ptcp_base(info, lexeme, par, ending):
	for wordform in info[lexeme]:
		if par in wordform[1] and 'msc anin sg nom' in wordform[1] and 'pass' not in wordform[1]:
			ptcp_lemma = wordform[0]
			ptcp_base = ptcp_lemma.split(ending)[0]
			# print('find_ptcp_base, lexeme: ' + lexeme + ', base: ' + ptcp_base)
			return ptcp_base
	print('something is rong with find_ptcp_base, lexeme ' + lexeme)


def prtcp_affixes(line, prtcp_base):
	base = line.split('#')[1]
	if base:
		if len(prtcp_base.split(base)) > 1:
			prtcp_base = prtcp_base.split(base)[1]
			# print('SUCCESSFULLY: ' + affix + ', base: ' + base)
		else:
			print('something strange: '+ line + '\nbase: ' + base + ', ptcpl_base: ' + prtcp_base)
	else:
		print('zero ptcpl ending: ' + line)
	line = line.split('#')[0] + prtcp_base + line.split('#')[2]
	return line

def secondary_par_matcher(text, ptcpls, info):
	'''finds places in vblex pars where there should be references to participle paradigms and makes it, returns string with paradigms'''
	lines = []
	for line in text.split('\n'):
		if 'BASE REQUIRED' in line:
			par, lexeme = line.split('@')[2], line.split('@')[3]
			current_pos_labels = ptcpls[par]
			for label in current_pos_labels:
				st_and_fl = current_pos_labels[label][0]
				ending = st_and_fl[1]
				if lexeme in current_pos_labels[label][1]:
					line = line.split('@')[0] + 'BASE__' + label + '__' + par + line.split('@')[4]
					# print('secondary_par_matcher: ' + str(st_and_fl))
					line = prtcp_affixes(line, find_ptcp_base(info, lexeme, par, ending))
					lines.append(line)
					break
		else:
			lines.append(line)
	return '\n'.join(lines)

def secondary_par_writer(ptcpls):
	'''returns string with participle paradigms and a dictionary where keys are lemmas used in names of ptcple pars and values
	are something complicated with other lemmaas belonging to the same inflectional class'''
	text = ''
	labels_s = {}
	for part in ptcpls:
		print(part, end = ', ')
		paradigms = paradigm_collector(ptcpls[part])
		similar_pars = find_similar(paradigms)
		new_text, current_labels = secondary_par_maker(similar_pars, part, paradigms)
		text += new_text
		labels_s[part] = current_labels
	return text, labels_s


def paradigms_writer(info):
	'''returns a string with all paradigms'''
	pstpss, pstact, prsact, prspss, other = par_splitter(info)
	ptcpls = {'pstpss' : pstpss, 'pstact' : pstact, 'prsact' : prsact, 'prspss' : prspss}
	text, labels_s = secondary_par_writer(ptcpls)
	paradigms = paradigm_collector(other, secondary = False)
	similar_other = find_similar(paradigms)
	types, labels_vblex = whole_par(similar_other)
	text += types
	text = secondary_par_matcher(text, labels_s, info)
	text += entries_maker(similar_other, labels_vblex, paradigms)

	fun_debugging_time(similar_other)

	return text


def main():
	info = json.load(codecs.open('../../verbs_z.json', 'r', 'utf-8'))
	info = lexeme_spliter(cleaner(info))
	text = paradigms_writer(info)

	russian_verbs = codecs.open('russian_verbs.dix.xml', 'w')
	russian_verbs.write(text)	
	russian_verbs.close()

main()

import os
os.system('subl russian_verbs.dix.xml')
