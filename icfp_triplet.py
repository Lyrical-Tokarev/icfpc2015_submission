#! /usr/bin/python

class Triplet:
	"""
	Triplet is a way to pick a cell of a honeycomb using three-axes coordinate system:
		* Axis *P* points down (to the South);
		* Axis *Q* points right-up (to the North-east);
		* Axis *R* points left-up (to the North-West).

	Objects of this `Triplet` class are immutable.
	"""

	def __init__(self, p, q, r):
		assert p + q + r == 0
		self.p = p
		self.q = q
		self.r = r

	def __eq__(self, other):
		return self.p == other.p and self.q == other.q and self.r == other.r

	def __repr__(self):
		return 'Triplet({}, {}, {})'.format(self.p, self.q, self.r)

	def __str__(self):
		return '({},{},{})'.format(self.p, self.q, self.r)

	def antiClockwise(self):
		return Triplet(-self.r, -self.p, -self.q)

	def clockwise(self):
		return Triplet(-self.q, -self.r, -self.p)

	def east(self):
		return Triplet(self.p, self.q + 1, self.r - 1)

	def northEast(self):
		return Triplet(self.p + 1, self.q, self.r - 1)

	def northWest(self):
		return Triplet(self.p + 1, self.q - 1, self.r)

	def west(self):
		return Triplet(self.p, self.q - 1, self.r + 1)

	def southWest(self):
		return Triplet(self.p - 1, self.q, self.r + 1)

	def southEast(self):
		return Triplet(self.p - 1, self.q + 1, self.r)

if __name__ == '__main__':
	origin = Triplet(0,0,0)
	assert Triplet(1,2,-3) == Triplet(1,2,-3)
	assert Triplet(1,2,-3).clockwise().antiClockwise() == Triplet(1,2,-3)
	assert Triplet(1,2,-3).clockwise().clockwise().clockwise() == Triplet(-1,-2,3)

	vec_e = origin.east()
	vec_ne = origin.northEast()
	vec_nw = origin.northWest()
	vec_w = origin.west()
	vec_sw = origin.southWest()
	vec_se = origin.southEast()
	assert vec_e == Triplet(0,1,-1)
	assert vec_ne == vec_e.antiClockwise()
	assert vec_nw == vec_ne.antiClockwise()
	assert vec_w == vec_nw.antiClockwise()
	assert vec_sw == vec_w.antiClockwise()
	assert vec_se == vec_sw.antiClockwise()
	assert vec_e == vec_se.antiClockwise()

