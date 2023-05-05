% This demo was released with SWI-Prolog and adapted for PyLog

PyLogDemo:

%% Demo coming from http://clwww.essex.ac.uk/course/LG519/2-facts/index_18.html
%%
%% Please load this file into SWI-Prolog
%%
%% Sam's likes and dislikes in food
%% 
%% Considering the following will give some practice
%% in thinking about backtracking.
%% ?- likes(sam,dahl).
%% ?- likes(sam,chop_suey).
%% ?- likes(sam,pizza).
%% ?- likes(sam,chips).
%% ?- likes(sam,curry).

likes('sam',Food) :-
        indian(Food),
        mild(Food).
likes('sam',Food) :-
        chinese(Food).
likes('sam',Food) :-
        italian(Food).
likes('sam','chips').

indian('curry').
indian('dahl').
indian('tandoori').
indian('kurma').

mild('dahl').
mild('tandoori').
mild('kurma').

chinese('chow_mein').
chinese('chop_suey').
chinese('sweet_and_sour').

italian('pizza').
italian('spaghetti').

main:

{{

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

}}
