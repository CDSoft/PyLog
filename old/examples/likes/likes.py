from __future__ import generators
from PyLog import *
class PyLogDemo(PyLogEngine, ):
	def mild(self, PyL_0):
		try:
			u=mgu(Term(PyL_0),Term('dahl'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			u=mgu(Term(PyL_0),Term('tandoori'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			u=mgu(Term(PyL_0),Term('kurma'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
	def indian(self, PyL_0):
		try:
			u=mgu(Term(PyL_0),Term('curry'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			u=mgu(Term(PyL_0),Term('dahl'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			u=mgu(Term(PyL_0),Term('tandoori'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			u=mgu(Term(PyL_0),Term('kurma'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
	def likes(self, PyL_0,PyL_1):
		try:
			Food = Var()
			u=mgu(Term(PyL_0,PyL_1),Term('sam',Food))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.And,[(self.indian,[Food]),(self.mild,[Food])]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			Food = Var()
			u=mgu(Term(PyL_0,PyL_1),Term('sam',Food))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.chinese,[Food]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			Food = Var()
			u=mgu(Term(PyL_0,PyL_1),Term('sam',Food))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.italian,[Food]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			u=mgu(Term(PyL_0,PyL_1),Term('sam','chips'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
	def chinese(self, PyL_0):
		try:
			u=mgu(Term(PyL_0),Term('chow_mein'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			u=mgu(Term(PyL_0),Term('chop_suey'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			u=mgu(Term(PyL_0),Term('sweet_and_sour'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
	def italian(self, PyL_0):
		try:
			u=mgu(Term(PyL_0),Term('pizza'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return
		try:
			u=mgu(Term(PyL_0),Term('spaghetti'))
			if u is not None:
				u.unify()
				for _ in self.Goal(self.true,[]):
					yield 1
				u.undo()
		except self.Cut:
			return


WHO, WHAT = Var('WHO'), Var('WHAT')
queries =	[
				('likes',('sam','dahl')),
				('likes',('sam','chop_suey')),
				('likes',('sam','pizza')),
				('likes',('sam','chips')),
				('likes',('sam','curry')),
				('likes',(WHO,WHAT)),
			]

demo = PyLogDemo()
for (pred, (who, what)) in queries:
	print "%s(%s,%s)"%(pred,who,what)
	n=0
	for _ in apply(getattr(demo,pred),[who,what]):
		print "yes"
		print "\twho =", who
		print "\twhat =", what
		n += 1
	if n==0:
		print "no"

