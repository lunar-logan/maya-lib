def f(x, k=1000):
  #Define your function here
	return (x**3 + x + k)
def dof(x):
	#define the derivative of f(x) here
	return (3 * (x**2) + 1)

def newton_raphson(a=-20, b=20):
	'''
	Select the range (a,b) very carefully.. Should contain the probable point of roots
	'''
	x = (a+b)/2.0
	for i in xrange(1, 30):
		y = x - (f(x)/dof(x))
		x = y
	return x

print newton_raphson()
#-0.682327803828
