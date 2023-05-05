#!/usr/bin/env python

from pylog import *

class f(Term): pass
class g(Term): pass

print "Simple unification"
X = Var('X')
Y = Var('Y')
a = f(X,g(Y,2))
b = f(g(1,2),X)
print "\tBefore unification"
print "\t\ta =", a
print "\t\tb =", b
u = mgu(a,b)
print "\t\tmgu(a,b) =", u
u.unify()
print "\tAfter unification"
print "\t\ta =", a
print "\t\tb =", b
u.undo()
print "\tAfter undoing unification"
print "\t\ta =", a
print "\t\tb =", b

print "Recursive terms"
A = Var('A')
a = f(A)
print "\t\tA =", A
print "\t\ta =", a
print "\tUnification of a and A"
u = mgu(a,A)
print "\t\tmgu(a,A) =", u
u.unify()
print "\tAfter unification"
print "\t\tA =", A
print "\t\ta =", a
u.undo()
print "\tAfter undoing unification"
print "\t\tA =", A
print "\t\ta =", a
