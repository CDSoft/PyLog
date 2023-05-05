# PyLog - Christophe Delord

# Abstract

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

# License

PyLog is available under the GNU Lesser General Public:

> PyLog: A first order logic library in Python
>
> Copyright (C) 2009 Christophe Delord
>
> PyLog is free software: you can redistribute it and/or modify it under
> the terms of the GNU Lesser General Public License as published by the
> Free Software Foundation, either version 3 of the License, or (at your
> option) any later version.
>
> Simple Parser is distributed in the hope that it will be useful, but
> WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
> Lesser General Public License for more details.
>
> You should have received a copy of the GNU Lesser General Public
> License along with Simple Parser. If not, see
> <http://www.gnu.org/licenses/>.

# A first order logic library in Python

PyLog provides a simple way to write logic terms, variables and atoms.
Atoms are special objects that can contain any Python objects. All you
need is to import PyLog:

    >>> from PyLog import *

## Logical objects

PyLog can handle terms, variables and atoms.

## Terms

To instantiate a term, just write it! The functor should be a valid
Python object based on Term (provided by PyLog). For example, to create
the ‘f’ functor :

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

## Logical operations

Once your terms and variables are instantiated PyLog can unify them. To
do this, you have to compute the most general unifier of two terms (or
variables or atoms). If such a unifier exists you can do the
unification. The unification is a new level in the stack. Useful when
backtracking.

<table>
<colgroup>
<col style="width: 41%" />
<col style="width: 58%" />
</colgroup>
<thead>
<tr class="header">
<th>Example</th>
<th>Result of execution</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><div class="sourceCode" id="cb1"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb1-1"><a href="#cb1-1" aria-hidden="true" tabindex="-1"></a><span class="im">from</span> pylog <span class="im">import</span> <span class="op">*</span></span>
<span id="cb1-2"><a href="#cb1-2" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb1-3"><a href="#cb1-3" aria-hidden="true" tabindex="-1"></a><span class="kw">class</span> f(Term): <span class="cf">pass</span></span>
<span id="cb1-4"><a href="#cb1-4" aria-hidden="true" tabindex="-1"></a><span class="kw">class</span> g(Term): <span class="cf">pass</span></span>
<span id="cb1-5"><a href="#cb1-5" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb1-6"><a href="#cb1-6" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;Simple unification&quot;</span></span>
<span id="cb1-7"><a href="#cb1-7" aria-hidden="true" tabindex="-1"></a>X <span class="op">=</span> Var(<span class="st">&#39;X&#39;</span>)</span>
<span id="cb1-8"><a href="#cb1-8" aria-hidden="true" tabindex="-1"></a>Y <span class="op">=</span> Var(<span class="st">&#39;Y&#39;</span>)</span>
<span id="cb1-9"><a href="#cb1-9" aria-hidden="true" tabindex="-1"></a>a <span class="op">=</span> f(X,g(Y,<span class="dv">2</span>))</span>
<span id="cb1-10"><a href="#cb1-10" aria-hidden="true" tabindex="-1"></a>b <span class="op">=</span> f(g(<span class="dv">1</span>,<span class="dv">2</span>),X)</span>
<span id="cb1-11"><a href="#cb1-11" aria-hidden="true" tabindex="-1"></a>s0 <span class="op">=</span> Stack()</span>
<span id="cb1-12"><a href="#cb1-12" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t</span><span class="st">Before unification&quot;</span></span>
<span id="cb1-13"><a href="#cb1-13" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t\t</span><span class="st">a =&quot;</span>, s0(a)</span>
<span id="cb1-14"><a href="#cb1-14" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t\t</span><span class="st">b =&quot;</span>, s0(b)</span>
<span id="cb1-15"><a href="#cb1-15" aria-hidden="true" tabindex="-1"></a>s1 <span class="op">=</span> s0.unify(a, b).<span class="bu">next</span>()</span>
<span id="cb1-16"><a href="#cb1-16" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t</span><span class="st">After unification&quot;</span></span>
<span id="cb1-17"><a href="#cb1-17" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t\t</span><span class="st">a =&quot;</span>, s1(a)</span>
<span id="cb1-18"><a href="#cb1-18" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t\t</span><span class="st">b =&quot;</span>, s1(b)</span>
<span id="cb1-19"><a href="#cb1-19" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb1-20"><a href="#cb1-20" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;Recursive terms&quot;</span></span>
<span id="cb1-21"><a href="#cb1-21" aria-hidden="true" tabindex="-1"></a>A <span class="op">=</span> Var(<span class="st">&#39;A&#39;</span>)</span>
<span id="cb1-22"><a href="#cb1-22" aria-hidden="true" tabindex="-1"></a>a <span class="op">=</span> f(A)</span>
<span id="cb1-23"><a href="#cb1-23" aria-hidden="true" tabindex="-1"></a>s0 <span class="op">=</span> Stack()</span>
<span id="cb1-24"><a href="#cb1-24" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t</span><span class="st">Before unification&quot;</span></span>
<span id="cb1-25"><a href="#cb1-25" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t\t</span><span class="st">A =&quot;</span>, s0(A)</span>
<span id="cb1-26"><a href="#cb1-26" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t\t</span><span class="st">a =&quot;</span>, s0(a)</span>
<span id="cb1-27"><a href="#cb1-27" aria-hidden="true" tabindex="-1"></a>s1 <span class="op">=</span> s0.unify(a, A).<span class="bu">next</span>()</span>
<span id="cb1-28"><a href="#cb1-28" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t</span><span class="st">After unification&quot;</span></span>
<span id="cb1-29"><a href="#cb1-29" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t\t</span><span class="st">A =&quot;</span>, s1(A)</span>
<span id="cb1-30"><a href="#cb1-30" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span> <span class="st">&quot;</span><span class="ch">\t\t</span><span class="st">a =&quot;</span>, s1(a)</span></code></pre></div></td>
<td><pre><code>
Simple unification
    Before unification
        a = f(X,g(Y,2))
        b = f(g(1,2),X)
    After unification
        a = f(g(1,2),g(1,2))
        b = f(g(1,2),g(1,2))
Recursive terms
    Before unification
        A = A
        a = f(A)
    After unification
        A = f(f(f(f(f(f(f(f(f(f(f(...)))))))))))
        a = f(f(f(f(f(f(f(f(f(f(f(...)))))))))))
</code></pre></td>
</tr>
</tbody>
</table>

# PROLOG

PyLog provides a simple PROLOG engine. It will translate a PROLOG
program into Python. This engine uses the new generator ability of
Python 2.4.

PROLOG predicates are Python generators yielding 1 when they succeed. As
a side effect they instantiate variables. So the yielded value doesn’t
matter. For example, to print all the members of a list:

    X = Var()
    l = cons(1,cons(2,nil))
    for _ in member(X,l)():
        print X

For a complete example, read [pylogsrc.py](pylogsrc.html).

# Download

- [PyLog](src/pylog.py)

# Links

- [Python](http://www.python.org/)
- [SWI-Prolog](http://www.swi-prolog.org/)
- [Python-Logic at Logilab](http://www.logilab.org/python-logic/)
