# PyLog - Christophe Delord

Abstract
========

> PyLog is a first order logic library including a PROLOG engine in
> Python.
>
> Please do not hesitate to test it and to report bugs and comments.
>
> > **note**
> >
> > [Python](http://www.python.org/) 2.4 or newer is required!
>
> Any collaboration is welcome ;-)

License
=======

PyLog is available under the GNU Lesser General Public:

>   PyLog: A first order logic library in Python
>
>   Copyright (C) 2009 Christophe Delord
>
>   PyLog is free software: you can redistribute it and/or modify
>   it under the terms of the GNU Lesser General Public License as published
>   by the Free Software Foundation, either version 3 of the License, or
>   (at your option) any later version.
>
>   Simple Parser is distributed in the hope that it will be useful,
>   but WITHOUT ANY WARRANTY; without even the implied warranty of
>   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
>   GNU Lesser General Public License for more details.
>
>   You should have received a copy of the GNU Lesser General Public License
>   along with Simple Parser.  If not, see <http://www.gnu.org/licenses/>.

A first order logic library in Python
=====================================

PyLog provides a simple way to write logic terms, variables and atoms.
Atoms are special objects that can contain any Python objects. All you
need is to import PyLog:

    >>> from PyLog import *

Logical objects
---------------

PyLog can handle terms, variables and atoms.

## Terms

To instantiate a term, just write it! The functor should be a valid
Python object based on Term (provided by PyLog). For example, to create
the 'f' functor :

    >>> class f(Term): pass
    >>> my_brand_new_term = f(1,f(2),3)
    >>> print my_brand_new_term
    f(1,f(2),3)

You can also add any methods to your terms. Really useful. You can for
example build terms and then call some methods of these terms.

## Variables

A variable is an instance of the Var class. Variables are free and can
be associated to another term in a stack:

    >>> X = Var()
    >>> class f(Term): pass
    >>> print "X:", X
    X: _1
    >>> s0 = Stack()
    >>> print "X:", X, "; s0(X):", s0(X)
    X: _1 ; s0(X): _1
    >>> s1 = s0.unify(X, f(1)).next()
    >>> print "X:", X, "; s1(X):", s1(X)
    X: _1 ; s1(X): f(1)
    >>> Y = Var()
    >>> s2 = s1.unify(X, Y).next()
    >>> print "Y:", Y, "; s2(Y):", s2(Y)
    Y: _2 ; s2(Y): f(1)

## Atoms

Atoms are Python objects. When building a term, any argument that is not
a term is considered as an atom.

Logical operations
------------------

Once your terms and variables are instantiated PyLog can unify them. To
do this, you have to compute the most general unifier of two terms (or
variables or atoms). If such a unifier exists you can do the
unification. The unification is a new level in the stack. Useful when
backtracking.

+-----------------------------------+--------------------------------------------------+
| Example                           | Result of execution                              |
+===================================+==================================================+
| ~~~~~~~~~~~~{.python}             | ~~~~~~~~~~~~~~~~                                 |
| from pylog import *               |                                                  |
|                                   | Simple unification                               |
| class f(Term): pass               |     Before unification                           |
| class g(Term): pass               |         a = f(X,g(Y,2))                          |
|                                   |         b = f(g(1,2),X)                          |
| print "Simple unification"        |     After unification                            |
| X = Var('X')                      |         a = f(g(1,2),g(1,2))                     |
| Y = Var('Y')                      |         b = f(g(1,2),g(1,2))                     |
| a = f(X,g(Y,2))                   | Recursive terms                                  |
| b = f(g(1,2),X)                   |     Before unification                           |
| s0 = Stack()                      |         A = A                                    |
| print "\tBefore unification"      |         a = f(A)                                 |
| print "\t\ta =", s0(a)            |     After unification                            |
| print "\t\tb =", s0(b)            |         A = f(f(f(f(f(f(f(f(f(f(f(...))))))))))) |
| s1 = s0.unify(a, b).next()        |         a = f(f(f(f(f(f(f(f(f(f(f(...))))))))))) |
| print "\tAfter unification"       |                                                  |
| print "\t\ta =", s1(a)            | ~~~~~~~~~~~~~~~~                                 |
| print "\t\tb =", s1(b)            |                                                  |
|                                   |                                                  |
| print "Recursive terms"           |                                                  |
| A = Var('A')                      |                                                  |
| a = f(A)                          |                                                  |
| s0 = Stack()                      |                                                  |
| print "\tBefore unification"      |                                                  |
| print "\t\tA =", s0(A)            |                                                  |
| print "\t\ta =", s0(a)            |                                                  |
| s1 = s0.unify(a, A).next()        |                                                  |
| print "\tAfter unification"       |                                                  |
| print "\t\tA =", s1(A)            |                                                  |
| print "\t\ta =", s1(a)            |                                                  |
| ~~~~~~~~~~~~                      |                                                  |
+-----------------------------------+--------------------------------------------------+

PROLOG
======

PyLog provides a simple PROLOG engine. It will translate a PROLOG
program into Python. This engine uses the new generator ability of
Python 2.4.

PROLOG predicates are Python generators yielding 1 when they succeed. As
a side effect they instantiate variables. So the yielded value doesn't
matter. For example, to print all the members of a list:

    X = Var()
    l = cons(1,cons(2,nil))
    for _ in member(X,l)():
        print X

For a complete example, read [pylogsrc.py](pylogsrc.html).

Download
========

-   [PyLog](src/pylog.py)

Links
=====

-   [Python](http://www.python.org/)
-   [SWI-Prolog](http://www.swi-prolog.org/)
-   [Python-Logic at Logilab](http://www.logilab.org/python-logic/)

