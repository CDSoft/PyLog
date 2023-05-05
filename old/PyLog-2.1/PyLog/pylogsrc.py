#!/usr/bin/env python

#<python>

""" PyLog is a first order logic library and a PROLOG engine in Python """

#</python>

#<python>
from __future__ import generators
#</python>
import tpg

#<python>

__date__ = "12 july 2002"
__version__ = "2.1"
__author__ = "Christophe Delord <christophe.delord@free.fr>"

##############################################################################
#                                                                            #
# Basic PyLog object                                                         #
#                                                                            #
##############################################################################

class PyLogObject(object):
	def deref(self): return self
	def isfree(self): return 0

def _mkPyLogObject(obj):
	if isinstance(obj, PyLogObject): return obj
	else                           : return Atom(obj)

def _PyLogObject_str(t, l=10):
	if l==0: return "..."
	t = t.deref()
	if isinstance(t, Atom): return str(t)
	if isinstance(t, Var) : return str(t)
	if isinstance(t, Term):
		str1 = lambda t, l=l-1: _PyLogObject_str(t,l)
		return "%s(%s)"%(t.__class__.__name__, ','.join(map(str1, t.args)))
	return "???"

##############################################################################
#                                                                            #
# Atoms                                                                      #
#                                                                            #
##############################################################################

class Atom(PyLogObject):
	def __init__(self, obj): self.obj = obj
	def __str__(self): return str(self.obj)
	def __cmp__(self, other):
		other = other.deref()
		if isinstance(other, Atom): return cmp(self.obj, other.obj)
		if isinstance(other, Var) : return +1
		return -1

class atom(PyLogObject):
	def __init__(self, name): self.name = name
	def __str__(self): return self.name
	def __cmp__(self, other):
		if isinstance(other, PyLogObject):
			other = other.deref()
			if isinstance(other, atom): return cmp(self.name, other.name)
			if isinstance(other, Var): return +1
		return -1

##############################################################################
#                                                                            #
# Terms                                                                      #
#                                                                            #
##############################################################################

class Term(PyLogObject):
	def __init__(self, *args): self.args = map(_mkPyLogObject,args)
	def arity(self): return len(self.args)
	def __str__(self): return _PyLogObject_str(self)
	def __cmp__(self, other):
		other = other.deref()
		if isinstance(other, Term):
			return cmp(
				(self .__class__.__name__, self .arity(), self .args),
				(other.__class__.__name__, other.arity(), other.args)
			)
		return +1
	def getarg(self, i): return self.args[i]
	def setarg(self, i, a): self.args[i] = a
	def consarglist(self):
		def _add(args, l):
			if args: return _add(args[:-1], cons(args[-1],l))
			return l
		return _add(self.args, nil)

_termdef = {}
def register_term(term):
	global _termdef
	_termdef[term.__name__] = term

##############################################################################
#                                                                            #
# Lists                                                                      #
#                                                                            #
##############################################################################

class cons(Term):
	def __init__(self, head, tail):
		super(cons,self).__init__(head, tail)
		self.head, self.tail = self.args
	def __str__(self): return _strlist(self)
	def pylist(self): return [self.head] + self.tail.pylist()

class nil(Term):
	def __str__(self): return "[]"
	def pylist(self): return []
nil = nil()

def _strlist(lst):
	l = []
	h, t = lst.head.deref(), lst.tail.deref()
	while 1:
		l.append(str(h))
		if not isinstance(t, cons): break
		h, t = t.head.deref(), t.tail.deref()
	head = ','.join(l)
	if t is nil: tail = ''
	else       : tail = '|%s'%str(t)
	return '[%s%s]'%(head, tail)

##############################################################################
#                                                                            #
# Variables                                                                  #
#                                                                            #
##############################################################################

class BindingError(Exception): pass

class Var(PyLogObject):
	_count = {}
	def __init__(self, name="_"):
		self.term = None
		try:
			self.name = "%s%d"%(name, self.__class__._count[name])
			self.__class__._count[name] += 1
		except KeyError:
			self.name = name
			self.__class__._count[name] = 1
	def __str__(self):
		v = self.deref()
		if isinstance(v, Var): return v.name
		else                 : return str(v)
	def deref(self):
		if self.term is not None: return self.term.deref()
		else                    : return self
	def bind(self, obj):
		v = self.deref()
		t = _mkPyLogObject(obj).deref()
		if isinstance(v, Var):
			if t!=v: v.term = t
		else: raise BindingError, "Cannot bind non free variables"
	def isfree(self): return isinstance(self.deref(), Var)
	def __cmp__(self, other):
		other = other.deref()
		if isinstance(other, Var): return cmp(self.name, other.name)
		return -1

##############################################################################
#                                                                            #
# Most general unifier                                                       #
#                                                                            #
##############################################################################

# A unifier is an associative array {var} -> {object}

class Unifier(dict):
	def __nonzero__(self): return 1
	def __str__(self): return " ".join(["%s/%s"%(t,v.name) for v,t in self.items()])
	def unify(self):
		self.backup = {}
		for v, t in self.items():
			self.backup[v] = v.term
			v.bind(t)
	def undo(self):
		for v,t in self.backup.items(): v.term = t
		self.backup = {}

