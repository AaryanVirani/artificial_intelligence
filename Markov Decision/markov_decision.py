import random

def parseInputFile(filename):
    with open(filename, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # First line to get six parameters
    params = lines[0].split()
    non_terminal_states = int(params[0])
    terminal_states = int(params[1])
    num_actions = int(params[2])
    rounds = int(params[3])
    frequency = int(params[4])
    M = int(params[5])

    # Second line for terminal-state rewards
    tokens = lines[1].split()
    rewards = {}
    for i in range(0, len(tokens), 2):
        state = int(tokens[i])
        reward = float(tokens[i + 1])
        rewards[state] = reward
    
    # Third line for cost of each action
    tokens = lines[2].split()
    action_costs = [0.0] * num_actions
    for i in range(0, len(tokens), 2):
        action = int(tokens[i])
        cost = float(tokens[i + 1])
        action_costs[action] = cost
    
    # Remaining lines for transition probabilities
    transitions = {}
    for line in lines[3:]:
        parts = line.split()
        if ":" not in parts[0]:
            continue
        state_string, action_string = parts[0].split(":")
        state = int(state_string)
        action = int(action_string)
        if state not in transitions:
            transitions[state] = {}
        results = []
        # Do for the remaining tokens
        for i in range(1, len(parts), 2):
            next_state = int(parts[i])
            prob = float(parts[i + 1])
            results.append((next_state, prob))
        transitions[state][action] = results

    return non_terminal_states, terminal_states, num_actions, rounds, frequency, M, rewards, action_costs, transitions


def chooseAction(s, count, total, num_actions, M, rewards): # M being the hyperparameter 
    for u in range(num_actions):
        if count[s][u] == 0:
            return u # choose an untried action arbitrarily
    
    avg = [total[s][a]/count[s][a] for a in range(num_actions)] # average reward
    bottom = min(min(avg), min(rewards.values()))
    top = max(rewards.values())

    if bottom == top: # avoiding divison by zero (set scaled avg to 1):
        savg = [1.0] * num_actions 
    else:
        savg = [0.25 + 0.75 * ((avg[i] - bottom)/(top - bottom)) for i in range(num_actions)] # average scaled to range [0.25, 1.0]
    
    c = sum(count[s][i] for i in range(num_actions)) 
    up = [savg[i] ** (c/M) for i in range(num_actions)] # unnormalized probabilities
    norm = sum(up)
    p = [i / norm for i in up]
    return random.choices(range(num_actions), weights=p)[0]


def printStatus(num_rounds, non_term_states, num_actions, count, total, output_file):
    print(f"After {num_rounds} rounds", file=output_file)
    print("Count:", file=output_file)
    for state in range(non_term_states):
        line = ""
        for action in range(num_actions):
            line += f"[{state},{action}]={count[state][action]}. "
        print(line, file=output_file)
    print("Total:", file=output_file)
    for state in range(non_term_states):
        line = ""
        for action in range(num_actions):
            line += f"[{state},{action}]={total[state][action]:.2f}. "
        print(line, file=output_file)
    best_action = []
    for state in range(non_term_states):
        if any(count[state][action] == 0 for action in range(num_actions)):
            best_action.append(f"{state}:U")
        else:
            best_action.append(f"{state}:{max(range(num_actions), key=lambda a: total[state][a]/count[state][a])}")
    print("Best action: ", " ".join(best_action), file=output_file)
    print(file=output_file)


def main():
    # Parse the input file
    filename = "input.txt"

    (non_terminal_states, terminal_states, num_actions, rounds, frequency, M, 
     rewards, action_costs, transitions) = parseInputFile(filename)

    count = [[0 for _ in range(num_actions)] for _ in range(non_terminal_states)]
    total = [[0.0 for _ in range(num_actions)] for _ in range(non_terminal_states)]

    with open("output.txt", "w") as output_file:
        for round_num in range(rounds):
            curr_state = random.randint(0, non_terminal_states - 1)
            cost = 0.0
            encountered = {}
            while curr_state < non_terminal_states: # while in a non-terminal state
                action = chooseAction(curr_state, count, total, num_actions, M, rewards)
                encountered[(curr_state, action)] = True
                cost += action_costs[action]
                if curr_state not in transitions or action not in transitions[curr_state]:
                    next_state = curr_state
                else:
                    results = transitions[curr_state][action]
                    next_state = random.choices([next_s for next_s, p in results], weights=[p for next_s, p in results])[0]
                curr_state = next_state
            reward = rewards.get(curr_state, 0.0)
            net_reward = reward - cost
            for (state, action) in encountered.keys():
                count[state][action] += 1
                total[state][action] += net_reward
            
            if frequency != 0 and (round_num + 1) % frequency == 0: # If freq param is nonzero, print output
                printStatus(round_num + 1, non_terminal_states, num_actions, count, total, output_file)
            
        # Print final output
        if frequency == 0 or rounds % frequency != 0:
            printStatus(rounds, non_terminal_states, num_actions, count, total, output_file)


if __name__ == "__main__":
    main()
