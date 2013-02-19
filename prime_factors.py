def pf(n):
  z = 2
	p = set()
	p.add(1)
	while z*z <= n:
		if n%z == 0:
			if not z in p:
				p.add(z)
			n/=z
		else:
			z += 1
	if n > 1: p.add(n)
	return p
