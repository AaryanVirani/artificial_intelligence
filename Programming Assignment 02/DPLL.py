# Implementation of basic DPLL algorithm
# atoms are integers 1...N
# literals are either positive or negative atom
# a clause is a set of literals

# The set of clauses is implemented as a list, because Python does not support sets of sets.
# The bindings is implemented as an array of size nAtoms (the number of atoms) where
# bindings[i] == 1 if atom i is bound to True
#               -1 if atom i is bound to False
#                0 if atom i is unbound

import numpy as np  # only used in creating random examples
global nAtoms  # number of propositional atoms + 1 (because Python uses zero-based indexing)
global debug   # Boolean flag for printing trace information
global strategy # Boolean flag to choose strategy in choosing atom to split on.
                # True for "clever" strategy, False for just choosing first unbound atom

strategy = True
debug = False

# superroutine: initializes bindings then calls the recursive DPLL.
def DPLLTop(clauses):
    global nAtoms
    nAtoms = 0
    for c in clauses:
        for lit in c:
            nAtoms = max(nAtoms,abs(lit))
    nAtoms += 1       # because Python uses 0-based indexing
    found, bindings = DPLL(clauses,[0]*nAtoms,0)
    return found, bindings

# Recursive call to DPLL
# depth is the depth of recursion. This is just there as defensive programming, in case some
# bug would otherwise give rise to an infinite depth recursion

def DPLL(clauses, bindings,depth):
    global nAtoms
    if depth > nAtoms:                    # Just to be on the safe side
        print("Recursion is too deep. Something is wrong")
        return
    easy = True
    while easy:
        if len(clauses) == 0:            # clauses is the empty set
            if debug:
                print("\nSuccess! ",bindings)
            return True, bindings
        if set() in clauses:              # the empty clause has been derived
            if debug:
                print("\nFailure. Backtracking")
            return False, bindings      
        easy, clauses, bindings = SingletonClause(clauses,bindings)
        if not easy:
            easy, clauses, bindings = PureLiteral(clauses,bindings)
    if strategy:
        p,sign = ChooseUnbound(clauses)
    else:
        p = 1+bindings[1:].index(0) # first unbound atom
        sign = 1
    clausesSaved, bindingsSaved = CopyClauses(clauses,bindings)
    if debug:
        print("\nNo easy cases. Splitting on ", p, ". Sign = ", sign)
    clauses, bindings = Propagate(clauses,bindings,p,sign)
    if debug:
        print("\n\nNew set:")
        for c in clauses:
             print(c)
        print("\n")
    success, bindings = DPLL(clauses,bindings,depth+1)
    if success:
        return True, bindings
    clauses, bindings = Propagate(clausesSaved,bindingsSaved,p,-sign)
    return DPLL(clauses,bindings,depth+1)

# find a singleton clause and propagate the corresponding assignment
def SingletonClause(clauses,bindings):    
    global debug
    for clause in clauses:
        if len(clause) == 1:
            lit, = clause
            p = abs(lit)
            sign = lit//p
            if debug:
               print("Singleton Clause", clause)
            clauses, bindings = Propagate(clauses,bindings,p,sign)
            return True, clauses, bindings
    return False, clauses, bindings

# find a pure literal, and propagate the corresponding assignment
def PureLiteral(clauses,bindings):
    global nAtoms
    signs = [set() for i in range(nAtoms)]
    for c in clauses:
        for lit in c:
            i = abs(lit)
            s = lit//i
            signs[i].add(s)
    for i in range(1,nAtoms):
        if len(signs[i]) == 1:   
            s, = signs[i]     
            if debug:
                print("Pure Literal", s*i)
            clauses, bindings = Propagate(clauses,bindings,i,s)
            return True, clauses, bindings
    return False, clauses, bindings


# make a deep copy of the clauses and the bindings, 
# so that destructive changes to one copy don't affect the other.

def CopyClauses(clauses,bindings):
    newClauses = []
    for c in clauses:
        newClauses += [c.copy()]
    return newClauses, bindings.copy()

