from fractions import gcd

class Fraction:
    def __init__(self, n, d):
        self.num = n
        self.den = d
    def add(self, f):
        d = self.den * f.den
        n = self.num*f.den + self.den * f.num
        cf = gcd(n, d)
        return Fraction(n/cf, d/cf)
    def value(self):
        return float(self.num)/float(self.den)
    def __str__(self):
        return str(self.num) + "/" + str(self.den)