def mgu(*terms):
	u = Unifier()					# current unifier
	if len(terms)<2: return u
	t = terms[0].deref()
	stack = [ (t, t2.deref()) for t2 in terms[1:] ]
	done = {}
	class NoMGU(Exception): pass
	def store(t1, t2):
		t1 = t1.deref()
		t2 = t2.deref()
		if (t1, t2) not in stack and (t1, t2) not in done:
			stack.append((t1, t2))
	def update(v, t):
		try            : store(u[v], t)
		except KeyError: u[v] = t
	def atom_atom(a1, a2):
		if a1.obj != a2.obj: raise NoMGU
	def term_atom(t, a):
		raise NoMGU
	def term_term(t1, t2):
		if t1.__class__ == t2.__class__ and t1.arity() == t2.arity():
			for (a1, a2) in zip(t1.args, t2.args): store(a1, a2)
		else:
			raise NoMGU
	def var_atom(v, a): update(v, a)
	def var_term(v, t): update(v, t)
	def var_var(v1, v2): update(v1, v2)
	try:
		while stack:
			t1, t2 = stack.pop()
			done[(t1, t2)] = 1
			if isinstance(t1, Atom):
				if isinstance(t2, Atom): atom_atom(t1,t2)
				elif isinstance(t2, Term): term_atom(t2,t1)
				elif isinstance(t2, Var): var_atom(t2,t1)
				else: type_error()
			elif isinstance(t1, Term):
				if isinstance(t2, Atom): term_atom(t1,t2)
				elif isinstance(t2, Term): term_term(t1,t2)
				elif isinstance(t2, Var): var_term(t2,t1)
				else: type_error()
			elif isinstance(t1, Var):
				if isinstance(t2, Atom): var_atom(t1,t2)
				elif isinstance(t2, Term): var_term(t1,t2)
				elif isinstance(t2, Var): var_var(t1,t2)
				else: type_error()
	except NoMGU: return None
	return u

##############################################################################
#                                                                            #
# PROLOG engine                                                              #
#                                                                            #
##############################################################################

class ClauseExpr(object):
	def __and__   (self, other): return And(self, other)
	def __or__    (self, other): return Or(self, other)
	def __rshift__(self, other): return And(self, cut, other)

class true(ClauseExpr):
	def __call__(self): yield 1
	def __str__(self): return "true"
true = true()

class fail(ClauseExpr):
	def __call__(self): raise StopIteration; yield 0
	def __str__(self): return "fail"
fail = fail()

class CutException(Exception): pass

class cut(ClauseExpr):
	def __call__(self): yield 1; raise CutException
	def __str__(self): return "!"
cut = cut()

class And(ClauseExpr):
	def __init__(self, *args): self.args = args
	def __call__(self):
		for _ in self._and(*self.args): yield 1
	def _and(self, *args):
		if args:
			for _ in args[0]():
				for _ in self._and(*args[1:]): yield 1
		else: yield 1
	def __str__(self): return ", ".join(map(str,self.args))

class Or(ClauseExpr):
	def __init__(self, *args): self.args = args
	def __call__(self):
		try:
			for arg in self.args:
				for _ in arg(): yield 1
		except CutException: pass
	def __str__(self): return "; ".join(map(str,self.args))

class unify(ClauseExpr):
	def __init__(self, t1, t2): self.t1, self.t2 = t1, t2
	def __str__(self): return "%s=%s"%(self.t1, self.t2)
	def __call__(self):
		u = mgu(self.t1,self.t2)
		if u is not None:
			u.unify()
			yield 1
			u.undo()

class notunify(ClauseExpr):
	def __init__(self, t1, t2): self.t1, self.t2 = t1, t2
	def __str__(self): return "%s\=%s"%(self.t1, self.t2)
	def __call__(self):
		if mgu(self.t1,self.t2) is None: yield 1

##############################################################################
#                                                                            #
# PROLOG parser                                                              #
#                                                                            #
##############################################################################

_cut_string = lambda n: lambda s,n=n:s[n:-n]

#</python>

