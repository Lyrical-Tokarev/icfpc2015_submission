#! /usr/bin/python

from math import exp
from random import random


def gibbs(e_cur, e_cand, temp):
	"""
	Acceptance probability function, that corresponds to Gibbs measure. 

	Function arguments:
		* `e_cur` -- energy of the current configuration;
		* `e_cand` -- energy of a candidate configuration;
		* `temp` -- temperature factor. 
	"""
	return exp((e_cur - e_cand) / temp)

class SimulatedAnnealing:
	def __init__(energy, candidate, schedule, apf=gibbs):
		"""
		`energy` -- Energy (target) function. It takes a configuration and returns
		a real value that measures its fitness. Note that lesser quantities means
		better fitness, i.e. energy has to be _minimized_ within a process
		of SA optimization.

		`candidate` -- Stochastic candidate configuration operator. It takes current
		configuration and offers another configuration, which is fairly close (in some
		meaning) by the current one. The operator offerings vary from call to call because
		of its stochasticness; if this propertie doesn't hold, SA optimization algorithm
		may stuck at a locally optimal point.

		`schedule` -- Annealing schedule, a decreasing sequence of temperatures. Length
		of the schedule determines duration of the SA process. Please note that
		SA algorithm is highly sensetive to schedule's features, although this effect
		can be partially compensated by choosing the APF. In the case of the default
		Gibbs APF temperature at the each step should be proportional to expected
		energy gain.

		`apf` -- Acceptance probability function. It calculates assurance of that
		candidate configuration should be accepted as a new configuration. Result
		quantity 1 and grater represents that candidate should be obligatory accepted,
		0 and less -- obligatory declined. APF takes three parameters:
			* `e_cur` -- energy of the current configuration;
			* `e_cand` -- energy of a candidate configuration;
			* `temp` -- temperature factor.
		"""
		self.energy    = energy
		self.candidate = candidate
		self.schedule  = schedule
		self.apf       = apf

	def optimize(c_cur, e_cur=None):
		if e_cur is None:
			e_cur = energy(c_cand)
		for temp in self.schedule:
			c_cand = self.candidate(c_cur)
			e_cand = self.energy(c_cand)
			if random() < apf(e_cur, e_cand, temp):
				(c_cur, e_cur) = (c_cand, e_cand)
		return (c_cur, e_cur)
