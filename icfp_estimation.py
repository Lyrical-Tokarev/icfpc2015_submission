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
		#TODO Implement me!
		return 0

		
if __name__ == "__main__":
	class Field:
		def __init__(self, w, h):
			self.field = (np.random.rand(w, h) < 0.5)

	f = Field(7, 7)
	(w, h) = f.field.shape
	print (BadnessEstimator(w, h).scoreBoundary(f))
