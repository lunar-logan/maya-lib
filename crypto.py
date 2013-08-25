def substitute(msg, key=1, symbols = "abcdefghijklmnopqrstuvwxyz"):
  n = len(symbols)
	symbolset, encMsg = set(symbols), ""
	for c in msg:
		if c in symbolset:
			index = ord(c)-ord(symbols[0]) + key
			encMsg += symbols[index%n]
		else: encMsg += c
	return encMsg

def signature(a):
	place, signature = {}, ""
	for i in xrange(len(a)):
		if a[i] in place:
			signature += str(place[a[i]])
		else:
			place[a[i]] = i
			signature += str(i)
	return signature
