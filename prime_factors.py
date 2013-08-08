#Finds and return a list of all the prime factors of a given integer
import collections
def pf(x):
	i, c, factors = 0, x, collections.Counter()
	while c%2 == 0:
		factors[2] += 1
		c /= 2
	i=3
	while i <= int(pow(c, 0.5)+1):
		if c % i == 0:
			factors[i] += 1
			c /= i
		else: i += 2
	if c > 1: factors[c] += 1
	return factors
