import itertools

"""

https://math.stackexchange.com/questions/2244761/translating-sentences-to-propositional-calculus-formulas


I'm trying to solve the following exercise which I found in my text book.

*Dave invites his friends to his wedding and gets the following responses.*

 1. *If Arnold does not come, then Bianca doesn't want to come either.*
 2. *At least one of the siblings Carla and Daniel come*
 3. *Either Arnold or Elisa come, but not both*
 4. *Either Elisa and Daniel come, or both do not come*
 5. *If Carla comes, then Daniel and Bianca also come.*

*Formalize the sentences in propositional calculus and find out who comes to the wedding.*

**My solutions looks as follows.**

Let $X_i$ be a variable with
$i \in \{(A)rnold,(B)ianca,(C)arla,(D)aniel,(E)lisa\}$
and $I(X_i)=1$ iff i comes to the wedding.

 1. $\lnot X_A \to \lnot X_B$
 2. $X_C \lor X_D$
 3. $(\lnot X_A \land X_E) \lor (X_A \land \lnot X_E)$
 4. $X_E \land X_D$
 5. $X_C \to (X_D \land X_B)$

Is this correct? And how do I proceed to find out who comes the wedding? My idea was to find an interpretation I such that $I \vDash (\lnot X_A \to \lnot X_B) \land (X_C \lor X_D) \land ((\lnot X_A \land X_E) \lor (X_A \land \lnot X_E)) \land (X_E \land X_D) \land (X_C \to (X_D \land X_B))$. But I constructed the truth table and found out that the formula is unsatisfiable. What is wrong here?


"""
tf = [True, False]
tfs = 5 * [tf]

def implies(p, q):
    #  p->q  ==  !(p and !q)
    return not( p and (not q) )

for p in itertools.product(*tfs):
    a,b,c,d,e = p

    x1 = implies(not a, not b)
    x2 = c or d
    x3 = ((not a) and e) or (a and (not e))
    x4 = e and d
    x5 = implies(c , d and b)

    res = x1 and x2 and x3 and x4 and x5
    if res:
        print p