exec(tpg.compile(r"""

#<tpg>

parser PrologParser:

	separator spaces: '\s+|#.*';

	token predicate_name: '[a-z]\w*';
	token variable_name : '[A-Z]\w*|_\w+';
	token string        : "\"(\\.|[^\"\\]+)*\"|'(\\.|[^'\\]+)*'"    _cut_string<1>;
	token floating      : "\d+\.\d*|\.\d+"                          float;
	token integer       : "\d+"                                     int;

	START/rules.genCode<> -> rules=_Rules<> ( RULE/r rules-r )* ;

	RULE/_Rule<name, args, expr> ->
		predicate_name/name ARGS/args
		( ':-' EXPR/expr | expr=_True<>)
		'\.'
		;

	ARGS/args -> args = _Args<> ( '\(' ( TERM/a args-a ( ',' TERM/a args-a )* )? '\)' )?  ;

	TERM/a ->
			variable_name/n                a=_Var<n>
		|	'_'                            a=_AnonymousVar<>
		|	predicate_name/n
			(	ARGS/as
				{{ self.check(len(as)) }}  a=_Term<n,as>
			|	                           a=_Atom<n>
			)
		|	'\[' LIST/a '\]'
		|	string/s                       a=_String<s>
		|	integer/i                      a=_Integer<i>
		|	floating/f                     a=_Floating<f>
		|	'\(' OBJECT/a '\)'
		|	'py' '\(' OBJECTS/p '\)'       a=_Python<<p>>
		;

	OBJECT/o ->
			IDENT/o             SOBJECT<_Object<o>>/o
		|	string/o            SOBJECT<_String<o>>/o
		|	integer/o           SOBJECT<_Integer<o>>/o
		|	floating/o          SOBJECT<_Floating<o>>/o
		|	'\(' OBJECT/o '\)'  SOBJECT<o>/o
		|	'\(' OBJECTS/o '\)' SOBJECT<o>/o
		;

	SOBJECT<o>/o ->
		(	'\.' IDENT/o2        SOBJECT<_Composition<o,_Object<o2>>>/o
		|	'\(' OBJECTS/as '\)' SOBJECT<_Application<o,as>>/o
		|	'\[' INDICE/i '\]'   SOBJECT<_Indexation<o,i>>/o
		|	#
		)
		;

	OBJECTS/os -> os = _Objects<> ( OBJECT/o os-o ( ',' OBJECT/o os-o )*)? ;

	INDICE/i -> OBJECT/i ( ':' OBJECT/i2 i=_Slice<i,i2> )? ;

	IDENT/i -> variable_name/i | predicate_name/i | '_'/i ;

	EXPR/e -> e = _Or_expr<> IF_THEN_EXPR/e1 e-e1 ( (';'|'\|') IF_THEN_EXPR/e1 e-e1 )* ;

	IF_THEN_EXPR/e ->
		AND_EXPR/e
		(	'->' AND_EXPR/then_expr
			(	(';'|'\|') IF_THEN_EXPR/else_expr
			|	else_expr = _Fail<>
			)
			e=_IfThen_expr<e,then_expr,else_expr>
		|	'\*->' AND_EXPR/then_expr
			(	(';'|'\|') IF_THEN_EXPR/else_expr
			|	else_expr = _Fail<>
			)
			e=_SoftCut<e,then_expr,else_expr>
		)?
		;

	AND_EXPR/e -> e = _And_expr<> ATOM_EXPR/e1 e-e1 ( ',' ATOM_EXPR/e1 e-e1 )* ;

	ATOM_EXPR/a ->
			TERM/t '=\.\.' TERM/l    a=_Univ<t,l>
		|	TERM/t1 '==' TERM/t2     a=_Eq<t1,t2>
		|	TERM/t1 '\\==' TERM/t2   a=_Ne<t1,t2>
		|	TERM/t1 '=' TERM/t2      a=_Unify<t1,t2>
		|	TERM/t1 '\\=' TERM/t2    a=_NotUnify<t1,t2>
		|	TERM/t1 '<=' TERM/t2     a=_Le<t1,t2>
		|	TERM/t1 '<' TERM/t2      a=_Lt<t1,t2>
		|	TERM/t1 '>=' TERM/t2     a=_Ge<t1,t2>
		|	TERM/t1 '>' TERM/t2      a=_Gt<t1,t2>
		|	predicate_name/n ARGS/as a=_Call<n,as>
		|	'!'                      a=_Cut<>
		|	'true'                   a=_True<>
		|	'fail'                   a=_Fail<>
		|	'\(' EXPR/a '\)'
		|	'\\\+' ATOM_EXPR/a       a=_Neg<a>
		;

	LIST/l ->
			TERM/t SLIST<t>/l
		|	l = _Nil<>
		;

	SLIST<head>/l ->
			',' TERM/t SLIST<t>/tail l=_List<head,tail>
		|	'\|' TERM/tail           l=_List<head,tail>
		|	                         l=_List<head,_Nil<>>
		;

#</tpg>

"""))

#<python>

def compile(prolog): return _PrologParser(prolog)
_PrologParser = PrologParser()

def _flatten(L):
	""" Flatten a list. Each item is yielded """
	for i in L:
		if type(i) == list:
			for j in _flatten(i):
				yield j
		else:
			yield i

class _Rules(list):
	add = list.append
	def __str__(self): return "\n".join(map(str,self))
	def genCode(self):
		rules = self
		code = []
		while rules:
			predicate = [ r for r in rules if r.name==rules[0].name ]
			rules     = [ r for r in rules if r.name!=rules[0].name ]
			code = [ code, self.genPredicateCode(predicate) ]
		return "\n".join(_flatten(code))
	def genPredicateCode(self, predicate):
		name = predicate[0].name
		form_args = ", ".join([ "_a_%d"%i for i in range(len(predicate[0].args)) ])
		variables = _VariableCollector()
		for r in predicate: r.collectVariables(variables)
		return [
			"class %s(PyLogPredicate):"%name,
			"\t"	+ "def __init__(self, %s):"%form_args,
			"\t\t"		+ "self._form_args = Term(%s)"%form_args,
			["\t\t"		+ "%s = Var('%s')"%(v.genCode(), v.name) for v in variables],
			"\t\t"		+ "self._exprs = [",
			["\t\t\t"		+ "(Term(%s), lambda:%s),"%(r.genArgs(), r.genCode()) for r in predicate],
			"\t\t"		+ "]",
			"",
		]

