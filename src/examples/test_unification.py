#!/usr/bin/env python

from pylog import *

class f(Term): pass
class g(Term): pass

print "Simple unification"
X = Var('X')
Y = Var('Y')
a = f(X,g(Y,2))
b = f(g(1,2),X)
s0 = Stack()
print "\tBefore unification"
print "\t\ta =", s0(a)
print "\t\tb =", s0(b)
s1 = s0.unify(a, b).next()
print "\tAfter unification"
print "\t\ta =", s1(a)
print "\t\tb =", s1(b)

print "Recursive terms"
A = Var('A')
a = f(A)
s0 = Stack()
print "\tBefore unification"
print "\t\tA =", s0(A)
print "\t\ta =", s0(a)
s1 = s0.unify(a, A).next()
print "\tAfter unification"
print "\t\tA =", s1(A)
print "\t\ta =", s1(a)
