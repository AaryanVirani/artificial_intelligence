from DPLL import DPLLTop

def parseInputFile(filename):
    with open(filename, "r") as f:  
        lines = [line.strip() for line in f if line.strip() != ""]

    # Parse the first line
    tokens = lines[0].split()
    N = int(tokens[0])
    # Getting empty vertices is redundant, as the unit clauses give an idea of the empty vertices
    Z = int(tokens[2])

    # parse the second line
    startList = lines[1].split()

    # parse the third line
    endList = lines[2].split()
    startState = {i + 1: startList[i] for i in range(N)}
    endState = {i + 1: endList[i] for i in range(N)}

    # Parse the edges in remaining lines
    edges = []
    for line in lines[3:]:
        u, v = line.split()
        edges.append((int(u), int(v)))
    
    return N, Z, startState, endState, edges

inDict = {}
emptyDict = {}
moveDict = {}
clauses = []
nextMove = 1

def addClause(*lits): # Converts a set of literals into a clause and appends it to a list
    global clauses
    clauses.append(set(lits))


def getEmptyVar(vertex, time): # Returns an identifier for the empty variable of a vertex at a given time
    global nextMove
    if (vertex, time) not in emptyDict:
        emptyDict[(vertex, time)] = nextMove
        nextMove += 1
    return emptyDict[(vertex, time)]


def getMoveVar(u, v, time): # Returns an identifier for the move variable of a piece from U to V at a given time
    global nextMove
    if (u, v, time) not in moveDict:
        moveDict[(u, v, time)] = nextMove
        nextMove += 1
    return moveDict[(u, v, time)]


def getInVar(u, v, time): # Returns an identifier for the variable of a piece in a vertex at a given time
    global nextMove
    if (u, v, time) not in inDict:
        inDict[(u, v, time)] = nextMove
        nextMove += 1
    return inDict[(u, v, time)]    


def getNeighbors(N, edges): # Checks the neighbors of each verte to determine if a move occurs/ed
    neighbors = {vertex: set() for vertex in range(1, N + 1)}
    for (u, v) in edges:
        neighbors[u].add(v)
        neighbors[v].add(u)
    return neighbors


def state_coherence(N, pieces, Z):
    # I. Definition of Empty
    for time in range(Z+1):
        for vertex in range(1, N+1):
            emptyVar = getEmptyVar(vertex, time) # Get the empty variable for vertex at time
            pieceVars = []
            for piece in pieces:
                inVar = getInVar(piece, vertex, time)
                addClause(-emptyVar, -inVar) # Making sure that if a vertex is empty, no piece is in it e.g. ¬Empty(5,3) V ¬In(A,5,3).
                pieceVars.append(inVar)
            addClause(emptyVar, *pieceVars) # e.g. Empty(5,3) V In(A,5,3) V In(B,5,3) V etc.
    
    # II. No two pieces can share the same vertex (at time 0 and at time Z)
    for vertex in range(1, N+1):
        for i in range(len(pieces)):
            for j in range(i+1, len(pieces)):
                addClause(-getInVar(pieces[i], vertex, 0), -getInVar(pieces[j], vertex, 0)) # At time 0, make sure no two pieces share the same vertex
                addClause(-getInVar(pieces[i], vertex, Z), -getInVar(pieces[j], vertex, Z)) # At time Z, make sure no two pieces share the same vertex


def precondition(Z, edges):
    # III. Ensure that at time T, if a move from U to V occurs, then U is not empty at time T and V is empty 
    for time in range(Z):
        for (u, v) in edges:
            moveVar = getMoveVar(u, v, time)
            addClause(-moveVar, -getEmptyVar(u, time)) # e.g. ¬Move(U,V,T) ∧ Empty(U,T)
            addClause(-moveVar, getEmptyVar(v, time)) # e.g. ¬Move(U,V,T) ∧ Empty(V,T)
            moveVar2 = getMoveVar(v, u, time) # Consider the reverse move
            addClause(-moveVar2, -getEmptyVar(v, time)) # e.g. ¬Move(V,U,T) ∧ Empty(V,T)
            addClause(-moveVar2, getEmptyVar(u, time)) # e.g. ¬Move(V,U,T) ∧ Empty(U,T)


def causal(Z, edges, pieces):
    # IV. If a move from U to V occurs at time T, then at time T+1, the piece that was at U is now at V
    for time in range(Z):
        for (u, v) in edges:
            moveVar = getMoveVar(u, v, time)
            for piece in pieces:
                addClause(-getInVar(piece, u, time), -moveVar, getInVar(piece, v, time+1)) # -In(P,U,T) ∧ -Move(U,V,T) ∧ In(P,V,T+1)
            moveVar2 = getMoveVar(v, u, time) # Consider the reverse move
            for piece in pieces:
                addClause(-getInVar(piece, v, time), -moveVar2, getInVar(piece, u, time+1))
                   
    # V. If a move from U to V occurs at time T, then at time T+1, U is empty and V is not empty
    for time in range(Z):
        for (u, v) in edges:
            moveVar = getMoveVar(u, v, time)
            addClause(-moveVar, getEmptyVar(u, time+1)) # - Move(U,V,T) V Empty(U,T+1)
            moveVar2 = getMoveVar(v, u, time) # Consider the reverse move
            addClause(-moveVar2, getEmptyVar(v, time+1)) # - Move(V,U,T) V Empty(V,T+1)
    