class PyLogPredicate(ClauseExpr):
	def __call__(self):
		try:
			for args, expr in self._exprs:
				u = mgu(self._form_args, args)
				if u is not None:
					u.unify()
					try:
						for _ in expr()(): yield 1
					except CutException:
						u.undo()
						raise CutException
					u.undo()
		except CutException: pass
	def __str__(self): return "%s(%s)"%(self.__class__.__name__, ','.join(map(str,self._form_args.args)))

class _VariableCollector(list):
	def __init__(self):
		super(_VariableCollector,self).__init__()
		self.names = {}
	def collect(self, var):
		if var.name not in self.names:
			self.names[var.name] = 1
			self.append(var)

class _Rule:
	def __init__(self, name, args, expr):
		self.name = name
		self.args = args
		self.expr = expr
	def __str__(self): return "%s(%s) :- %s ."%(self.name, self.args, self.expr)
	def collectVariables(self, variables):
		self.args.collectVariables(variables)
		self.expr.collectVariables(variables)
	def genCode(self): return self.expr.genCode()
	def genArgs(self): return self.args.genCode()

class _Or_expr(list):
	add = list.append
	def __str__(self): return "; ".join(map(str,self))
	def collectVariables(self, variables):
		for item in self: item.collectVariables(variables)
	def genCode(self): return " | ".join([ item.genCode() for item in self ])

class _And_expr(list):
	add = list.append
	def __str__(self): return ", ".join(map(str,self))
	def collectVariables(self, variables):
		for item in self: item.collectVariables(variables)
	def genCode(self): return " & ".join([ "(%s)"%item.genCode() for item in self ])

class _IfThen_expr:
	def __init__(self, cond, then_expr, else_expr): self.cond, self.then_expr, self.else_expr = cond, then_expr, else_expr
	def __str__(self): return "%s -> %s ; %s"%(self.cond, self.then_expr, self.else_expr)
	def collectVariables(self, variables):
		self.cond.collectVariables(variables)
		self.then_expr.collectVariables(variables)
		self.else_expr.collectVariables(variables)
	def genCode(self): return "(%s) & cut & (%s) | (%s)"%(self.cond.genCode(), self.then_expr.genCode(), self.else_expr.genCode())

class _SoftCut:
	def __init__(self, cond, then_expr, else_expr): self.cond, self.then_expr, self.else_expr = cond, then_expr, else_expr
	def __str__(self): return "%s *-> %s ; %s"%(self.cond, self.then_expr, self.else_expr)
	def collectVariables(self, variables):
		self.cond.collectVariables(variables)
		self.then_expr.collectVariables(variables)
		self.else_expr.collectVariables(variables)
	def genCode(self): return "softcut(%s,%s,%s)"%(self.cond.genCode(), self.then_expr.genCode(), self.else_expr.genCode())

class _Call:
	def __init__(self, name, args): self.name, self.args = name, args
	def __str__(self): return "%s(%s)"%(self.name, self.args)
	def collectVariables(self, variables): self.args.collectVariables(variables)
	def genCode(self): return "%s(%s)"%(self.name, self.args.genCode())

class _Args(list):
	add = list.append
	def __str__(self): return ', '.join(map(str,self))
	def collectVariables(self, variables):
		for arg in self: arg.collectVariables(variables)
	def genCode(self): return ",".join([ a.genCode() for a in self ])

class _Comp:
	def __init__(self, t1, t2): self.t1, self.t2 = t1, t2
	def collectVariables(self, variables):
		self.t1.collectVariables(variables)
		self.t2.collectVariables(variables)

class _Univ(_Comp):
	def __str__(self): return "%s=..%s"%(self.t1, self.t2)
	def genCode(self): return "univ(%s,%s)"%(self.t1.genCode(), self.t2.genCode())

class _Unify(_Comp):
	def __str__(self): return "%s=%s"%(self.t1, self.t2)
	def genCode(self): return "unify(%s,%s)"%(self.t1.genCode(), self.t2.genCode())

class _NotUnify(_Comp):
	def __str__(self): return "%s=%s"%(self.t1, self.t2)
	def genCode(self): return "notunify(%s,%s)"%(self.t1.genCode(), self.t2.genCode())

class _Eq(_Comp):
	def __str__(self): return "%s==%s"%(self.t1, self.t2)
	def genCode(self): return "eq(%s,%s)"%(self.t1.genCode(), self.t2.genCode())

class _Ne(_Comp):
	def __str__(self): return "%s\==%s"%(self.t1, self.t2)
	def genCode(self): return "ne(%s,%s)"%(self.t1.genCode(), self.t2.genCode())

class _Lt(_Comp):
	def __str__(self): return "%s<%s"%(self.t1, self.t2)
	def genCode(self): return "lt(%s,%s)"%(self.t1.genCode(), self.t2.genCode())

class _Le(_Comp):
	def __str__(self): return "%s<=%s"%(self.t1, self.t2)
	def genCode(self): return "le(%s,%s)"%(self.t1.genCode(), self.t2.genCode())

class _Gt(_Comp):
	def __str__(self): return "%s>%s"%(self.t1, self.t2)
	def genCode(self): return "gt(%s,%s)"%(self.t1.genCode(), self.t2.genCode())

class _Ge(_Comp):
	def __str__(self): return "%s>=%s"%(self.t1, self.t2)
	def genCode(self): return "ge(%s,%s)"%(self.t1.genCode(), self.t2.genCode())

