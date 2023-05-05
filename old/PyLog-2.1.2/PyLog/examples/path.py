#!/usr/bin/env python

from pylog import *

exec(compile(r"""

next(a,b).
next(a,c).

next(b,d).
next(c,e).

next(d,f).
next(e,f).

next(f,g).

path(X,Y,[X,Y]) :- next(X,Y).
path(X,Y,[[X,Z]|PATH]) :- next(X,Z), path(Z,Y,PATH).

shorten([],[]).
shorten([X],[X]) :- !.
shorten([X,X|L0], L1) :- !, shorten([X|L0], L1).
shorten([X|L0], [X|L1]) :- shorten(L0, L1).

"""))

PATH, PATH0, PATH1 = Var('P'), Var('P0'), Var('P1')
X = Var('X')
Y = Var('Y')
GOAL = path(X,Y,PATH0) & flatten(PATH0,PATH1) & shorten(PATH1,PATH)
for _ in GOAL():
	print X, Y, PATH
