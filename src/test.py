#!/usr/bin/env python2.4

from pylog import *

import sys

test = {
    'termes': """
        class f(Term): pass
        my_brand_new_term = f(1,f(2),3)
        print my_brand_new_term
    """,
    'variables': """
        X = Var()
        class f(Term): pass
        print "X:", X
        s0 = Stack()
        print "X:", X, "; s0(X):", s0(X)
        s1 = s0.unify(X, f(1)).next()
        print "X:", X, "; s1(X):", s1(X)
        Y = Var()
        s2 = s1.unify(X, Y).next()
        print "Y:", Y, "; s2(Y):", s2(Y)
    """,
}

if __name__ == '__main__':
    for cmd in sys.argv[1:]:
        for l in test[cmd].splitlines():
            l = l.strip()
            if l:
                print ">>>", l
                exec l
