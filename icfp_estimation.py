#! /usr/bin/python

from icfp_loader_script import Field
import numpy as np
from numpy import log, logical_not, logical_xor

def heightBadness(x, height):
	return log((height + 1) / (x + 1))

class BadnessEstimator:
	def __init__(self, width, height):
		self.width  = width
		self.height = height
		xs = np.arange(height)
		self.height_scale = heightBadness(xs)

	def scoreHeight(self, field):
		row_fullness = self.width - np.sum(field.field, axis=0)
		return np.sum(row_fullness * self.height_scale)

	def deltaScoreHeight(self, field, cell):
		badness = heightBadness(cell.x)
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
		#TODO Not accurate
		hb = np.zeros((self.width, self.height), dtype=bool)
		np.logical_not(field.field[0, :], out=hb[0, :])
		np.diff(field.field, axis=0, out=hb[1:, :])

		vb = np.zeros((self.width, self.height), dtype=bool)
		np.logical_not(field.field[:, 0], out=vb[:, 0])
		np.diff(field.field, axis=1, out=vb[:, 1:])

		return np.sum(hb) + np.sum(vb) + np.sum(logical_xor(hb, vb))

	def deltaScoreBoundary(self, field, cell):
		#TODO Implement me!
		return 0
		