def frame(N, Z, edges, pieces):
    neighbors = getNeighbors(N, edges) # Get the neighbors of each vertex

    # VI. If a vertex is empty at time T, but not at time T+1, then there must be a move from one of its neighbors to it
    for time in range(Z):
        for vertex in range(1, N+1):
            lits = [-getEmptyVar(vertex, time), getEmptyVar(vertex, time+1)]
            for neighbor in neighbors[vertex]:
                lits.append(getMoveVar(neighbor, vertex, time)) # e.g. -Empty(V,T) V Empty(V,T+1) V Move(U,V,T) V Move(W,V,T) etc.
            addClause(*lits)

    # VII. If a vertex is not empty at time T, but empty at time T+1, then there must be a move from it to one of its neighbors
        for vertex in range(1, N+1):
            lits = [getEmptyVar(vertex, time), -getEmptyVar(vertex, time+1)]
            for neighbor in neighbors[vertex]:
                lits.append(getMoveVar(vertex, neighbor, time)) # e.g. Empty(V,T) V -Empty(V,T+1) V Move(V,U,T) V Move(V,W,T) etc.
            addClause(*lits)

    # VIII. If a piece is at vertex V at time T, then at time T + 1, either the piece is still at V or V is empty
    for time in range(Z):
        for vertex in range(1, N+1):
            for piece in pieces:
                addClause(-getInVar(piece, vertex, time), getInVar(piece, vertex, time+1), getEmptyVar(vertex, time+1)) # e.g. -In(P,V,T) ∧ In(P,V,T+1) ∧ Empty(V,T+1)


def single_move(edges, Z):
    # IX. For any two distinct edges, and any time T between 0 and Z-1, at most one of the two edges can be moved
    for time in range(Z):
        possibleMoves = []
        for (u, v) in edges:
            possibleMoves.append(getMoveVar(u, v, time)) # e.g. Move(U,V,T)
            possibleMoves.append(getMoveVar(v, u, time)) # e.g. Move(V,U,T)
        for i in range(len(possibleMoves)):
            for j in range(i+1, len(possibleMoves)):
                addClause(-possibleMoves[i], -possibleMoves[j]) # e.g. ¬Move(U,V,T) ∧ ¬Move(W, X, T)


def start_state(N, startState):
    # X. For each vertex, specify the piece in the vertex at time 0 or specify that the vertex is empty
    for vertex in range(1, N+1):
        if startState[vertex] == "Empty":
            addClause(getEmptyVar(vertex, 0)) # e.g. Empty(V,0)
        else:
            addClause(getInVar(startState[vertex], vertex, 0)) # e.g. In(P,V,0)


def end_state(N, endState, Z):
    # XI. For each vertex, specify the piece in the vertex at time Z or specify that the vertex is empty
    for vertex in range(1, N+1):
        if endState[vertex] == "Empty":
            addClause(getEmptyVar(vertex, Z)) # e.g. Empty(V,Z)
        else:
            addClause(getInVar(endState[vertex], vertex, Z)) # e.g. In(P,V,Z)


def convert_identifiers(lit):
    # Reverse the mappings of the global dictionaries
    emptyDict_rev = {v: key for key, v in emptyDict.items()}
    inDict_rev = {v: key for key, v in inDict.items()}
    moveDict_rev = {v: key for key, v in moveDict.items()}
    if lit < 0:
        atomID = -lit
        prefix = "~"
    else:
        atomID = lit
        prefix = ""
    if atomID in emptyDict_rev:
        vertex, time = emptyDict_rev[atomID]
        return f"{prefix}Empty({vertex},{time})"
    elif atomID in inDict_rev:
        piece, vertex, time = inDict_rev[atomID]
        return f"{prefix}In({piece},{vertex},{time})"
    elif atomID in moveDict_rev:
        u, v, time = moveDict_rev[atomID]
        return f"{prefix}Move({u},{v},{time})"
    else:
        return f"{prefix}Unknown({atomID})"
    

def interpretSolution(bindings, Z, edges): # Returns a sorted list of moves that form the solution
    plan = []
    for t in range(Z):
        for (u, v) in edges:
            if bindings[getMoveVar(u, v, t)] == 1: # Checks the move in one direction, checking if a move occured (1) or not (0)
                plan.append((t, u, v))  # Print time as t+1
            if bindings[getMoveVar(v, u, t)] == 1: # Checks the move in the reverse direction
                plan.append((t, v, u))
    plan.sort(key=lambda x: x[0])
    return plan


def main():
    filename = "input.txt"
    frontend = "frontend.txt"
    backend = "backend.txt"
    N, Z, startState, endState, edges = parseInputFile(filename)
    
    pieces = set()
    for v in range(1, N+1): # Collects all the pieces in the puzzle, both in the start and end states
        if startState[v] != "Empty":
            pieces.add(startState[v])
        if endState[v] != "Empty":
            pieces.add(endState[v])

    pieces = list(pieces)

    # Build the axioms
    state_coherence(N, pieces, Z)
    precondition(Z, edges)
    causal(Z, edges, pieces)
    frame(N, Z, edges, pieces)
    single_move(edges, Z)
    start_state(N, startState)
    end_state(N, endState, Z)

    # Print the front end to the file
    with open(frontend, "w") as f:
        f.write("Output from front end:\n")
        for clause in clauses:
            clause_str = " V ".join(convert_identifiers(lit) for lit in clause)
            f.write(f"{clause_str}\n")

    # Run DPLL
    success, bindings = DPLLTop(clauses)  
    if success:
        plan = interpretSolution(bindings, Z, edges)
        if plan:
           with open(backend, "w") as f:
                f.write("Output from back end:\n")
                for move in plan:
                    f.write(f"Move({move[1]},{move[2]},{move[0]}) ")
    else:
        f.write("Output from back end:\n")
        f.write("No solution found.\n")

if __name__ == "__main__":
    main()