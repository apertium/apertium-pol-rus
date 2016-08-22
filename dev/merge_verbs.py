# -*- coding: utf-8 -*-
# ok, i'm writing it in Python 2.7 -_-

import codecs
import re
import lxml
from lxml import etree

def get_data():
	with codecs.open(u'../../apertium-rus/apertium-rus.rus.dix', u'r') as rus_dix:
		lines_rus_dix = rus_dix.read()
	with codecs.open('russian_verbs.dix', 'r') as rv_par:
	    to_add = rv_par.read()
	return lines_rus_dix, to_add

# def get_parts(the_xml):
# 	dictionary = etree.fromstring(the_xml.replace('<?xml version="1.0" encoding="UTF-8"?>', ''))
# 	paradigms = dictionary.xpath('pardefs/pardef')
# 	entries = dictionary.xpath('section/e[@lm]')
# 	return paradigms, entries

# def del_vblex_pars(paradigms):
# 	print('length of pars before ' + str(len(paradigms)))
# 	pars_len = len(paradigms)
# 	i = 0
# 	while i < pars_len:
# 		if len(paradigms[i].xpath('./e/p/r/s[@n="vblex"]')) > 0:
# 			# print(paradigms[i].get('n'))
# 			paradigms.pop(i)
# 			pars_len -= 1
# 		else:
# 			i += 1
# 	print('length of pars after ' + str(len(paradigms)))
# 	return paradigms

def del_vblex_ents(entries):
	print('entr bfr: ' + str(len(entries)))
	for child in entries:
		if child.tag == 'e' and 'vblex' in child.xpath('par')[0].get('n'):
			entries.remove(child)
	print('entr aftr: ' + str(len(entries)))
	return entries


def del_vblex_pars_mod(paradigms):
	print('length of pars before ' + str(len(paradigms)))
	pars_len = len(paradigms)
	for child in paradigms:
		if len(child.xpath('./e/p/r/s[@n="vblex"]')) > 0:
			# print(child.get('n'))
			paradigms.remove(child)
	print('length of pars after ' + str(len(paradigms)))
	return paradigms

def get_parts_mod(the_xml, ent_sec):
	dictionary = etree.fromstring(the_xml.replace('<?xml version="1.0" encoding="UTF-8"?>', ''))
	paradigms = dictionary.xpath('pardefs')[0]
	verb_entries = dictionary.xpath(ent_sec)[0]
	return paradigms, verb_entries, dictionary

def write_new_file(dictionary):
	new = codecs.open('apertium-rus.rus.dix.new', 'w')
	# new_par_text = '\n\n'
	# cyr_attr = {}
	# for paradigm in paradigms[10:15]:
	# 	cyr_attr[etree.tostring(paradigm, encoding='unicode', pretty_print=True).split('"')[1]] = paradigm.get('n')
	# 	curr_attr = etree.tostring(paradigm, encoding='unicode', pretty_print=True).split('"')[1]
	# 	new.write(etree.tostring(paradigm, encoding='unicode', pretty_print=True).replace(curr_attr, paradigm.get('n')))
	text = etree.tostring(dictionary, encoding='unicode', pretty_print=True)
	text = text.replace('>\n      <pardef', '>\n\n\n      <pardef')
	new.write(text)
	new.close()

def adder(toupdate, toadd):
	print('previous: ' + str(len(toupdate)))
	for el in toadd:
		toupdate.append(el)
	print('final: ' + str(len(toupdate)))
	return toupdate


def main():
	lines_rus_dix, to_add = get_data()
	paradigms, entries, dictionary = get_parts_mod(lines_rus_dix, 'section[@id="gci"]')
	cleaned_paradgms = del_vblex_pars_mod(paradigms)
	cleaned_ents = del_vblex_ents(entries)
	new_paradigms, new_entries, new_dictionary = get_parts_mod(to_add, 'section[@id="main"]')
	final_pars = adder(cleaned_paradgms, new_paradigms)
	final_ents = adder(cleaned_ents, new_entries)
	# cl_ent = dictionary.xpath('section[@id="gci"]')[0]
	# print('finally: ' + str(len(cl_ent)))
	write_new_file(dictionary)

main()


