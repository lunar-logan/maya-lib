long PrimeFactors(long n) {
	if (n <= 0) return 1;
	long e = 2, divisors = 1;
	int count = 0;

	while(n % e == 0) {
		count ++;
		n/=e;
	}
	if(count > 0) {
		//cout << e << "^" << count << " ";
		divisors = ((divisors % MOD) * ((2*count+1) % MOD)) % MOD;
	}

	count = 0;
	while (e <= floor(sqrt(n)+1))
	{
		if(n%e == 0) {
			n/=e;
			++count;
		} else {
			if(count > 0) {
				//cout << e << "^" << count << " ";
				divisors = ((divisors % MOD) * ((2*count+1) % MOD)) % MOD;
				count = 0;
			}
			e += 2;
		}
	}
	if(n > 1) {
		//cout << n << "^" << 1 << " ";
		divisors = ((divisors % MOD) * (3 % MOD)) % MOD;
	}
	//cout << endl;
	//cout << "Total Divisors : " << divisors << endl;
	return divisors;
}