class _Neg:
	def __init__(self, a): self.a = a
	def __str__(self): return "\\+%s"%self.a
	def collectVariables(self, variables): self.a.collectVariables(variables)
	def genCode(self): return "(%s & cut & fail | true)"%self.a.genCode()

class _Term:
	def __init__(self, name, args): self.name, self.args, self.isarithmetic = name, args, 0
	def __str__(self): return "%s(%s)"%(self.name, self.args)
	def collectVariables(self, variables): self.args.collectVariables(variables)
	def genCode(self): return "%s(%s)"%(self.name, self.args.genCode())

class _Atom:
	def __init__(self, name): self.name = name
	def __str__(self): return self.name
	def collectVariables(self, variables): pass
	def genCode(self): return "Atom(atom('%s'))"%self.name

class _Var:
	def __init__(self, name): self.name = name
	def __str__(self): return self.name
	def collectVariables(self, variables): variables.collect(self)
	def genCode(self): return self.name

class _AnonymousVar:
	def __str__(self): return "_"
	def collectVariables(self, variables): pass
	def genCode(self): return "Var()"

class _List:
	def __init__(self, head, tail): self.head, self.tail = head, tail
	def __str__(self): return "[%s|%s]"%(self.head, self.tail)
	def collectVariables(self, variables):
		self.head.collectVariables(variables)
		self.tail.collectVariables(variables)
	def genCode(self): return "cons(%s,%s)"%(self.head.genCode(), self.tail.genCode())

class _Cut:
	def __str__(self): return "!"
	def collectVariables(self, variables): pass
	def genCode(self): return "cut"

class _True:
	def __str__(self): return "true"
	def collectVariables(self, variables): pass
	def genCode(self): return "true"

class _Fail:
	def __str__(self): return "fail"
	def collectVariables(self, variables): pass
	def genCode(self): return "fail"

class _Nil:
	def collectVariables(self, variables): pass
	def genCode(self): return "nil"
	def __str__(self): return "[]"

class _Integer:
	def __init__(self, i): self.val = i
	def collectVariables(self, variables): pass
	def genCode(self): return "Atom(%s)"%repr(self.val)
	def __str__(self): return str(self.val)

class _Floating:
	def __init__(self, f): self.val = f
	def collectVariables(self, variables): pass
	def genCode(self): return "Atom(%s)"%repr(self.val)
	def __str__(self): return str(self.val)

class _String:
	def __init__(self, s): self.val = s
	def collectVariables(self, variables): pass
	def genCode(self): return "Atom(%s)"%repr(self.val)
	def __str__(self): return str(self.val)

class _Python:
	def __init__(self, obj): self.obj = obj
	def collectVariables(self, variables): pass
	def genCode(self):
		if type(self.obj) == type(()):
			code = tuple([ o.genCode() for o in self.obj ])
		elif type(self.obj) == type([]):
			code = [ o.genCode() for o in self.obj ]
		else:
			code = self.obj.genCode()
		return "Atom((%s))"%code

	def __str__(self): return str(self.obj)

class _Objects(list):
	add = list.append
	def __str__(self): return ",".join(map(str,self))
	def genCode(self): return ",".join([o.genCode() for o in self])

class _Object:
	def __init__(self, name): self.name = name
	def __str__(self): return self.name
	def genCode(self): return self.name

class _Composition:
	def __init__(self, obj, meth): self.obj, self.meth = obj, meth
	def __str__(self): return "%s.%s"%(self.obj, self.meth)
	def genCode(self): return "%s.%s"%(self.obj.genCode(), self.meth.genCode())

class _Application:
	def __init__(self, obj, args): self.obj, self.args = obj, args
	def __str__(self): return "%s(%s)"%(self.obj, self.args)
	def genCode(self): return "%s(%s)"%(self.obj.genCode(), self.args.genCode())

class _Indexation:
	def __init__(self, obj, args): self.obj, self.args = obj, args
	def __str__(self): return "%s[%s]"%(self.obj, self.args)
	def genCode(self): return "%s[%s]"%(self.obj.genCode(), self.args.genCode())

class _Slice:
	def __init__(self, start, end): self.start, self.end = start, end
	def __str__(self): return "%s:%s"%(self.start, self.end)
	def genCode(self): return "%s:%s"%(self.start.genCode(), self.end.genCode())

##############################################################################
#                                                                            #
# PROLOG library                                                             #
#                                                                            #
##############################################################################

# Verify Type of a Term

class _is_type(ClauseExpr):
	def __init__(self, t): self.t = t

class is_var(_is_type):
	def __call__(self):
		if self.t.isfree(): yield 1

class is_nonvar(_is_type):
	def __call__(self):
		if not self.t.isfree(): yield 1

class is_integer(_is_type):
	def __call__(self):
		t = self.t.deref()
		if not t.isfree() and isinstance(t, Atom) and type(t.obj) in (type(0), type(0L)): yield 1

class is_float(_is_type):
	def __call__(self):
		t = self.t.deref()
		if not t.isfree() and isinstance(t, Atom) and type(t.obj)==type(0.0): yield 1

class is_number(_is_type):
	def __call__(self):
		t = self.t.deref()
		if not t.isfree() and isinstance(t, Atom) and type(t.obj) in (type(0), type(0L), type(0.0)): yield 1

