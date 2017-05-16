from lxml import etree


BIDIX = '../apertium-pol-rus.pol-rus.dix'
RUSDIX = '../../apertium-rus/apertium-rus.rus.dix'
POS = 'vblex'


def get_data(dixname, ent_sec):
    """
    Takes 2 strings: path to the dix and name of the section.
    Returns a tuple of par etree, entries etree and whole dictionary etree. 
    """
    with open(dixname) as rus_dix:
        dix = rus_dix.read()
    dix = etree.fromstring(dix.replace('<?xml version=\'1.0\' encoding=\'utf-8\'?>', ''))
    entries = dix.xpath(ent_sec)[0]
    return entries, dix


def verb_ents_bidix(pairs):
	"""
	Takes a tree with word entries, returns a tuple with verb entries,
	verb entries translated as expressions ans a tree of entries cleaned
	from any verb entries.
	"""
	print('len of entries: ' + str(len(pairs)))
	expressions, verbents = [], []
	for pair in pairs:
		if pair.xpath('./p/r/s[@n="vblex"]'):
			# verbs.append(pair[0][-1].text + '\n')
			if pair[0][-1][0].tag == 'b':
				expressions.append(pair)
			else:
				verbents.append(pair)
			pairs.remove(pair)
	print('verbents: ' + str(len(verbents)))
	print('len of cleaned entries: ' + str(len(pairs)))
	return expressions, verbents, pairs


def main():
    monoverbs, monodix = get_data(RUSDIX, 'section[@id="gci"]')
    pairs, bidix = get_data(BIDIX, 'section[@id="main"]')
    expressions, verbents, cleaned_pairs = verb_ents_bidix(pairs)
    verbents = change_verbents(verbents)
    bidix = build_new_bidix(bidix, verbents, expressions)


if __name__ == '__main__':
    main()
