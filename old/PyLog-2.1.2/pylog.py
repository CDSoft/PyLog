#!/usr/bin/env python

""" PyLog is a first order logic library and a PROLOG engine in Python """

from __future__ import generators
import tpg

__date__ = "15 january 2004"
__version__ = "2.1.2"
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
        u = Unifier()                                   # current unifier
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


class PrologParser(tpg.Parser):
    __grammar__ = r"""

        separator spaces: '\s+|#.*';

        token predicate_name: '[a-z]\w*'                                ;
        token variable_name : '[A-Z]\w*|_\w+'                           ;
        token string        : "\"(\\.|[^\"\\]+)*\"|'(\\.|[^'\\]+)*'"    $ lambda s: s[1:-1]
        token floating      : "\d+\.\d*|\.\d+"                          float
        token integer       : "\d+"                                     int

        START/$rules.genCode()$ -> $rules=_Rules()$ ( RULE/r $rules.add(r)$ )* ;

        RULE/$_Rule(name, args, expr)$ ->
                predicate_name/name ARGS/args
                ( ':-' EXPR/expr | $expr=_True()$)
                '\.'
                ;

        ARGS/args -> $args = _Args()$ ( '\(' ( TERM/a $args.add(a)$ ( ',' TERM/a $args.add(a)$ )* )? '\)' )?  ;

        TERM/a ->
                        variable_name/n                 $ a=_Var(n)
                |       '_'                             $ a=_AnonymousVar()
                |       predicate_name/n
                        (       ARGS/as
                                check $len(as)$         $ a=_Term(n,as)
                        |                               $ a=_Atom(n)
                        )
                |       '\[' LIST/a '\]'
                |       string/s                        $ a=_String(s)
                |       integer/i                       $ a=_Integer(i)
                |       floating/f                      $ a=_Floating(f)
                |       '\(' OBJECT/a '\)'
                |       'py' '\(' OBJECTS/p '\)'        $ a=_Python((p,))
                ;

        OBJECT/o ->
                        IDENT/o             SOBJECT<$_Object(o)$>/o
                |       string/o            SOBJECT<$_String(o)$>/o
                |       integer/o           SOBJECT<$_Integer(o)$>/o
                |       floating/o          SOBJECT<$_Floating(o)$>/o
                |       '\(' OBJECT/o '\)'  SOBJECT<o>/o
                |       '\(' OBJECTS/o '\)' SOBJECT<o>/o
                ;

        SOBJECT<o>/o ->
                (       '\.' IDENT/o2        SOBJECT<$_Composition(o,_Object(o2))$>/o
                |       '\(' OBJECTS/as '\)' SOBJECT<$_Application(o,as)$>/o
                |       '\[' INDICE/i '\]'   SOBJECT<$_Indexation(o,i)$>/o
                |       #
                )
                ;

        OBJECTS/os -> $os = _Objects()$ ( OBJECT/o $os.add(o)$ ( ',' OBJECT/o $os.add(o)$ )*)? ;

        INDICE/i -> OBJECT/i ( ':' OBJECT/i2 $i=_Slice(i,i2)$ )? ;

        IDENT/i -> variable_name/i | predicate_name/i | '_'/i ;

        EXPR/e -> $e = _Or_expr()$ IF_THEN_EXPR/e1 $e.add(e1)$ ( (';'|'\|') IF_THEN_EXPR/e1 $e.add(e1)$ )* ;

        IF_THEN_EXPR/e ->
                AND_EXPR/e
                (       '->' AND_EXPR/then_expr
                        (       (';'|'\|') IF_THEN_EXPR/else_expr
                        |       $ else_expr = _Fail()
                        )
                        $ e=_IfThen_expr(e,then_expr,else_expr)
                |       '\*->' AND_EXPR/then_expr
                        (       (';'|'\|') IF_THEN_EXPR/else_expr
                        |       $ else_expr = _Fail()
                        )
                        $ e=_SoftCut(e,then_expr,else_expr)
                )?
                ;

        AND_EXPR/e -> $e = _And_expr()$ ATOM_EXPR/e1 $e.add(e1)$ ( ',' ATOM_EXPR/e1 $e.add(e1)$ )* ;

        ATOM_EXPR/a ->
                        TERM/t '=\.\.' TERM/l    $ a=_Univ(t,l)
                |       TERM/t1 '==' TERM/t2     $ a=_Eq(t1,t2)
                |       TERM/t1 '\\==' TERM/t2   $ a=_Ne(t1,t2)
                |       TERM/t1 '=' TERM/t2      $ a=_Unify(t1,t2)
                |       TERM/t1 '\\=' TERM/t2    $ a=_NotUnify(t1,t2)
                |       TERM/t1 '<=' TERM/t2     $ a=_Le(t1,t2)
                |       TERM/t1 '<' TERM/t2      $ a=_Lt(t1,t2)
                |       TERM/t1 '>=' TERM/t2     $ a=_Ge(t1,t2)
                |       TERM/t1 '>' TERM/t2      $ a=_Gt(t1,t2)
                |       predicate_name/n ARGS/as $ a=_Call(n,as)
                |       '!'                      $ a=_Cut()
                |       'true'                   $ a=_True()
                |       'fail'                   $ a=_Fail()
                |       '\(' EXPR/a '\)'
                |       '\\\+' ATOM_EXPR/a       $ a=_Neg(a)
                ;

        LIST/l ->
                        TERM/t SLIST<t>/l
                |       $ l = _Nil()
                ;

        SLIST<head>/l ->
                        ',' TERM/t SLIST<t>/tail $ l=_List(head,tail)
                |       '\|' TERM/tail           $ l=_List(head,tail)
                |                                $ l=_List(head,_Nil())
                ;

    """

    def init_lexer(self):
        lexer = tpg.NamedGroupLexer(True, 0)
        lexer.def_token('_tok_1', r':-')
        lexer.def_token('_tok_2', r'\.')
        lexer.def_token('_tok_3', r'\(')
        lexer.def_token('_tok_4', r',')
        lexer.def_token('_tok_5', r'\)')
        lexer.def_token('_tok_6', r'_')
        lexer.def_token('_tok_7', r'\[')
        lexer.def_token('_tok_8', r'\]')
        lexer.def_token('_tok_9', r'py')
        lexer.def_token('_tok_10', r':')
        lexer.def_token('_tok_11', r';')
        lexer.def_token('_tok_12', r'\|')
        lexer.def_token('_tok_13', r'->')
        lexer.def_token('_tok_14', r'\*->')
        lexer.def_token('_tok_15', r'=\.\.')
        lexer.def_token('_tok_16', r'==')
        lexer.def_token('_tok_17', r'\\==')
        lexer.def_token('_tok_18', r'=')
        lexer.def_token('_tok_19', r'\\=')
        lexer.def_token('_tok_20', r'<=')
        lexer.def_token('_tok_21', r'<')
        lexer.def_token('_tok_22', r'>=')
        lexer.def_token('_tok_23', r'>')
        lexer.def_token('_tok_24', r'!')
        lexer.def_token('_tok_25', r'true')
        lexer.def_token('_tok_26', r'fail')
        lexer.def_token('_tok_27', r'\\\+')
        lexer.def_separator('spaces', r'\s+|#.*')
        lexer.def_token('predicate_name', r'[a-z]\w*')
        lexer.def_token('variable_name', r'[A-Z]\w*|_\w+')
        lexer.def_token('string', r"\"(\\.|[^\"\\]+)*\"|'(\\.|[^'\\]+)*'", lambda s: s[1:-1])
        lexer.def_token('floating', r"\d+\.\d*|\.\d+", float)
        lexer.def_token('integer', r"\d+", int)
        return lexer

    def START(self, ):
        r""" START -> (RULE)* """
        rules=_Rules()
        while True:
            _p1 = self.lexer.token()
            try:
                r = self.RULE()
                rules.add(r)
            except tpg.WrongToken:
                self.lexer.back(_p1)
                break
        return rules.genCode()

    def RULE(self, ):
        r""" RULE -> predicate_name ARGS (':-' EXPR | ) '\.' """
        name = self.eat('predicate_name')
        args = self.ARGS()
        _p1 = self.lexer.token()
        try:
            self.eat('_tok_1') # ':-'
            expr = self.EXPR()
        except tpg.WrongToken:
            self.lexer.back(_p1)
            expr=_True()
        self.eat('_tok_2') # '\.'
        return _Rule(name, args, expr)

    def ARGS(self, ):
        r""" ARGS -> ('\(' (TERM (',' TERM)*)? '\)')? """
        args = _Args()
        _p1 = self.lexer.token()
        try:
            self.eat('_tok_3') # '\('
            _p2 = self.lexer.token()
            try:
                a = self.TERM()
                args.add(a)
                while True:
                    _p3 = self.lexer.token()
                    try:
                        self.eat('_tok_4') # ','
                        a = self.TERM()
                        args.add(a)
                    except tpg.WrongToken:
                        self.lexer.back(_p3)
                        break
            except tpg.WrongToken:
                self.lexer.back(_p2)
            self.eat('_tok_5') # '\)'
        except tpg.WrongToken:
            self.lexer.back(_p1)
        return args

    def TERM(self, ):
        r""" TERM -> variable_name | '_' | predicate_name (ARGS | ) | '\[' LIST '\]' | string | integer | floating | '\(' OBJECT '\)' | 'py' '\(' OBJECTS '\)' """
        _p1 = self.lexer.token()
        try:
            try:
                try:
                    n = self.eat('variable_name')
                    a=_Var(n)
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    self.eat('_tok_6') # '_'
                    a=_AnonymousVar()
            except tpg.WrongToken:
                self.lexer.back(_p1)
                try:
                    n = self.eat('predicate_name')
                    _p2 = self.lexer.token()
                    try:
                        as = self.ARGS()
                        self.check(len(as))
                        a=_Term(n,as)
                    except tpg.WrongToken:
                        self.lexer.back(_p2)
                        a=_Atom(n)
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    self.eat('_tok_7') # '\['
                    a = self.LIST()
                    self.eat('_tok_8') # '\]'
        except tpg.WrongToken:
            self.lexer.back(_p1)
            try:
                try:
                    s = self.eat('string')
                    a=_String(s)
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    i = self.eat('integer')
                    a=_Integer(i)
            except tpg.WrongToken:
                self.lexer.back(_p1)
                try:
                    f = self.eat('floating')
                    a=_Floating(f)
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    try:
                        self.eat('_tok_3') # '\('
                        a = self.OBJECT()
                        self.eat('_tok_5') # '\)'
                    except tpg.WrongToken:
                        self.lexer.back(_p1)
                        self.eat('_tok_9') # 'py'
                        self.eat('_tok_3') # '\('
                        p = self.OBJECTS()
                        self.eat('_tok_5') # '\)'
                        a=_Python((p,))
        return a

    def OBJECT(self, ):
        r""" OBJECT -> IDENT SOBJECT | string SOBJECT | integer SOBJECT | floating SOBJECT | '\(' OBJECT '\)' SOBJECT | '\(' OBJECTS '\)' SOBJECT """
        _p1 = self.lexer.token()
        try:
            try:
                o = self.IDENT()
                o = self.SOBJECT(_Object(o))
            except tpg.WrongToken:
                self.lexer.back(_p1)
                try:
                    o = self.eat('string')
                    o = self.SOBJECT(_String(o))
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    o = self.eat('integer')
                    o = self.SOBJECT(_Integer(o))
        except tpg.WrongToken:
            self.lexer.back(_p1)
            try:
                o = self.eat('floating')
                o = self.SOBJECT(_Floating(o))
            except tpg.WrongToken:
                self.lexer.back(_p1)
                try:
                    self.eat('_tok_3') # '\('
                    o = self.OBJECT()
                    self.eat('_tok_5') # '\)'
                    o = self.SOBJECT(o)
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    self.eat('_tok_3') # '\('
                    o = self.OBJECTS()
                    self.eat('_tok_5') # '\)'
                    o = self.SOBJECT(o)
        return o

    def SOBJECT(self, o):
        r""" SOBJECT -> '\.' IDENT SOBJECT | '\(' OBJECTS '\)' SOBJECT | '\[' INDICE '\]' SOBJECT |  """
        _p1 = self.lexer.token()
        try:
            try:
                self.eat('_tok_2') # '\.'
                o2 = self.IDENT()
                o = self.SOBJECT(_Composition(o,_Object(o2)))
            except tpg.WrongToken:
                self.lexer.back(_p1)
                self.eat('_tok_3') # '\('
                as = self.OBJECTS()
                self.eat('_tok_5') # '\)'
                o = self.SOBJECT(_Application(o,as))
        except tpg.WrongToken:
            self.lexer.back(_p1)
            try:
                self.eat('_tok_7') # '\['
                i = self.INDICE()
                self.eat('_tok_8') # '\]'
                o = self.SOBJECT(_Indexation(o,i))
            except tpg.WrongToken:
                self.lexer.back(_p1)
        return o

    def OBJECTS(self, ):
        r""" OBJECTS -> (OBJECT (',' OBJECT)*)? """
        os = _Objects()
        _p1 = self.lexer.token()
        try:
            o = self.OBJECT()
            os.add(o)
            while True:
                _p2 = self.lexer.token()
                try:
                    self.eat('_tok_4') # ','
                    o = self.OBJECT()
                    os.add(o)
                except tpg.WrongToken:
                    self.lexer.back(_p2)
                    break
        except tpg.WrongToken:
            self.lexer.back(_p1)
        return os

    def INDICE(self, ):
        r""" INDICE -> OBJECT (':' OBJECT)? """
        i = self.OBJECT()
        _p1 = self.lexer.token()
        try:
            self.eat('_tok_10') # ':'
            i2 = self.OBJECT()
            i=_Slice(i,i2)
        except tpg.WrongToken:
            self.lexer.back(_p1)
        return i

    def IDENT(self, ):
        r""" IDENT -> variable_name | predicate_name | '_' """
        _p1 = self.lexer.token()
        try:
            i = self.eat('variable_name')
        except tpg.WrongToken:
            self.lexer.back(_p1)
            try:
                i = self.eat('predicate_name')
            except tpg.WrongToken:
                self.lexer.back(_p1)
                i = self.eat('_tok_6') # '_'
        return i

    def EXPR(self, ):
        r""" EXPR -> IF_THEN_EXPR ((';' | '\|') IF_THEN_EXPR)* """
        e = _Or_expr()
        e1 = self.IF_THEN_EXPR()
        e.add(e1)
        while True:
            _p1 = self.lexer.token()
            try:
                try:
                    self.eat('_tok_11') # ';'
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    self.eat('_tok_12') # '\|'
                e1 = self.IF_THEN_EXPR()
                e.add(e1)
            except tpg.WrongToken:
                self.lexer.back(_p1)
                break
        return e

    def IF_THEN_EXPR(self, ):
        r""" IF_THEN_EXPR -> AND_EXPR ('->' AND_EXPR ((';' | '\|') IF_THEN_EXPR | ) | '\*->' AND_EXPR ((';' | '\|') IF_THEN_EXPR | ))? """
        e = self.AND_EXPR()
        _p1 = self.lexer.token()
        try:
            try:
                self.eat('_tok_13') # '->'
                then_expr = self.AND_EXPR()
                _p2 = self.lexer.token()
                try:
                    try:
                        self.eat('_tok_11') # ';'
                    except tpg.WrongToken:
                        self.lexer.back(_p2)
                        self.eat('_tok_12') # '\|'
                    else_expr = self.IF_THEN_EXPR()
                except tpg.WrongToken:
                    self.lexer.back(_p2)
                    else_expr = _Fail()
                e=_IfThen_expr(e,then_expr,else_expr)
            except tpg.WrongToken:
                self.lexer.back(_p1)
                self.eat('_tok_14') # '\*->'
                then_expr = self.AND_EXPR()
                _p3 = self.lexer.token()
                try:
                    try:
                        self.eat('_tok_11') # ';'
                    except tpg.WrongToken:
                        self.lexer.back(_p3)
                        self.eat('_tok_12') # '\|'
                    else_expr = self.IF_THEN_EXPR()
                except tpg.WrongToken:
                    self.lexer.back(_p3)
                    else_expr = _Fail()
                e=_SoftCut(e,then_expr,else_expr)
        except tpg.WrongToken:
            self.lexer.back(_p1)
        return e

    def AND_EXPR(self, ):
        r""" AND_EXPR -> ATOM_EXPR (',' ATOM_EXPR)* """
        e = _And_expr()
        e1 = self.ATOM_EXPR()
        e.add(e1)
        while True:
            _p1 = self.lexer.token()
            try:
                self.eat('_tok_4') # ','
                e1 = self.ATOM_EXPR()
                e.add(e1)
            except tpg.WrongToken:
                self.lexer.back(_p1)
                break
        return e

    def ATOM_EXPR(self, ):
        r""" ATOM_EXPR -> TERM '=\.\.' TERM | TERM '==' TERM | TERM '\\==' TERM | TERM '=' TERM | TERM '\\=' TERM | TERM '<=' TERM | TERM '<' TERM | TERM '>=' TERM | TERM '>' TERM | predicate_name ARGS | '!' | 'true' | 'fail' | '\(' EXPR '\)' | '\\\+' ATOM_EXPR """
        _p1 = self.lexer.token()
        try:
            try:
                try:
                    t = self.TERM()
                    self.eat('_tok_15') # '=\.\.'
                    l = self.TERM()
                    a=_Univ(t,l)
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    try:
                        t1 = self.TERM()
                        self.eat('_tok_16') # '=='
                        t2 = self.TERM()
                        a=_Eq(t1,t2)
                    except tpg.WrongToken:
                        self.lexer.back(_p1)
                        t1 = self.TERM()
                        self.eat('_tok_17') # '\\=='
                        t2 = self.TERM()
                        a=_Ne(t1,t2)
            except tpg.WrongToken:
                self.lexer.back(_p1)
                try:
                    try:
                        t1 = self.TERM()
                        self.eat('_tok_18') # '='
                        t2 = self.TERM()
                        a=_Unify(t1,t2)
                    except tpg.WrongToken:
                        self.lexer.back(_p1)
                        t1 = self.TERM()
                        self.eat('_tok_19') # '\\='
                        t2 = self.TERM()
                        a=_NotUnify(t1,t2)
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    try:
                        t1 = self.TERM()
                        self.eat('_tok_20') # '<='
                        t2 = self.TERM()
                        a=_Le(t1,t2)
                    except tpg.WrongToken:
                        self.lexer.back(_p1)
                        t1 = self.TERM()
                        self.eat('_tok_21') # '<'
                        t2 = self.TERM()
                        a=_Lt(t1,t2)
        except tpg.WrongToken:
            self.lexer.back(_p1)
            try:
                try:
                    try:
                        t1 = self.TERM()
                        self.eat('_tok_22') # '>='
                        t2 = self.TERM()
                        a=_Ge(t1,t2)
                    except tpg.WrongToken:
                        self.lexer.back(_p1)
                        t1 = self.TERM()
                        self.eat('_tok_23') # '>'
                        t2 = self.TERM()
                        a=_Gt(t1,t2)
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    try:
                        n = self.eat('predicate_name')
                        as = self.ARGS()
                        a=_Call(n,as)
                    except tpg.WrongToken:
                        self.lexer.back(_p1)
                        self.eat('_tok_24') # '!'
                        a=_Cut()
            except tpg.WrongToken:
                self.lexer.back(_p1)
                try:
                    try:
                        self.eat('_tok_25') # 'true'
                        a=_True()
                    except tpg.WrongToken:
                        self.lexer.back(_p1)
                        self.eat('_tok_26') # 'fail'
                        a=_Fail()
                except tpg.WrongToken:
                    self.lexer.back(_p1)
                    try:
                        self.eat('_tok_3') # '\('
                        a = self.EXPR()
                        self.eat('_tok_5') # '\)'
                    except tpg.WrongToken:
                        self.lexer.back(_p1)
                        self.eat('_tok_27') # '\\\+'
                        a = self.ATOM_EXPR()
                        a=_Neg(a)
        return a

    def LIST(self, ):
        r""" LIST -> TERM SLIST |  """
        _p1 = self.lexer.token()
        try:
            t = self.TERM()
            l = self.SLIST(t)
        except tpg.WrongToken:
            self.lexer.back(_p1)
            l = _Nil()
        return l

    def SLIST(self, head):
        r""" SLIST -> ',' TERM SLIST | '\|' TERM |  """
        _p1 = self.lexer.token()
        try:
            self.eat('_tok_4') # ','
            t = self.TERM()
            tail = self.SLIST(t)
            l=_List(head,tail)
        except tpg.WrongToken:
            self.lexer.back(_p1)
            try:
                self.eat('_tok_12') # '\|'
                tail = self.TERM()
                l=_List(head,tail)
            except tpg.WrongToken:
                self.lexer.back(_p1)
                l=_List(head,_Nil())
        return l



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
                        "\t"    + "def __init__(self, %s):"%form_args,
                        "\t\t"          + "self._form_args = Term(%s)"%form_args,
                        ["\t\t"         + "%s = Var('%s')"%(v.genCode(), v.name) for v in variables],
                        "\t\t"          + "self._exprs = [",
                        ["\t\t\t"               + "(Term(%s), lambda:%s),"%(r.genArgs(), r.genCode()) for r in predicate],
                        "\t\t"          + "]",
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
                |       eq(self.Term1,self.Term2) & unify(self.Order,Atom('='))  \
                |       gt(self.Term1,self.Term2) & unify(self.Order,Atom('>'))
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

