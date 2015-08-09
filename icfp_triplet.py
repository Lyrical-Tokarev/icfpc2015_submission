#! /usr/bin/python

class Triplet:
	"""
	Triplet is a way to pick a cell of a honeycomb using three-axes coordinate system:
		* Axis *P* points down (to the South);
		* Axis *Q* points right-up (to the North-east);
		* Axis *R* points left-up (to the North-West).

	Objects of this `Triplet` class are immutable.
	"""

	def __init__(self, p = 0, q = 0, r = 0):
		assert p + q + r == 0
		self.p = p
		self.q = q
		self.r = r

	def asTuple(self):
		return (self.p, self.q, self.r)

	@staticmethod
	def fromColRow(col, row=None):
		if row is None:
			(col, row) = col    # Unpack pair
		se_moves = row
		e_moves  = col - row // 2
		return Triplet(se_moves, e_moves, -(se_moves + e_moves))

	def toColRow(self):
		return ((self.q - self.r) // 2, self.p)

	def __eq__(self, other):
		return self.p == other.p and self.q == other.q and self.r == other.r

	def __repr__(self):
		return 'Triplet({}, {}, {})'.format(self.p, self.q, self.r)

	def __str__(self):
		return '({},{},{})'.format(self.p, self.q, self.r)

	def clockwise(self, pivot=None):
		if pivot is None:
			return Triplet(-self.r, -self.p, -self.q)
		else:
			return Triplet(-self.r - pivot.q, -self.p - pivot.r, -self.q - pivot.p)

	def antiClockwise(self, pivot=None):
		if pivot is None:
			return Triplet(-self.q, -self.r, -self.p)
		else:
			return Triplet(-self.q - pivot.r, -self.r - pivot.p, -self.p - pivot.q)

	def east(self):
		return Triplet(self.p, self.q + 1, self.r - 1)

	def northEast(self):
		return Triplet(self.p - 1, self.q + 1, self.r)

	def northWest(self):
		return Triplet(self.p - 1, self.q, self.r + 1)

	def west(self):
		return Triplet(self.p, self.q - 1, self.r + 1)

	def southWest(self):
		return Triplet(self.p + 1, self.q - 1, self.r)

	def southEast(self):
		return Triplet(self.p + 1, self.q, self.r - 1)

	def tie(self, pin):
		return Triplet(self.p + pin.p, self.q + pin.q, self.r + pin.r)

	def untie(self, pin):
		return Triplet(self.p - pin.p, self.q - pin.q, self.r - pin.r)


if __name__ == '__main__':
	zero = Triplet(0,0,0)
	assert Triplet(1,2,-3) == Triplet(1,2,-3)
	assert Triplet(1,2,-3).clockwise().antiClockwise() == Triplet(1,2,-3)
	assert Triplet(1,2,-3).clockwise().clockwise().clockwise() == Triplet(-1,-2,3)

	vec_e = zero.east()
	vec_ne = zero.northEast()
	vec_nw = zero.northWest()
	vec_w = zero.west()
	vec_sw = zero.southWest()
	vec_se = zero.southEast()
	assert vec_e == Triplet(0,1,-1)
	assert vec_ne == vec_e.antiClockwise()
	assert vec_nw == vec_ne.antiClockwise()
	assert vec_w == vec_nw.antiClockwise()
	assert vec_sw == vec_w.antiClockwise()
	assert vec_se == vec_sw.antiClockwise()
	assert vec_e == vec_se.antiClockwise()

	pin = Triplet(1,0,-1)
	assert Triplet(1,2,-3).tie(pin).untie(pin) == Triplet(1,2,-3)

	assert Triplet(1,2,-3).antiClockwise(pin) == Triplet(1,2,-3).untie(pin).antiClockwise().tie(pin)
	assert Triplet(1,2,-3).clockwise(pin) == Triplet(1,2,-3).untie(pin).clockwise().tie(pin)

	assert vec_e == Triplet.fromColRow(1,0)
	assert vec_ne == Triplet.fromColRow(0,-1)
	assert vec_nw == Triplet.fromColRow(-1,-1)
	assert vec_w == Triplet.fromColRow(-1,0)
	assert vec_sw == Triplet.fromColRow(-1,1)
	assert vec_se == Triplet.fromColRow(0,1)

	assert vec_e.toColRow() == (1,0)
	assert vec_ne.toColRow() == (0,-1)
	assert vec_nw.toColRow() == (-1,-1)
	assert vec_w.toColRow() == (-1,0)
	assert vec_sw.toColRow() == (-1,1)
	assert vec_se.toColRow() == (0,1)
