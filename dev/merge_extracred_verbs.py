from lxml import etree
import os

INDIR = 'verbs.extracted'


def get_beginning():
    with open('dix.beginning.xml') as f:
        beginning = f.read()
    return etree.fromstring(beginning)


def merge():
    basepars, vbpars, entries = [], [], []
    for fname in os.listdir(INDIR):
        with open(os.path.join(INDIR, fname)) as f:
            text = f.read()
        di = etree.fromstring(text)


merge()
