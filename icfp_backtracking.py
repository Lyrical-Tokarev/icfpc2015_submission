#! /usr/bin/python

class Backtracker:
	def __init__(self, adj, targets):
		"""
		`adj(u)` returns an iterable object that generates pairs *(t, v)* where *v*
		is a vertex adjacent to *u* and *t* is a lable of the edge *uv*. Note the code
		`dict(adj(v))` creates a map (i.e. a dictionary) of adjvacent vertices
		by corresponding edge labels.
		"""
		self.routes = { u: (None, None) for u in targets}
		q = targets
		while len(q) > 0:
			u = q.pop()
			for (t, v) in adj(u):
				if v in self.routes:
					continue
				self.routes[v] = (t, u)
				q.add(v)

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
	bt = Backtracker(neibhours.get, {5})
	path = ''.join(bt.pathFrom(2))
	assert path in {'zye', 'bcwye'}
