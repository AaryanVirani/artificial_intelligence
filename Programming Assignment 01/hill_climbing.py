import random

def read_input(filename: str) -> tuple[str, str, dict[str, int], list[str], list[tuple[str, str]]]:
    """
    Parses the input file, extracting the target value, the vertices and their values, and the edges.

    Args:
        filename (str): The name of the input file
    
    Returns:
        tuple[str, str, dict[str, int], list[str], list[tuple[str, str]]: The target value, the flag, the vertices and their values, the list of vertices, and the list of edges.
    """
    with open(filename, "r") as f:
        lines = [line.strip() for line in f.readlines()]   
    
    target, flag, random_num = lines[0].split(" ")
    vertices = {}
    vertex_list = []
    i = 1

    while i < len(lines) and lines[i].strip() != "":
        vertex, value = lines[i].split()
        vertices[vertex] = int(value)
        vertex_list.append(vertex)
        i += 1

    i += 1 # skip the blank line

    edges = []
    while i < len(lines):
        edge = lines[i].split()
        edges.append((edge[0], edge[1]))
        i += 1
    
    return target, flag, random_num, vertices, vertex_list, edges


def build_graph(vertex_list: list, 
                edges: list[tuple[str, str]]) -> dict[str, set[str]]:
    """
    Builds a graph from the list of vertices and edges.

    Args:
        vertex_list (list[str]): The list of vertices
        edges (list[tuple[str, str]]): The list of edges
    
    Returns:
        dict[str, set[str]]: The graph representation
    """
    graph = {v: set() for v in vertex_list}
    for edge in edges:
        graph[edge[0]].add(edge[1])
        graph[edge[1]].add(edge[0])
    
    return graph


def random_start_state(vertex_list: list[str]) -> set:
    """
    Generates a random start state.

    Args:
        vertex_list (list[str]): The list of vertices
        graph (dict[str, set[str]]): The graph representation
    
    Returns:
        set: The random start state
    """
    state = set()
    for vertex in vertex_list:
        if random.choice([True, False]): # Randomly add the vertex (0.5) probability
            state.add(vertex)
    return state


def evaluate_state(state: set[str],
                   vertices: dict[str, int]) -> int:
    """
    Evaluates the current state.

    Args:
        state (set[str]): The current state
        vertices (dict[str, int]): The vertices and their values
    
    Returns:
        int: The value of the state
    """
    return sum([vertices[vertex] for vertex in state]) # Getting the sum of the values of the vertices in the state


def is_valid_state(state: set[str],
                   graph: dict[str, set[str]]) -> bool:
    """
    Checks if the current state is valid.

    Args:
        state (set[str]): The current state
        graph (dict[str, set[str]]): The graph representation
    
    Returns:
        bool: True if the state is valid, False otherwise
    """
    for vertex in state:
        for neighbor in graph[vertex]:
            if neighbor in state:
                return False
    return True


def count_edge_penalty(state: set[str],
                       graph: dict[str, set[str]],
                       vertex_values: dict[str, int]) -> int:
    """
    Returns the sum of the costs of all edges in the state (where each edge is only counted once [using Q5])

    Args:
        state (set[str]): The current state
        graph (dict[str, set[str]]): The graph representation
        vertex_values (dict[str, int]): The values of the vertices
    
    Returns:
        int: The sum of the costs of all edges in the state
    """
    penalty = 0
    state_list = list(state)   
    for i in range(len(state_list)):
        for j in range(i+1, len(state_list)):
            u = state_list[i]
            v = state_list[j]
            if v in graph[u]:
                penalty += min(vertex_values[u], vertex_values[v]) # Getting the lower end of the edge
    return penalty


def calculate_error(state: set,
                    vertex_values: dict[str, int],
                    target: int, 
                    graph: dict[str, set[str]]) -> int:
    """
    Calculates the error of the current state.

    Args:
        state (set): The current state
        vertex_values (dict[str, int]): The values of the vertices
        target (int): The target value
        graph (dict[str, set[str]]): The graph representation
    
    Returns:
        int: The error of the state
    """
    cost = evaluate_state(state, vertex_values) # Getting the value of the state
    shortfall = max(0, target - cost) # Getting the shortfall
    edge_penalty = count_edge_penalty(state, graph, vertex_values)
    return shortfall + edge_penalty


