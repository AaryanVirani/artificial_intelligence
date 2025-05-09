def read_input(filename: str) -> tuple[str, str, dict[str, int], list[str], list[tuple[str, str]]]:
    """
    Parses the input file, extracting the target value, the vertices and their values, and the edges.

    Args:
        filename (str): The name of the input file
    
    Returns:
        tuple[str, str, dict[str, int], list[str], list[tuple[str, str]]: The target value, the flag, the vertices and their values, the list of vertices, and the list of edges.
    """
    with open(filename, "r") as f:
        lines = f.readlines()
    
    # Ensure that there is no trailing whitespaces
    lines = [line.strip() for line in lines]

    # Read the first line (shows the flag and target)
    target, flag = lines[0].split(" ")[0], lines[0].split(" ")[1]

    # Then read the vertices
    vertices = {}
    vertex_list = []
    i = 1

    # Read until we hit a blank line
    while i < len(lines) and lines[i].strip() != "":
        vertex, value = lines[i].split()
        vertices[vertex] = int(value)
        vertex_list.append(vertex)
        i += 1

    # Skipping the blank line
    i += 1

    # Deal with the edges
    edges = []
    while i < len(lines):
        edge = lines[i].split()
        edges.append((edge[0], edge[1]))
        i += 1
    
    return target, flag, vertices, vertex_list, edges


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


def add_vertex(vertex: str, state: set[str], graph: dict[str, set[str]]) -> bool:
    """
    Adds a vertex to the state if it is a valid move.

    Args:
        vertex (str): The vertex to add
        state (set[str]): The current state
        graph (dict[str, set[str]]): The graph representation
    
    Returns:
        bool: True if the vertex was added, False otherwise
    """
    for v in state:
        if vertex in graph[v]:
            return False
    return True


def depth_search(flag: str, 
                 state: set[str], 
                 curr_depth: int, 
                 depth_lim: int, 
                 target: int, 
                 graph: dict[str, set[str]],
                 vertex_values: dict[str, int],
                 printed: set[tuple[str, ...]] = None) -> tuple[set[str] | None, bool, int]:
    """
    Performs a depth-first search to find a solution.

    Args:
        flag (str): The flag to determine the type of search
        state (set[str]): The current state
        curr_depth (int): The current depth
        depth_lim (int): The depth limit
        target (int): The target value
        graph (dict[str, set[str]]): The graph representation
        vertex_values (dict[str, int]): The values of the vertices
        printed (set[tuple[str, ...]], optional): The set of printed states
    
    Returns:
        tuple[set[str] | None, bool, int]: The solution, a flag indicating whether the search expanded, and the max depth reached
    """
    if printed is None:
        printed = set()

    if curr_depth > 0 and curr_depth < depth_lim and flag == "V": # Prints the first state (even during expansion)
        state_key = tuple(sorted(state))
        if state_key not in printed:
            printed.add(state_key)
            total = sum(vertex_values[v] for v in state)
            sorted_state = sorted(state)
            print(*sorted_state, end = " ")
            print(f"Value: {total}.")


    if curr_depth == depth_lim: # If we reached the depth limit
        if state and flag == "V": # Prints the last state
            total = sum(vertex_values[v] for v in state) # Calculate the total value
            state = sorted(state) 
            print(*state, end = " ")
            print(f"Value: {total}.")
        if state and sum(vertex_values[v] for v in state) >= target: # If the total value is greater than or equal to the target
            return state, True, len(state) # Return the state as the solution
        return None, False, len(state) # Otherwise, return None
    
    expand = False # Flag to indicate whether the search expanded or not
    max_depth = len(state) # Tracking the largest state size reached in a branch (to terminate early)

    for v in sorted(vertex_values.keys()): # Iterate over the vertices
        if state and v <= max(state): # If the vertex is less than or equal to the maximum vertex in the state
            continue
        if v not in state and add_vertex(v, state, graph): # If the vertex is not in the state and it is a valid move
            new_state = state.copy() # Create a new state
            new_state.add(v) # Add the vertex to the new state
            expand = True # Set the flag to True
            solution, child_expanded, child_max_size = depth_search(flag, new_state, curr_depth + 1, depth_lim, target, graph, vertex_values, printed) # Recursively call the function
            max_depth = max(max_depth, child_max_size) # Update the max depth
            if solution is not None: # If a solution is found
                return solution, True, max_depth
            if child_expanded:
                expand = True
    return None, expand, max_depth


def iterative_deepening_search(flag: str, 
                               target: int, 
                               graph: dict[str, set[str]], 
                               vertex_values: dict[str, int]) -> None:
    """
    Performs an iterative deepening search to find a solution.

    Args:
        flag (str): The flag to determine the type of search
        target (int): The target value
        graph (dict[str, set[str]]): The graph representation
        vertex_values (dict[str, int]): The values of the vertices
    """
    depth = 1
    prev_max_depth = 0  # Allows for early termination (to prevent identical searches)
    max_depth = len(vertex_values)
    while depth <= max_depth:
        if flag == "V":
            if depth > 1: # Print a newline to separate the different depths
                print()
            print(f"Depth={depth}.")

        solution, _, current_max_depth = depth_search(flag, set(), 0, depth, target, graph, vertex_values, printed=set()) # Perform a depth search
        if solution is not None: # If a solution is found
            solution = sorted(solution) # Sort the solution
            total = sum(vertex_values[v] for v in solution) # Calculate the total value
            if flag == "V":
                print()
            print(f"Found solution", end=" ") 
            print(*solution, end = " ")
            print(f"Value: {total}")
            return
        
        if current_max_depth <= prev_max_depth: # If the current max depth is less than or equal to the previous max depth
            break # Terminate the search

        prev_max_depth = current_max_depth # Update the previous max depth
        depth += 1

    print("No solution found")


def main():
    target, flag, vertex_values, vertex_list, edges = read_input("input.txt")
    graph = build_graph(vertex_list, edges)
    iterative_deepening_search(flag, int(target), graph, vertex_values)


if __name__ == "__main__":
    main()