#! /usr/bin/python

import numpy as np
from numpy import log, logical_not, logical_xor

def heightBadness(x, height):
	return log((height + 1) / (x + 1))

class BadnessEstimator:
	def __init__(self, width, height):
		self.width  = width
		self.height = height
		xs = np.arange(height)
		self.height_scale = heightBadness(height, xs)

	def scoreHeight(self, field):
		row_fullness = self.width - np.sum(field.field, axis=0)
		return np.sum(row_fullness * self.height_scale)

	def deltaScoreHeight(self, field, cell):
		badness = heightBadness(self.height, cell.x)
		if field.field[cell.y, cell.x]:
			return badness
		else:
			return -badness

	def scoreFilledRows(self, field):
		row_fullness = logical_not(np.any(field.field, axis=0))
		return -np.sum(row_fullness)

	def deltaScoreFilledRows(self, field, cell):
		empty_cells = np.sum(field.field[:, cell.x])
		badness = -1 if empty_cells == self.width - 1 else 0
		if field.field[cell.y, cell.x]:
			return badness
		else:
			return -badness

	def scoreBoundary(self, field):
		tiles = logical_not(field.field)
		n1 = self.height // 2
		n2 = (self.height - 1) // 2
		joints  = np.sum(tiles[:, :-1] & tiles[:, 1:])
		joints += np.sum(tiles[:-1, :] & tiles[1:, :])
		joints += np.sum(tiles[1:, 0:2*n1:2] & tiles[:-1, 1:2*n1+1:2])
		joints += np.sum(tiles[:-1, 1:2*n2+1:2] & tiles[1:, 2:2*n2+2:2])
		return 6 * np.sum(tiles) - 2 * joints

	def deltaScoreBoundary(self, field, cell):
		f = field.field
		(cm, rm) = (self.width - 1, self.height - 1)
		(c, r) = (cell.y, cell.x)
		bounds  = c == 0 or f[c, r] != f[c-1, r]
		bounds += c == cm or f[c, r] != f[c+1, r]
		bounds += r == 0 and f[c, r] != f[c, r-1]
		bounds += r == rm od f[c, r] != f[c, r+1]
		if r & 1:
			bounds += c == cm or r == 0 or f[c, r] != f[c+1, r-1]
			bounds += c == cm or r == rm or f[c, r] != f[c+1, r+1]
		else:
			bounds += c == 0 or r == 0 or f[c, r] != f[c-1, r-1]
			bounds += c == 0 or r == rm or f[c, r] != f[c-1, r+1]
		return 6 - 2 * bounds

		
if __name__ == "__main__":
	class Field:
		def __init__(self, w, h):
			self.field = (np.random.rand(w, h) < 0.5)

	f = Field(7, 7)
	(w, h) = f.field.shape
	print (BadnessEstimator(w, h).scoreBoundary(f))