def get_neighbors(state: set[str],
                  vertex_list: list[str],
                  graph: dict[str, set[str]], 
                  vertex_values: dict,
                  target: int) -> list[set[str]]:
    """
    Generates the neighbors of the current state.

    Args:
        state (set[str]): The current state
        vertex_list (list[str]): The list of vertices
        graph (dict[str, set[str]]): The graph representation
        vertex_values (dict[str, int]): The values of the vertices
        target (int): The target value
    
    Returns:
        list[set[str]]: The list of neighbors
    """
    neighbors = [] # List to store the neighbors
    for v in state:
        neighbor = state.copy()
        neighbor.remove(v)
        cost = evaluate_state(neighbor, vertex_values)
        error = calculate_error(neighbor, vertex_values, target, graph)
        neighbors.append((neighbor, cost, error))
    
    for v in vertex_list: # Adding a vertex to the state
        if v not in state: # Ensuring that the vertex is not already in the state
            neighbor = state.copy()
            neighbor.add(v)
            cost = evaluate_state(neighbor, vertex_values)
            error = calculate_error(neighbor, vertex_values, target, graph)
            neighbors.append((neighbor, cost, error))
    
    return neighbors


def hill_climbing(target: int,
                  vertex_values: dict[str, int],
                  vertex_list: list[str],
                  graph: dict[str, set[str]],
                  verbose: bool=False,
                  start_state: set=None) -> tuple[set, bool]:
    """
    Performs the hill climbing algorithm to find a solution.

    Args:
        target (int): The target value
        vertex_values (dict[str, int]): The values of the vertices
        vertex_list (list[str]): The list of vertices
        graph (dict[str, set[str]]): The graph representation
        verbose (bool): True to print the state at each iteration
        start_state (set): The starting state
    
    Returns:
        set: The solution state
    """
    if start_state is None: # Randomly choosing a start state
        start_state = random_start_state(vertex_list)

    if verbose:
        states = sorted(start_state)
        print(f"Randomly chosen start state: ", end="")
        print(*states if states else ["{}"], sep=" ", end=".\n")
    
    current_state = start_state # Setting the current state to the start state
    current_cost = evaluate_state(current_state, vertex_values) # Getting the value of the current state
    current_error = calculate_error(current_state, vertex_values, target, graph) # Getting the error of the current state

    if verbose:
        current_state_space = ' '.join(sorted(current_state)) if current_state else "{}" # Getting the state space
        print(f"{current_state_space} Value = {current_cost}. Error = {current_error}.")

    if current_error == 0: # If the randomly chosen state is already the goal state
        return current_state, True

    while True:
        neighbors = get_neighbors(current_state, vertex_list, graph, vertex_values, target) # Getting the neighbors of the current state
        if verbose:
            print("Neighbors:")
            for neighbor, neighbor_cost, neighbor_error in neighbors: # Printing the neighbors
                state_space = " ".join(sorted(neighbor)) if neighbor else "{}"
                print(f"{state_space} Value = {neighbor_cost}. Error = {neighbor_error}.")
                if neighbor_error == 0:
                    return neighbor, True
            
            print() 
        # Find the neighbor with the smallest error
        best_neighbor = None
        best_cost = None
        best_error = float("inf") # To ensure comparison with neighbors
        for neighbor, neighbor_cost, neighbor_error in neighbors: # Finding the best neighbor
            if neighbor_error < best_error:
                best_neighbor = neighbor
                best_cost = neighbor_cost
                best_error = neighbor_error

        if best_neighbor is None or best_error >= current_error: # If the best neighbor is not found or the error is not minimized
            if verbose: 
                print("Search failed\n")
            return current_state, False

        if verbose:
            state_space = " ".join(sorted(best_neighbor)) if best_neighbor else "{}"
            print(f"Move to {state_space} Value = {best_cost}. Error = {best_error}.")

        current_state = best_neighbor 
        current_cost = best_cost
        current_error = best_error

        if current_error == 0:
            return current_state, True
            

def hill_climbing_random_restarts(vertex_list: list,
                                  graph: dict,
                                  vertex_values: dict,
                                  target: int,
                                  num_restarts: int,
                                  verbose: bool=False) -> set:
    """
    Performs the hill climbing algorithm with random restarts, until a solution is found or the number of restarts is reached.

    Args:
        vertex_list (list): The list of vertices
        graph (dict): The graph representation
        vertex_values (dict): The values of the vertices
        target (int): The target value
        num_restarts (int): The number of restarts
        verbose (bool): True to print the state at each iteration
    
    Returns:
        set: The solution state
    """
    for i in range(num_restarts): # Performing the hill climbing algorithm within the number of restarts
        state, found = hill_climbing(target, vertex_values, vertex_list, graph, verbose)
        if found:
            return state
    print("No solution found.")
    return None


def main():
    target, flag, random_num, vertex_values, vertex_list, edges = read_input("input.txt")
    graph = build_graph(vertex_list, edges)
    verbose = (flag.upper() == "V")
    num_restarts = int(random_num)
    solution = hill_climbing_random_restarts(vertex_list, graph, vertex_values, int(target), num_restarts, verbose)
    if solution:
        sol = " ".join(sorted(solution))
        if verbose:
            print()
        print(f"Found solution {sol} Value = {evaluate_state(solution, vertex_values)}")


if __name__ == "__main__":
    main()