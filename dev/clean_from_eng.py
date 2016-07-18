import codecs
words_to_delete = ['The', 'the', 'of', 'in', 'Wiki', 'Google', 'Commons', 'Open', 'Windows', 'Wikinews', 'Prix', 'Red', 
					'Oracle', 'Foundation', 'and', 'Office', 'International', 'University', 'Skype', 'Airbus', 'Air', 'Tour', 'Blues',
					'Space', 'SpaceX', 'Microsoft', 'Ubuntu', 'Facebook', 'FC', 'Creative', 'OpenStreetMap', 'OpenOffice.org', 'Express', 
					'World', 'open', 'for', 'online', 'LibreOffice', 'art', 'Day', 'Dragon']
punctuation = list(' ,.()-?!:;"') + ['\n']
f = codecs.open('../../pol.crp.txt', 'r', 'utf-8')
f1 = codecs.open('../../pol.crp_without_eng.txt', 'w', 'utf-8')
polish_corpus = f.read()
f.close()
for word in words_to_delete:
	polish_corpus = polish_corpus.replace('<br clear="all">', '')
	for sign in punctuation:
		for s in punctuation:
			polish_corpus = polish_corpus.replace(sign + word + s, '')
			# print('signs: ' + sign + s)
 
f1.write(polish_corpus)
f1.close()