class is_list(PyLogPredicate):
	def __init__(self, _a_0):
		self._form_args = Term(_a_0)
		X = Var('X')
		T = Var('T')
		self._exprs = [
			(Term(X), lambda:(is_var(X)) & (cut) & (fail)),
			(Term(nil), lambda:true),
			(Term(cons(Var(),T)), lambda:(is_list(T))),
		]

class append(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		L = Var('L')
		A = Var('A')
		L1 = Var('L1')
		L2 = Var('L2')
		L3 = Var('L3')
		self._exprs = [
			(Term(nil,L,L), lambda:true),
			(Term(cons(A,L1),L2,cons(A,L3)), lambda:(append(L1,L2,L3))),
		]

class member(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		X = Var('X')
		L = Var('L')
		self._exprs = [
			(Term(X,cons(X,Var())), lambda:true),
			(Term(X,cons(Var(),L)), lambda:(member(X,L))),
		]

class memberchk(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		X = Var('X')
		L = Var('L')
		self._exprs = [
			(Term(X,cons(X,Var())), lambda:(cut)),
			(Term(X,cons(Var(),L)), lambda:(memberchk(X,L))),
		]

class delete(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		X = Var('X')
		L1 = Var('L1')
		L2 = Var('L2')
		Y = Var('Y')
		self._exprs = [
			(Term(nil,Var(),nil), lambda:true),
			(Term(cons(X,L1),X,L2), lambda:(cut) & (delete(L1,X,L2))),
			(Term(cons(Y,L1),X,cons(Y,L2)), lambda:(delete(L1,X,L2))),
		]

class select(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		X = Var('X')
		L = Var('L')
		Y = Var('Y')
		R = Var('R')
		self._exprs = [
			(Term(X,cons(X,L),L), lambda:true),
			(Term(X,cons(Y,L),cons(Y,R)), lambda:(select(X,L,R))),
		]

class nth0(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		I = Var('I')
		L = Var('L')
		E = Var('E')
		self._exprs = [
			(Term(I,L,E), lambda:(((is_integer(I))) & cut & ((ge(I,Atom(0))) & (zz_nth_det(I,L,E))) | ((zz_nth_gen(Atom(0),I,L,E))))),
		]

class nth1(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		I = Var('I')
		L = Var('L')
		E = Var('E')
		I0 = Var('I0')
		self._exprs = [
			(Term(I,L,E), lambda:(((is_integer(I))) & cut & ((succ(I0,I)) & (zz_nth_det(I0,L,E))) | ((zz_nth_gen(Atom(1),I,L,E))))),
		]

class zz_nth_det(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		E = Var('E')
		I = Var('I')
		L = Var('L')
		I1 = Var('I1')
		self._exprs = [
			(Term(Atom(0),cons(E,Var()),E), lambda:(cut)),
			(Term(I,cons(Var(),L),E), lambda:(succ(I1,I)) & (zz_nth_det(I1,L,E))),
		]

class zz_nth_gen(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2, _a_3):
		self._form_args = Term(_a_0, _a_1, _a_2, _a_3)
		I = Var('I')
		E = Var('E')
		J = Var('J')
		L = Var('L')
		J1 = Var('J1')
		self._exprs = [
			(Term(I,I,cons(E,Var()),E), lambda:true),
			(Term(J,I,cons(Var(),L),E), lambda:(succ(J,J1)) & (zz_nth_gen(J1,I,L,E))),
		]

class last(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		E = Var('E')
		L = Var('L')
		self._exprs = [
			(Term(E,cons(E,nil)), lambda:true),
			(Term(E,cons(Var(),L)), lambda:(last(E,L))),
		]

class reverse(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		L = Var('L')
		R = Var('R')
		self._exprs = [
			(Term(L,R), lambda:(zz_reverse(L,nil,R))),
		]

class zz_reverse(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		R = Var('R')
		X = Var('X')
		L = Var('L')
		R1 = Var('R1')
		R2 = Var('R2')
		self._exprs = [
			(Term(nil,R,R), lambda:true),
			(Term(cons(X,L),R1,R2), lambda:(zz_reverse(L,cons(X,R1),R2))),
		]

class flatten(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		A = Var('A')
		L = Var('L')
		B = Var('B')
		FA = Var('FA')
		FB = Var('FB')
		self._exprs = [
			(Term(nil,nil), lambda:(cut)),
			(Term(A,cons(A,nil)), lambda:(is_atomic(A)) & (cut)),
			(Term(cons(A,nil),L), lambda:(cut) & (flatten(A,L))),
			(Term(cons(A,B),L), lambda:(flatten(A,FA)) & (flatten(B,FB)) & (append(FA,FB,L))),
		]

class length(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		L = Var('L')
		N1 = Var('N1')
		N = Var('N')
		self._exprs = [
			(Term(nil,Atom(0)), lambda:true),
			(Term(cons(Var(),L),N1), lambda:(length(L,N)) & (succ(N,N1))),
		]

class merge(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		L = Var('L')
		X = Var('X')
		L1 = Var('L1')
		Y = Var('Y')
		L2 = Var('L2')
		Z = Var('Z')
		self._exprs = [
			(Term(nil,L,L), lambda:true),
			(Term(L,nil,L), lambda:true),
			(Term(cons(X,L1),cons(Y,L2),cons(Z,L)), lambda:(((lt(X,Y))) & cut & ((unify(Z,X)) & (merge(L1,cons(Y,L2),L))) | ((unify(Z,Y)) & (merge(cons(X,L1),L2,L))))),
		]

# Set Manipulation

class is_set(PyLogPredicate):
	def __init__(self, _a_0):
		self._form_args = Term(_a_0)
		X = Var('X')
		S = Var('S')
		self._exprs = [
			(Term(Atom(0)), lambda:(cut) & (fail)),
			(Term(nil), lambda:(cut)),
			(Term(cons(X,S)), lambda:(memberchk(X,S)) & (cut) & (fail)),
			(Term(cons(Var(),S)), lambda:(is_set(S))),
		]

class list_to_set(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		X = Var('X')
		L = Var('L')
		S = Var('S')
		L1 = Var('L1')
		self._exprs = [
			(Term(nil,nil), lambda:true),
			(Term(cons(X,L),cons(X,S)), lambda:(delete(L,X,L1)) & (list_to_set(L1,S))),
		]

class intersection(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		X = Var('X')
		S1 = Var('S1')
		S2 = Var('S2')
		S = Var('S')
		self._exprs = [
			(Term(nil,Var(),nil), lambda:(cut)),
			(Term(cons(X,S1),S2,cons(X,S)), lambda:(memberchk(X,S2)) & (cut) & (intersection(S1,S2,S))),
			(Term(cons(Var(),S1),S2,S), lambda:(intersection(S1,S2,S))),
		]

class subtract(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		X = Var('X')
		S1 = Var('S1')
		S2 = Var('S2')
		S = Var('S')
		self._exprs = [
			(Term(nil,Var(),nil), lambda:(cut)),
			(Term(cons(X,S1),S2,S), lambda:(memberchk(X,S2)) & (cut) & (subtract(S1,S2,S))),
			(Term(cons(X,S1),S2,cons(X,S)), lambda:(subtract(S1,S2,S))),
		]

class union(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		S = Var('S')
		X = Var('X')
		S1 = Var('S1')
		S2 = Var('S2')
		self._exprs = [
			(Term(nil,S,S), lambda:(cut)),
			(Term(cons(X,S1),S2,S), lambda:(memberchk(X,S2)) & (cut) & (union(S1,S2,S))),
			(Term(cons(X,S1),S2,cons(X,S)), lambda:(union(S1,S2,S))),
		]

class subset(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		S = Var('S')
		X = Var('X')
		SS = Var('SS')
		self._exprs = [
			(Term(nil,S), lambda:(cut)),
			(Term(cons(X,SS),S), lambda:(memberchk(X,S)) & (subset(SS,S))),
		]

class merge_set(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2):
		self._form_args = Term(_a_0, _a_1, _a_2)
		S = Var('S')
		X = Var('X')
		S1 = Var('S1')
		Y = Var('Y')
		S2 = Var('S2')
		self._exprs = [
			(Term(nil,S,S), lambda:(cut)),
			(Term(S,nil,S), lambda:(cut)),
			(Term(cons(X,S1),cons(Y,S2),cons(X,S)), lambda:(lt(X,Y)) & (cut) & (merge_set(S1,cons(Y,S2),S))),
			(Term(cons(X,S1),cons(Y,S2),cons(Y,S)), lambda:(gt(X,Y)) & (cut) & (merge_set(cons(X,S1),S2,S))),
			(Term(cons(X,S1),cons(Y,S2),cons(X,S)), lambda:(eq(X,Y)) & (cut) & (merge_set(S1,S2,S))),
		]

# Sorting Lists

class sort(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		L = Var('L')
		S = Var('S')
		self._exprs = [
			(Term(L,S), lambda:(zz_sort(L,S))),
		]

class zz_sort(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		X = Var('X')
		L = Var('L')
		S = Var('S')
		INF = Var('INF')
		SUP = Var('SUP')
		SINF = Var('SINF')
		SSUP = Var('SSUP')
		self._exprs = [
			(Term(nil,nil), lambda:(cut)),
			(Term(cons(X,nil),cons(X,nil)), lambda:(cut)),
			(Term(cons(X,L),S), lambda:(zz_sort_split(X,L,INF,SUP)) & (zz_sort(INF,SINF)) & (zz_sort(SUP,SSUP)) & (append(SINF,cons(X,SSUP),S))),
		]

class zz_sort_split(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2, _a_3):
		self._form_args = Term(_a_0, _a_1, _a_2, _a_3)
		X = Var('X')
		Y = Var('Y')
		L = Var('L')
		INF = Var('INF')
		SUP = Var('SUP')
		self._exprs = [
			(Term(Var(),nil,nil,nil), lambda:(cut)),
			(Term(X,cons(Y,L),INF,cons(Y,SUP)), lambda:(lt(X,Y)) & (cut) & (zz_sort_split(X,L,INF,SUP))),
			(Term(X,cons(Y,L),cons(Y,INF),SUP), lambda:(gt(X,Y)) & (cut) & (zz_sort_split(X,L,INF,SUP))),
			(Term(X,cons(Y,L),INF,SUP), lambda:(eq(X,Y)) & (zz_sort_split(X,L,INF,SUP))),
		]

class msort(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		L = Var('L')
		S = Var('S')
		self._exprs = [
			(Term(L,S), lambda:(zz_msort(L,S))),
		]

class zz_msort(PyLogPredicate):
	def __init__(self, _a_0, _a_1):
		self._form_args = Term(_a_0, _a_1)
		X = Var('X')
		L = Var('L')
		S = Var('S')
		INF = Var('INF')
		SUP = Var('SUP')
		SINF = Var('SINF')
		SSUP = Var('SSUP')
		self._exprs = [
			(Term(nil,nil), lambda:(cut)),
			(Term(cons(X,nil),cons(X,nil)), lambda:(cut)),
			(Term(cons(X,L),S), lambda:(zz_msort_split(X,L,INF,SUP)) & (zz_msort(INF,SINF)) & (zz_msort(SUP,SSUP)) & (append(SINF,cons(X,SSUP),S))),
		]

class zz_msort_split(PyLogPredicate):
	def __init__(self, _a_0, _a_1, _a_2, _a_3):
		self._form_args = Term(_a_0, _a_1, _a_2, _a_3)
		X = Var('X')
		Y = Var('Y')
		L = Var('L')
		INF = Var('INF')
		SUP = Var('SUP')
		self._exprs = [
			(Term(Var(),nil,nil,nil), lambda:(cut)),
			(Term(X,cons(Y,L),INF,cons(Y,SUP)), lambda:(le(X,Y)) & (cut) & (zz_msort_split(X,L,INF,SUP))),
			(Term(X,cons(Y,L),cons(Y,INF),SUP), lambda:(gt(X,Y)) & (cut) & (zz_msort_split(X,L,INF,SUP))),
		]
