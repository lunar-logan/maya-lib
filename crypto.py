def substitute(msg, key=1, symbols = "abcdefghijklmnopqrstuvwxyz"):
  n = len(symbols)
	symbolset, encMsg = set(symbols), ""
	for c in msg:
		if c in symbolset:
			index = ord(c)-ord(symbols[0]) + key
			encMsg += symbols[index%n]
		else: encMsg += c
	return encMsg
