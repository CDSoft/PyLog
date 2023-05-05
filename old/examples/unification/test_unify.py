#!/usr/bin/python

from PyLog import *

class f(Term): pass
class g(Term): pass

print "Simple unification"
X=Var('X')
Y=Var('Y')
a=f(X,g(Y,2))
b=f(g(1,2),X)
print "\tBefore unification"
print "\ta =", a
print "\tb =", b
u = mgu(a,b)
print "\tmgu(a,b) =", u
u.unify()
print "\tAfter unification"
print "\ta =", a
print "\tb =", b
u.undo()
print "\tAfter undoing unification"
print "\ta =", a
print "\tb =", b

print "Recursive terms"
A=Var('A')
a=f(A)
print "\tA =", A
print "\ta =", a
print "\tunification of a and A"
u=mgu(a,A)
print "\tmgu(a,A) =", u
u.unify()
print "\tAfter unification"
print "\tA =", A
print "\ta =", a
u.undo()
print "\tAfter undoing unification"
print "\tA =", A
print "\ta =", a