class is_atomic(_is_type):
	def __call__(self):
		t = self.t.deref()
		if not t.isfree() and isinstance(t, Atom): yield 1

class is_atom(_is_type):
	def __call__(self):
		t = self.t.deref()
		if not t.isfree() and isinstance(t, Atom) and isinstance(t.obj, atom): yield 1

class is_string(_is_type):
	def __call__(self):
		t = self.t.deref()
		if not t.isfree() and isinstance(t, Atom) and type(t.obj)==type(""): yield 1

class is_compound(_is_type):
	def __call__(self):
		t = self.t.deref()
		if not t.isfree() and isinstance(t, Term) and t.arity()>0: yield 1

class is_ground(_is_type):
	def __call__(self):
		stack = [self.t.deref()]
		seen = {stack[0]:1}
		while stack:
			t = stack.pop()
			if t.isfree(): raise StopIteration
			if isinstance(t, Term):
				for a in t.args:
					if a not in seen:
						seen[a] = 1
						stack.append(a)
		yield 1
		
del _is_type

# Standard Order of Terms

class _cmp(ClauseExpr):
	def __init__(self, t1, t2): self.t1, self.t2 = t1, t2
	
class eq(_cmp):
	def __call__(self):
		if self.t1.deref()==self.t2.deref(): yield 1

class ne(_cmp):
	def __call__(self):
		if self.t1.deref()!=self.t2.deref(): yield 1

class lt(_cmp):
	def __call__(self):
		if self.t1.deref()<self.t2.deref(): yield 1

class le(_cmp):
	def __call__(self):
		if self.t1.deref()<=self.t2.deref(): yield 1

class gt(_cmp):
	def __call__(self):
		if self.t1.deref()>self.t2.deref(): yield 1

class ge(_cmp):
	def __call__(self):
		if self.t1.deref()>=self.t2.deref(): yield 1

class compare(ClauseExpr):
	def __init__(self, Order, Term1, Term2):
		self.Order, self.Term1, self.Term2 = Order, Term1, Term2
		self._compare =                                              \
			lt(self.Term1,self.Term2) & unify(self.Order,Atom('<'))  \
		|	eq(self.Term1,self.Term2) & unify(self.Order,Atom('='))  \
		|	gt(self.Term1,self.Term2) & unify(self.Order,Atom('>'))
	def __call__(self):
		for _ in self._compare(): yield 1

# Control Predicates

# fail, true, !, \+ and -> are already defined

class repeat(ClauseExpr):
	def __call__(self):
		while 1: yield 1
	def __str__(self): return "repeat"

class softcut(ClauseExpr):
	def __init__(self, cond, then_expr, else_expr):
		self.cond, self.then_expr, self.else_expr = cond, then_expr, else_expr
		self.true_expr = self.cond & self.then_expr
		self.false_expr = self.else_expr
	def __str__(self): return "%s *-> %s; %s"%(self.cond, self.then_expr, self.else_expr)
	def __call__(self):
		failed = 1
		for _ in self.true_expr():
			failed = 0
			yield 1
		if failed:
			for _ in self.false_expr():
				yield 1

# Analysing and Constructing Terms

class functor(ClauseExpr):
	def __init__(self, t, f, a):
		self.t, self.f, self.a = t, f, a
	def __str__(self): return "functor(%s,%s,%s)"%(self.t, self.f, self.a)
	def __call__(self):
		t, f, a = self.t.deref(), self.f.deref(), self.a.deref()
		if t.isfree():
			if isinstance(f, Atom) and isinstance(f.obj, atom) and isinstance(a, Atom) and type(a.obj) in (type(0), type(0L)):
				u = mgu(t, _termdef[f.obj.name](*[Var() for _ in range(a.obj)]))
				if u is not None:
					u.unify()
					yield 1
					u.undo()
		elif isinstance(t, Term):
			u = mgu(Term(f, a), Term(t.__class__.__name__, Atom(t.arity())))
			if u is not None:
				u.unify()
				yield 1
				u.undo()

class arg(ClauseExpr):
	def __init__(self, a, t, v):
		self.a, self.t, self.v = a, t, v
	def __str__(self): return "arg(%s,%s,%s)"%(self.a, self.t, self.v)
	def __call__(self):
		a, t, v = self.a.deref(), self.t.deref(), self.v.deref()
		if isinstance(t, Term):
			if a.isfree():
				for i in range(t.arity()):
					u = mgu(Term(a, v), Term(i+1, t.getarg(i)))
					if u is not None:
						u.unify()
						yield 1
						u.undo()
			elif isinstance(a, Atom) and type(a.obj) in (type(0), type(0L)):
				u = mgu(v, t.getarg(a.obj-1))
				if u is not None:
					u.unify()
					yield 1
					u.undo()

class setarg(ClauseExpr):
	def __init__(self, a, t, v):
		self.a, self.t, self.v = a, t, v
	def __str__(self): return "setarg(%s,%s,%s)"%(self.a, self.t, self.v)
	def __call__(self):
		a, t, v = self.a.deref(), self.t.deref(), self.v.deref()
		if isinstance(t, Term) and isinstance(a, Atom) and type(a.obj) in (type(0), type(0L)):
			i = a.obj-1
			old_v = t.getarg(i)
			t.setarg(i, v)
			yield 1
			t.setarg(i, old_v)

