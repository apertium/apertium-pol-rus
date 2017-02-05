'''
cleaning the bidix from the messy translations from glosbe
dictionaries: bab.ls, pons, classes
'''

# subtasks:
# write a func for dealing with glosbe output (either choose first two or choose those which confporm to some criteria)
# write a func for changing the bidix (replacing old entries with new ones)



from lxml import etree
from lxml import html
from urllib import parse
from urllib import request
import os
import string
import subprocess


POS = 'n'
BIDIX = '../apertium-pol-rus.pol-rus.dix'
RUSDIX = '../../apertium-rus/apertium-rus.rus.dix'
BABLA = 'http://pl.bab.la/slownik/polski-rosyjski/'
PONS = 'http://en.pons.com/translate?q={0}&l=plru&in=&lf=pl'
TAGS_BOUNDARY = {'n' : 3, 'adj' : 2}
TAGS_LEMMAS = {'n' : '<n>.*<sg><nom>', 'adj' : '<adj>.*<sg><nom>',
               'vblex' : '<vblex>.*<inf>'}


def get_all_pairs():
    '''takes POS tag needed, returns all lines with pairs of this POS'''
    with open(BIDIX, 'r') as f:
        t = f.readlines()
    translations = [line for line in t if '<e><p><l>' in line
                    and '<s n="' + POS in line]
    return translations


def lines_parsed(translations):
    '''takes lines with translations, returns dict '''
    d_of_tr = {}
    for line in translations:
        sinfo = get_line_info(line, 0)
        tword = get_line_info(line, 1)[0]
        if sinfo not in d_of_tr:
            d_of_tr[sinfo] = [tword]
        else:
            d_of_tr[sinfo] += [tword]
    return d_of_tr


def get_line_info(line, n):
    tree = etree.fromstring(line)
    word = tree[0][n].text
    if tree[0][n][0].tail:
        word += ' ' + tree[0][n][0].tail
    # tags = ' '.join([tag.get('n') for tag in tree[0][n].getchildren()
    #                  if tag.get('n') is not None])
    prefix = line[:line.index('<r>') + 3]
    suffix = line[line.index('</r>'):]
    return word, prefix, suffix


def check_homonimy(d):
    for key in d:
        if len(d[key]) > 2:
            new_translations = correct(key, d[key])
            print('new translations: ' + str(new_translations))


def correct(sword, translations):
    '''returns a list of lines with pairs'''
    lexeme = sword[0]
    first_part = '<e><p><l>' + lexeme + '<s n="' + '/><s n="'.join(sword[0])
    pons_tr = from_pons(parse.quote(lexeme.encode()))
    babla_tr = from_babla(parse.quote(lexeme.encode()))
    if pons_tr + babla_tr:
        return [sword[1] + tr + sword[2] for tr in set(pons_tr + babla_tr)]


def from_pons(word):
    page = request.urlopen(PONS.format(word)).read().decode('utf-8')
    if correct_page(page, word):
        translations = html.fromstring(page).xpath('.//div[@class="target"]')
        translations = [' '.join([a.text for a in t if a.tag == 'a']).replace(chr(769), '') 
                        for t in translations]
        print(translations)
        translations = [tr for tr in translations if all_cyrillic(tr) and ' ' not in tr]
        return translations_tagged(translations)
    return []


def from_babla(word):
    translations = html.fromstring(page).xpath('.//ul[@class="sense-group-results"]')[0]
    translations = [ch[0] for ch in translations.getchildren() if ch[0].tag == 'a']
    translations = [tr.text for tr in translations if all_cyrillic(tr.text)]
    print(word)
    return translations_tagged(translations)


def correct_page(page, word):
    entries = html.fromstring(page).xpath('.//dt[@class="_entry_title"]')
    word = parse.unquote(word)
    if entries and entries[0][0].text != word:
        print('PONS: no such word: ' + word)
        return False
    return True


def all_cyrillic(s): return not set(string.ascii_letters).intersection(set(s))


def translations_tagged(translations):
    '''takes a list of russian words, returnes a list of them with grammar tags
    if there are such in the dictionary'''
    result = []
    for tr in translations:
        line = tags_getter(tr)
        if line:
            result.append(line)
            print('appended: ' + line)
        else:
            print('NOT FOUND ' + tr)
    return result


def tags_getter(rword):
    ana = subprocess.getoutput('echo {0} | lt-proc -a '
        '../../apertium-rus/rus.automorf.bin | tr "/" "\n" '
        '| grep "{1}"'.format(rword, TAGS_LEMMAS[POS]))
    ana = ana.split('<')[:TAGS_BOUNDARY[POS] + 1]
    if ana == ['']:
        os.system('echo ' + rword + '>> not_in_rus.dix')
    return '<s n="'.join(ana).replace('>', '">')


def main():
    translations = get_all_pairs()
    d = lines_parsed(translations)
    # print(sum([len(d[key]) for key in d]))
    check_homonimy(d)

main()
# print(from_pons(parse.quote('rząd'.encode())))


# --- for future --- 

def from_classes():
    prefix = 'http://www.classes.ru/all-polish/dictionary-polish-russian-term-2.htm' # всё сложно
