import codecs

f = codecs.open('nouns2dictionary_07.07.xml', 'r', 'utf-8')
lines = f.readlines()

for i in range(len(lines)):
	for j in range(len(lines)):
		if lines[i] == lines[j] and i != j and '<' in lines[i]:
			print(str(i) + ', ' + str(j) + ':\n' + lines[i])
