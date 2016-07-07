# -*- coding: utf-8 -*-

import codecs
import re

def forms_collector(fname):
	'''opens a with smthn from morpheus, reads it and makes a dictionary of lemmas and wordforms'''
	with codecs.open(fname, 'r', 'utf-8') as f:
		forms = [line.split('\t') for line in f.readlines()]

	morph_d = {}
	for line in forms:
		if line[1] not in morph_d:
			morph_d[line[1]] = [line[0]]
		else:
			morph_d[line[1]].append(line[0])
	return morph_d

def info_collector(fname):
	'''opens a file with smthn from morpheus, reads it and makes a dictionary of lemmas and wordforms'''
	with codecs.open(fname, 'r', 'utf-8') as f:
		forms = [line.split('\t') for line in f.readlines()]

	gram_d = {}
	for line in forms:
		if line[1] not in gram_d:
			gram_d[line[1]] = line[2].split(':')
	# for key in gram_d:
	# 	print(key + ' : ' + gram_d[key])
	return gram_d

def paradigm_collector(morph_d):
	'''returns a dictionary, where keys are lemmas and values is a tuple of stem and flections'''
	paradigms = {}
	for lemma in morph_d:
		# print(lemma)
		stem_len = stem_finder(morph_d[lemma], lemma)
		# for form in morph_d[lemma]:
		# 	print(form[:stem_len] + ' : ' + form[stem_len:], end = ', ')
		# print('\n')
		stem = lemma[:stem_len]
		flections = [form[stem_len:] for form in morph_d[lemma]]
		paradigms[lemma] = (stem, flections)
	return paradigms

def stem_finder(forms, lemma):
	'''finds length of the stem, returns an integer. called in paradigm_collector'''
	min_len = len(min(forms, key=len))
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
	'''finds similar inflectional types'''
	similar = {}
	for lemma in paradigms:
		if tuple(set(paradigms[lemma][1])) not in similar:
			similar[tuple(set(paradigms[lemma][1]))] = [lemma]
		else:
			similar[tuple(set(paradigms[lemma][1]))].append(lemma)

	# for inventory in similar:
		# print(str(inventory))
		# print(str(similar[inventory]))
	print('number of paradigms: ' + str(len(similar)))
	return similar

def check_presence(lemmas):
	with codecs.open('../../apertium-pol/apertium-pol.pol.dix', 'r', 'utf-8') as f:
		hyp = [re.findall('<e lm="(\\w+)"><i>\w+</i><par n=".+__np"/>', line) for line in f]
		already_there = set([h[0] for h in hyp if len(h) > 0])
	# print(already_there)
	intersection = set(lemmas).intersection(set(already_there))
	print('intersection: ' + str(intersection))
	return set(lemmas).difference(set(already_there))

def to_morph(to_add, info):
	with codecs.open('add_to_monodix.xml', 'w', 'utf-8') as f:
		for word in to_add:
			f.write('    <e lm="' + word + '"><i>' + word + '</i><par n="Andrzej__np"/></e>\n')
			# if info[word] == 'f':
			# 	f.write('    <e lm="' + word + '"><i>' + word + '</i><par n="miłoś/ć__n"/></e>\n')
			# else:
			# 		print('aaa')
				# f.write('    <e lm="' + word + '"><i>' + word + '</i><par n="Adam__np"/></e>\n')

def to_bidix(to_add, info):
	with codecs.open('add_to_bidix.xml', 'w', 'utf-8') as f:
		for word in to_add:
			# if info[word] == 'f':
			# 	f.write('    <e><p><l>' + word + '<s n="np"/><s n="ant"/><s n="f"/></l><r>' + word + '<s n="np"/><s n="ant"/><s n="f"/></r></p></e>\n')
			# else:
			f.write('    <e><p><l>' + word + '<s n="np"/><s n="ant"/><s n="mp"/></l><r>' + word + '<s n="np"/><s n="ant"/><s n="m"/></r></p></e>\n')

morph_d = forms_collector('../../rzeczowniki.txt')
info = info_collector('../../rzeczowniki.txt')
paradigms = paradigm_collector(morph_d)
similar = find_similar(paradigms)
inventories = [similar[inventory] for inventory in similar]
# wordclass = sorted(inventories, key = len)[-1]

for inventory in inventories:
	# print(inventory)
	if 'Jacek' in inventory:
		wordclass = inventory

print(wordclass)
with codecs.open('/tmp/lot', 'w', 'utf-8') as f1:
	for word in wordclass:
		f1.write(word + '\n')

with codecs.open('added.txt', 'w', 'utf-8') as f:
	for lemma in wordclass:
		f.write(lemma + '\n')

for key in similar:
	if similar[key] == wordclass:
		print(key)

to_add = check_presence(wordclass)
to_morph(to_add, info)
to_bidix(to_add, info)

# done = [wordclass]
# inventories = [similar[inventory] for inventory in similar if similar[inventory] not in done]