class univ(ClauseExpr):
	def __init__(self, t, l): self.t, self.l = t, l
	def __str__(self): return "%s=..%s"%(self.t, self.l)
	def __call__(self):
		t, l = self.t.deref(), self.l.deref()
		if isinstance(t, Term):
			u = mgu(l, cons(Atom(atom(t.__class__.__name__)), t.consarglist()))
			if u is not None:
				u.unify()
				yield 1
				u.undo()
		elif isinstance(l.head, Atom) and isinstance(l.head.obj, atom):
			u = mgu(t, _termdef[l.head.obj.name](*l.tail.pylist()))
			if u is not None:
				u.unify()
				yield 1
				u.undo()

# Arithmetic

class between(ClauseExpr):
	def __init__(self, low, high, value): self.low, self.high, self.value = low, high, value
	def __str__(self): return "between(%s,%s,%s)"%(self.low, self.high, self.value)
	def __call__(self):
		l, h = self.low.deref(), self.high.deref()
		if not isinstance(l, Atom) or type(l.obj) not in (type(0), type(0L)): return
		if not isinstance(h, Atom) or type(h.obj) not in (type(0), type(0L)): return
		v = self.value.deref()
		if v.isfree():
			for x in range(l.obj, h.obj+1):
				_v = v.term
				v.bind(x)
				yield 1
				v.term = _v
		else:
			if not isinstance(v, Atom) or type(v.obj) not in (type(0), type(0L)): return
			if l.obj <= v.obj <= h.obj: yield 1

class succ(ClauseExpr):
	def __init__(self, int1, int2): self.int1, self.int2 = int1, int2
	def __str__(self): return "succ(%s,%s)"%(self.int1, self.int2)
	def __call__(self):
		int1, int2 = self.int1.deref(), self.int2.deref()
		if isinstance(int1, Atom) and type(int1.obj) in (type(0), type(0L)):
			if isinstance(int2, Atom) and type(int2.obj) in (type(0), type(0L)):
				if int2.obj == int1.obj+1: yield 1
			elif int2.isfree():
				_int2 = int2.term
				int2.bind(int1.obj+1)
				yield 1
				int2.term = _int2
		elif isinstance(int2, Atom) and type(int2.obj) in (type(0), type(0L)):
			if int1.isfree():
				_int1 = int1.term
				int1.bind(int2.obj-1)
				yield 1
				int1.term = _int1

class plus(ClauseExpr):
	def __init__(self, a, b, c): self.a, self.b, self.c = a, b, c
	def __str__(self): return "plus(%s,%s,%s)"%(self.a, self.b, self.c)
	def __call__(self):
		a, b, c = self.a.deref(), self.b.deref(), self.c.deref()
		def isint(x): return isinstance(x, Atom) and type(x.obj) in (type(0), type(0L))
		if isint(a):
			if isint(b):
				if c.isfree():
					_c = c.term
					c.bind(a.obj+b.obj)
					yield 1
					c.term = _c
				elif isint(c) and c.obj==a.obj+b.obj: yield 1
			elif b.isfree() and isint(c):
				_b = b.term
				b.bind(c.obj-a.obj)
				yield 1
				b.term = _b
		elif a.isfree() and isint(b) and isint(c):
			_a = a.term
			a.bind(c.obj-b.obj)
			yield 1
			a.term = _a

# List Manipulation

#</python>

exec(compile(r"""

#<prolog>

is_list(X) :- is_var(X), !, fail.
is_list([]).
is_list([_|T]) :- is_list(T).

append([], L, L).
append([A|L1], L2, [A|L3]) :- append(L1, L2, L3).

member(X, [X|_]).
member(X, [_|L]) :- member(X, L).

memberchk(X, [X|_]) :- !.
memberchk(X, [_|L]) :- memberchk(X, L).

delete([], _, []).
delete([X|L1], X, L2) :- !, delete(L1, X, L2).
delete([Y|L1], X, [Y|L2]) :- delete(L1, X, L2).

select(X, [X|L], L).
select(X, [Y|L], [Y|R]) :- select(X, L, R).

nth0(I, L, E) :-
	(	is_integer(I)
	->	I >= 0,
		zz_nth_det(I, L, E)
	;	zz_nth_gen(0, I, L, E)
	).

nth1(I, L, E) :-
	(	is_integer(I)
	->	succ(I0, I),
		zz_nth_det(I0, L, E)
	;	zz_nth_gen(1, I, L, E)
	).

zz_nth_det(0, [E|_], E) :- !.
zz_nth_det(I, [_|L], E) :- succ(I1,I), zz_nth_det(I1, L, E).

zz_nth_gen(I, I, [E|_], E).
zz_nth_gen(J, I, [_|L], E) :- succ(J, J1), zz_nth_gen(J1, I, L, E).

last(E, [E]).
last(E, [_|L]) :- last(E, L).

reverse(L, R) :- zz_reverse(L, [], R).

zz_reverse([], R, R).
zz_reverse([X|L], R1, R2) :- zz_reverse(L, [X|R1], R2).

flatten([], []) :- !.
flatten(A, [A]) :- is_atomic(A), !.
flatten([A], L) :- !, flatten(A, L).
flatten([A|B], L) :- flatten(A,FA), flatten(B,FB), append(FA,FB,L).

length([], 0).
length([_|L], N1) :- length(L, N), succ(N, N1).

merge([], L, L).
merge(L, [], L).
merge([X|L1], [Y|L2], [Z|L]) :-
	(	X < Y
	->	Z = X,
		merge(L1, [Y|L2], L)
	;	Z = Y,
		merge([X|L1], L2, L)
	).

#</prolog>

"""))

