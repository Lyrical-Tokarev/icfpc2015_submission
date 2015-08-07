#! /usr/bin/python

from itertools import *


class Random:
	"""
	The pseudo-random sequence of numbers will be computed from a given seed using
	a linear congruential generator with the following parameters:

		modulus    = 2 ** 32
		multiplier = 1103515245
		increment  = 12345
	"""

	def __init__(self, seed):
		self.state = seed

	def __iter__(self):
		return self

	def __next__(self):
		return self.next()	# for compatibility with Python 3

	def next(self):
		prn = (self.state & 0x7FFF0000) >> 16 
		self.state = (1103515245 * self.state + 12345) & 0xFFFFFFFF
		return prn


"""
A little bit of home-made unit testing.  For a sake of the Old Ones of course!
""" 
if __name__ == '__main__':
	rnd = Random(17)

	actual = list(islice(rnd, 10))
	expected = [0, 24107, 16552, 12125, 9427, 13152, 21440, 3383, 6873, 16117]
	assert actual == expected