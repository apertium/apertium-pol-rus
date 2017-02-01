# -*- codecs:utf-8 -*-

import codecs
import os
import lxml.html
import string

PATH = '/home/maryszmary/Documents/texts/source/post1950'


def corpus(fname):
    '''получает на вход путь к файлу, открывает файл с xml, возвращает строку с текстом файла без тегов'''
    f = codecs.open(fname, 'r', 'utf-8')
    myfile = f.read().split('\n', 1)[1]
    tree = lxml.html.fromstring(myfile)
    content = tree.xpath('.//p')
    text = ''
    for el in content:
    	if el.text != None:
    		text += '\n' + el.text
    f.close()
    return text


def extractor_of_text():
    f = codecs.open('/home/maryszmary/Documents/ruscorpora', 'w', 'utf-8')
    for d, dirs, files in os.walk(PATH):
        for fi in files:
            text = corpus(os.path.join(d, fi))
            f.write(text)
    f.close()


def fd_of_corp():
    f = codecs.open('/home/maryszmary/Documents/ruscorp_fd', 'w', 'utf-8')
    di = {}
    for d, dirs, files in os.walk(PATH):
        for fi in files:
            text = corpus(os.path.join(d, fi))
            di = fd(di, text)
    res = [el + ' : ' + str(di[el]) for el in sorted(di, key=lambda x: -di[x])] 
    f.write('\n'.join(res))
    f.close()


def fd(di, text):
    for word in text.lower().split():
        word = word.strip(string.punctuation)
        if word in di:
            di[word] += 1
        else:
            di[word] = 1
    return di 


# extractor_of_text()
fd_of_corp()

