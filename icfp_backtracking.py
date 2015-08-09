#! /usr/bin/python

from collections import deque


class Backtracker:
	"""
	`Backtracker` is a class that performs path search in a specified graph. A single
	backtracker instance can used multiple times for obtaining a path from different
	_source_ vertices to the same _target_ vertex.

	Vertices of the graph have to provide `__eq__` and `__hash__` methods. The graph
	is not necessary be stored in-memory, but instead it can be determined implicitly
	(see `adj` argument of the construct).
	"""

	class BtQueue:
		def __init__(self, dq, push, pop):
			self.dq   = dq
			self.push = push
			self.pop  = pop

		def __len__(self):  return len(self.dq)
		def __iter__(self): return iter(self.dq)

	def __init__(self, adj, q):
		"""
		Vertex *u* is _adjacent_ to *v* iff there is an edge form *v* to *u* (not from *u*
		to *v*!). The function `adj(u)` returns an iterable object that generates pairs
		*(t, v)* where *v* is a vertex adjacent to *u* and *t* is a lable
		of the edge *vu*. Note the code `dict(adj(v))` creates a map (i.e. a dictionary)
		of adjvacent vertices by corresponding edge labels.

		`q` is a collection of target vertices, usually singleton. Its precise type
		(stack, queue, randomized set) controls strategy of traversing (depth-first,
		breadth-first, etc)  
		"""
		self.routes = { u: (None, None) for u in q }
		while len(q) > 0:
			u = q.pop()
			for (t, v) in adj(u):
				if v in self.routes:
					continue
				self.routes[v] = (t, u)
				q.push(v)

	def breadthFirst(adj, target):
		dq = deque((target,))
		return Backtracker(adj, Backtracker.BtQueue(dq, dq.append, dq.popleft))

	def depthFirst(adj, target):
		dq = deque((target,))
		return Backtracker(adj, Backtracker.BtQueue(dq, dq.append, dq.pop))

	def pathFrom(self, v):
		while True:
			(t, v) = self.routes[v]
			if v is None:
				return
			yield t


if __name__ == "__main__":
	neibhours = {
		1: { ('y', 4) },
		2: { ('a', 1) },
		3: { ('b', 2), ('v', 4) },
		4: { ('w', 6), ('x', 5), ('z', 2) },
		5: { ('e', 1) },
		6: { ('c', 3), ('d', 5) }
	}
	bt = Backtracker.depthFirst(neibhours.get, 5)
	path = ''.join(bt.pathFrom(2))
	assert path in {'zye', 'bcwye'}
	print(path)