#<python>

# Set Manipulation

#</python>

exec(compile(r"""

#<prolog>

is_set(0) :- !, fail.
is_set([]) :- !.
is_set([X|S]) :- memberchk(X,S), !, fail.
is_set([_|S]) :- is_set(S).

list_to_set([],[]).
list_to_set([X|L], [X|S]) :- delete(L, X, L1), list_to_set(L1, S).

intersection([], _, []) :- !.
intersection([X|S1], S2, [X|S]) :- memberchk(X, S2), !, intersection(S1, S2, S).
intersection([_|S1], S2, S) :- intersection(S1, S2, S).

subtract([], _, []) :- !.
subtract([X|S1], S2, S) :- memberchk(X, S2), !, subtract(S1, S2, S).
subtract([X|S1], S2, [X|S]) :- subtract(S1, S2, S).

union([], S, S) :- !.
union([X|S1], S2, S) :- memberchk(X, S2), !, union(S1, S2, S).
union([X|S1], S2, [X|S]) :- union(S1, S2, S).

subset([], S) :- !.
subset([X|SS], S) :- memberchk(X, S), subset(SS, S).

merge_set([], S, S) :- !.
merge_set(S, [], S) :- !.
merge_set([X|S1], [Y|S2], [X|S]) :- X<Y, !, merge_set(S1, [Y|S2], S).
merge_set([X|S1], [Y|S2], [Y|S]) :- X>Y, !, merge_set([X|S1], S2, S).
merge_set([X|S1], [Y|S2], [X|S]) :- X==Y, !, merge_set(S1, S2, S).

#</prolog>

"""))

#<python>

# Sorting Lists

#</python>

exec(compile(r"""

#<prolog>

sort(L, S) :- zz_sort(L, S).

zz_sort([], []) :- !.
zz_sort([X], [X]) :- !.
zz_sort([X|L], S) :-
	zz_sort_split(X,L,INF,SUP),
	zz_sort(INF, SINF),
	zz_sort(SUP, SSUP),
	append(SINF, [X|SSUP], S).

zz_sort_split(_, [], [], []) :- !.
zz_sort_split(X, [Y|L], INF, [Y|SUP]) :- X<Y, !, zz_sort_split(X, L, INF, SUP).
zz_sort_split(X, [Y|L], [Y|INF], SUP) :- X>Y, !, zz_sort_split(X, L, INF, SUP).
zz_sort_split(X, [Y|L], INF, SUP) :- X==Y, zz_sort_split(X, L, INF, SUP).

msort(L, S) :- zz_msort(L, S).

zz_msort([], []) :- !.
zz_msort([X], [X]) :- !.
zz_msort([X|L], S) :-
	zz_msort_split(X,L,INF,SUP),
	zz_msort(INF, SINF),
	zz_msort(SUP, SSUP),
	append(SINF, [X|SSUP], S).

zz_msort_split(_, [], [], []) :- !.
zz_msort_split(X, [Y|L], INF, [Y|SUP]) :- X<=Y, !, zz_msort_split(X, L, INF, SUP).
zz_msort_split(X, [Y|L], [Y|INF], SUP) :- X>Y, !, zz_msort_split(X, L, INF, SUP).

#</prolog>

"""))

if __name__ == '__main__':

	import sys

	if sys.argv[1:] == [ '--build' ]:

		print "Building PyLog..."

		start = lambda s: s[2:-2]
		stop = lambda s: s[3:-2]

		class List(list):
			add = list.append

		def GenCode(lines, tag):
			return {
				"python": lambda code: code,
				"tpg"   : lambda code: tpg.compile(code).replace('from __future__ import generators',''),
				"prolog": compile,
			}[tag]("".join(lines))
		
		exec(tpg.compile(r"""

			parser TagParser:

				token start: '#<\w+>\n' start ;
				token stop: '#</\w+>\n' stop ;
				token line: '.*\n' ;

				TAG/tag -> start/tag ;
				END<tag> -> stop/s {{ self.check(s==tag) }} ;

				START/{{"".join(code)}} ->
					code = List<>
					line/l code-l	# #/usr/bin/env python
					(	TAG/tag
							block = List<>
							( line/l block-l )*
						END<tag>
						code-GenCode<block,tag>
					|	line
					)*
					;

		"""))

		source_file = sys.argv[0]
		compiled_file = 'pylog.py'
		print "\tReading source file (%s)"%source_file
		tag_parser = TagParser()
		f = open(source_file)
		src = f.read()
		f.close()
		print "\tGenerating Python code"
		code = tag_parser(src)
		print "\tSaving compiled file (%s)"%compiled_file
		f = open(compiled_file, 'w')
		f.write(code)
		f.close()
		print "Done"
		print "Have fun with PyLog ;-)"