# When there are no easy cases, and DPLL reaches a choice point,
# ChooseUnbound(clauses) implements a heuristic for choosing the atom
# to split on and the first sign to try with it, as follows:
# 1) Let maxL be the length of the shortest clause in clauses. 
#    E.g. if clauses contains clauses of length 2, 3, and 4, then maxL = 2.
# 2) Find the literal lit that occurs most often in clauses of length maxL 
#     (which have been collected in the list longestClauses).
#    E.g. if maxL = 2, and literal 2 occurs in 3 clauses of length 2, 
#          literal -3 occurs in 5, and literal -4 occurs in 1
#    then lit = -3
#    Return the atom and sign of lit, in this case 3 and -1
#    Note that if atom p occurs with sign s in k different clauses and maxL=2
#    then setting p to be s creates k different singleton clauses, which are all
#    easy cases. 
def ChooseUnbound(clauses):
    global nAtoms
    maxL = 0
    for c in clauses:
        if len(c) > maxL:
            maxL = len(c)
            longestClauses = [c]
        elif len(c) == maxL:
            longestClauses += [c]
    litCount = [0]*(2*nAtoms+1)
    max = 0
    for c in longestClauses:
        for lit in c:
            i = lit
            if i < 0:
                i = nAtoms-lit
            litCount[i] += 1
            if litCount[i] > max:
                imax = i
                max = litCount[i]
    if imax < nAtoms:
        return imax, 1
    else: 
        return imax-nAtoms, -1
        
# Assign the sign s to atom i in bindings, and propagate the effect to
# clauses. That is, delete any clause that contains s*i 
# and delete literal -s*i from any clause that contains it.

def Propagate(clauses,bindings,i,s):
    global debug
    if debug:
        print("Propagating atom", i, "sign", s)
    bindings[i]=s
    newClauses = clauses.copy()  # Note that this is a top level copy.
    for c in clauses:
        if s*i in c:
            newClauses.remove(c)
            if debug:
                print("Deleting clause", c)
        elif -s*i in c:
            if debug:
                print("Deleting literal ", -s*i, "from", c)
            c.remove(-s*i)
    return newClauses, bindings
     
        
# A few simple test examples

def test1():
    global debug
    debug = True
    clauses = [{1},{-1,2},{-1,-2,3}]
    return DPLLTop(clauses)

def test2():
    global debug
    debug = True
    clauses = [{1,2},{1,-2,-3},{2,3}]
    return DPLLTop(clauses)

def test3():
    global debug
    debug = True
    clauses = [{1, 2, 3}, {1, -2, -3}, {1, -4}, {-2, -3, -4}, {-1, -2, 3},
               {5, 6}, {5, -6}, {2, -5},{-3, -5}]
    return DPLLTop(clauses) 

def test4():
    global debug
    debug = True
    clauses = [{1,2},{1,-2},{-1,2},{-1,-2}]
    return DPLLTop(clauses) 

# Randomly generate a set of nClauses clauses all of length 3 with nAtoms different atoms
# seed is a seed for the random number generate. -1 if you don't want to set the seed.
# trace is a Boolean flag for verbose output.

def testRandom3SAT(nAtoms,nClauses,seed,trace):
   global debug
   if seed >= 0:
       np.random.seed(seed) 
   debug = trace
   clauses = []
   saveClauses = []
   for i in range(nClauses):
       atoms = np.random.choice(range(1,nAtoms+1),size=3,replace=False)
       signs = np.random.choice([1,-1],size=3,replace=True)
       clauses += [{int(atoms[0]*signs[0]), int(atoms[1]*signs[1]), int(atoms[2]*signs[2])}]
       saveClauses += [{int(atoms[0]*signs[0]), int(atoms[1]*signs[1]), int(atoms[2]*signs[2])}]
   if debug:
       print("Initial clauses:")
       for c in clauses:
           print(c)
       print("\n")       
   found, bindings = DPLLTop(clauses)
   if found:
       CheckAnswer(saveClauses,bindings)
   return found, bindings

def CheckAnswer(clauses,bindings):
    for c in clauses:
        ok = False
        for lit in c:
            if bindings[abs(lit)]*lit > 0:
                ok = True
        if not(ok):
            print("Wrong answer obtained!")
            print(clauses)
            print(bindings)
            return False
    return True  

# Try it with RandomTests(60,[230,240,260,280,300],100)

def RandomTests(nAtoms,clausesLengths,nTries):
    nlens = len(clausesLengths)
    counts = [0]*len(clausesLengths)
    for i in range(nlens):
        for j in range(nTries):
            found, bindings = testRandom3SAT(nAtoms, clausesLengths[i],-1,False)
            if found:
                counts[i] += 1
        print("With", nAtoms, "atoms and", clausesLengths[i], "clauses,", 
               "the fraction satisfiable is", counts[i]/nTries)
    return counts 