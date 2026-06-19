import sys
#from datetime import datetime
from collections import deque
from queue import PriorityQueue
import heapq
import itertools
import datetime 
from datetime import datetime
from copy import deepcopy
import time

# Load start state from file
def load_puzzle(file_path):
    #with open(file_path, 'r') as file:
        #return [list(map(int, line.split())) for line in file]
    puzzle = []
    with open(file_path, 'r') as file:
         for line in file:
            if line.strip() == "END OF FILE":
                break
            row = list(map(int, line.split()))
            #puzzle.append([int(x) for x in line.split()])
            puzzle.append(row)
    return puzzle

# Get neighbors function for BFS Algorithm
def get_neighbors(state):
    neighbors = []
    zero_index = state.index(0)
    row, col = divmod(zero_index, 3)

    # Directions for moving the empty space (row_offset, col_offset)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for direction in directions:
        new_row, new_col = row + direction[0], col + direction[1]

        if 0 <= new_row < 3 and 0 <= new_col < 3:
            # Swap the empty space with the adjacent tile
            new_index = new_row * 3 + new_col
            new_state = list(state)
            new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
            neighbors.append(tuple(new_state))

    return neighbors

def get_blank_pos(board):
    return board.index(0)


def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                return i, j
    return None 

# Get neighbors function for UCS Algorithm
def get_neighbors_ucs(board):
    neighbors = []
    blank_pos = get_blank_pos(board)
    row, col = divmod(blank_pos, 3)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for move in moves:
        new_row, new_col = row + move[0], col + move[1]
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_blank_pos = new_row * 3 + new_col
            new_board = list(board)
            new_board[blank_pos], new_board[new_blank_pos] = new_board[new_blank_pos], new_board[blank_pos]
            neighbors.append((new_board, new_board[blank_pos], move))

    return neighbors

from datetime import datetime

# Function to write the BFS search trace and results to a file
def write_bfs_to_file(current_state, fringe, visited, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size):
    # Generate a unique file name based on the current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    filename = f"trace-{timestamp}.txt"
    
    with open(filename, 'w') as file:
        # Write header information about search progress
        file.write(f"Nodes Popped: {nodes_popped}\n")
        file.write(f"Nodes Expanded: {nodes_expanded}\n")
        file.write(f"Nodes Generated: {nodes_generated}\n")
        file.write(f"Max Fringe Size: {max_fringe_size}\n")
        file.write(f"Current State:\n")
        for row in current_state:
            file.write(f"{row}\n")
        file.write("\n")
        
        # Write contents of the fringe (queue)
        file.write("Fringe:\n")
        for state, path, cost in fringe:
            file.write(f"State: {state}, Cost: {cost}, Path: {path}\n")
        
        # Write visited states (closed set)
        file.write("\nClosed Set (Visited):\n")
        for state in visited:
            file.write(f"{state}\n")
        
        file.write("\nEnd of Trace\n")

    #print(f"Trace successfully written to {filename}")

# Beginning of BFS Implementation
MOVES = {
    'Down': (-1, 0),
    'Up': (1, 0),
    'Right': (0, -1),
    'Left': (0, 1)
}

# Helper function to find the position of the blank (0)
def find_blank_bfs(state):
    for i, row in enumerate(state):
        if 0 in row:
            return i, row.index(0)

# Helper function to generate a new state after moving the blank
def move(state, direction):
    r, c = find_blank_bfs(state)
    dr, dc = MOVES[direction]
    new_r, new_c = r + dr, c + dc
    if 0 <= new_r < 3 and 0 <= new_c < 3:
        new_state = [list(row) for row in state]
        new_state[r][c], new_state[new_r][new_c] = new_state[new_r][new_c], new_state[r][c]
        return tuple(tuple(row) for row in new_state), state[new_r][new_c]  # Return the new state and cost
    return None, None

# BFS implementation
def bfs(start_state, goal_state, dump_flag):
    start_state = tuple(tuple(row) for row in start_state)
    goal_state = tuple(tuple(row) for row in goal_state)
    
    queue = deque([(start_state, [], 0)])  # (state, path, cost)
    visited = set([start_state])
    nodes_popped = nodes_expanded = nodes_generated = max_fringe_size = 0

    while queue:
        max_fringe_size = max(max_fringe_size, len(queue))
        current_state, path, cost = queue.popleft()
        nodes_popped += 1

        if current_state == goal_state:
            if dump_flag:
                write_bfs_to_file(current_state, list(queue), visited, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)
            return path, cost, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size
        
        nodes_expanded += 1
        for direction in MOVES:
            new_state, move_cost = move(current_state, direction)
            if new_state and new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [(direction, move_cost)], cost + move_cost))
                nodes_generated += 1
        
        if dump_flag:
            write_bfs_to_file(current_state, list(queue), visited, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)

    return None, -1, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size  # No solution found

# Helper function to print the output in the specified format
def print_output(path, cost, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size):
    print(f"Nodes Popped: {nodes_popped}")
    print(f"Nodes Expanded: {nodes_expanded}")
    print(f"Nodes Generated: {nodes_generated}")
    print(f"Max Fringe Size: {max_fringe_size}")
    print(f"Solution Found at depth {len(path)} with cost of {cost}.")
    print("Steps:")
    for direction, move_cost in path:
        print(f"\tMove {move_cost} {direction}")
# End of BFS code

# Function to write UCS trace search to file
def write_search_to_file(current_state, fringe, explored, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size, file_name_prefix):
    # Generate timestamp for the file name
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{file_name_prefix}-{timestamp}.txt"

    with open(file_name, 'w') as f:
        # Write current state
        f.write("Current State:\n")
        for row in current_state:
            f.write(' '.join(map(str, row)) + '\n')
        f.write("\n")

        # Write fringe details
        f.write("Fringe:\n")
        for cost, state, (zero_row, zero_col), depth, path in fringe:
            f.write(f"Cost: {cost}\n")
            f.write("Actions:\n")
            for action in path:
                f.write(f"    {action}\n")
            f.write("State:\n")
            for row in state:
                f.write(' '.join(map(str, row)) + '\n')
            f.write("\n")

        # Write explored states
        f.write("Explored States:\n")
        for state in explored:
            for row in state:
                f.write(' '.join(map(str, row)) + '\n')
            f.write("\n")

        # Write search statistics
        f.write(f"Nodes Popped: {nodes_popped}\n")
        f.write(f"Nodes Expanded: {nodes_expanded}\n")
        f.write(f"Nodes Generated: {nodes_generated}\n")
        f.write(f"Max Fringe Size: {max_fringe_size}\n")
        f.write("\n")

# Beginning of UCS Algorithm code     
moves = [("Down", -1, 0), ("Up", 1, 0), ("Right", 0, -1), ("Left", 0, 1)]

def print_board(board):
    for row in board:
        print(' '.join(map(str, row)))
    print()

def get_cost(board, row, col):
    return board[row][col]

def is_goal(state, goal):
    return state == goal

def find_empty_tile(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def get_neighbors_uniform(state, zero_row, zero_col):
    neighbors = []
    for move, row_offset, col_offset in moves:
        new_row, new_col = zero_row + row_offset, zero_col + col_offset
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_state = deepcopy(state)
            new_state[zero_row][zero_col], new_state[new_row][new_col] = new_state[new_row][new_col], new_state[zero_row][zero_col]
            neighbors.append((new_state, move, new_row, new_col))
    return neighbors

def ucs(initial_state, goal_state, dump_flag):
    # Priority queue for UCS (min-heap)
    fringe = []
    heapq.heappush(fringe, (0, initial_state, find_empty_tile(initial_state), 0, []))  # (cost, state, empty_tile_pos, depth, path)
    
    # Dictionary to store the lowest cost to reach a state
    cost_so_far = {tuple(tuple(row) for row in initial_state): 0}
    
    # Set to store explored states
    explored = set()
    
    # Track search statistics
    nodes_popped = 0
    nodes_expanded = 0
    nodes_generated = 0
    max_fringe_size = 1
    
    file_name_prefix = 'trace'

    while fringe:
        max_fringe_size = max(max_fringe_size, len(fringe))
        cost, current_state, (zero_row, zero_col), depth, path = heapq.heappop(fringe)
        
        # Convert state to tuple for hashable type
        current_state_tuple = tuple(tuple(row) for row in current_state)
        
        # Goal check
        if is_goal(current_state, goal_state):
            print(f"Nodes Popped: {nodes_popped}")
            print(f"Nodes Expanded: {nodes_expanded}")
            print(f"Nodes Generated: {nodes_generated}")
            print(f"Max Fringe Size: {max_fringe_size}")
            print(f"Solution Found at depth {depth} with cost of {cost}.")
            print("Steps:")
            for step in path:
                print(f"        {step}")
            return
        
        if dump_flag:
            write_search_to_file(current_state, fringe, explored, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size, file_name_prefix)
        
        # Skip if state is already explored
        if current_state_tuple in explored:
            continue
        
        # Mark current state as explored
        explored.add(current_state_tuple)
        nodes_popped += 1
        
        # Expand the node
        neighbors = get_neighbors_uniform(current_state, zero_row, zero_col)
        nodes_expanded += 1
        
        # Generate new states
        for neighbor, move, new_row, new_col in neighbors:
            #new_state_tuple = tuple(tuple(row) for row in neighbor)
            new_cost = cost + get_cost(current_state, new_row, new_col)
            new_path = path + [f"Move {get_cost(current_state, new_row, new_col)} {move}"]
             # Check if the new state has a lower cost path before adding to fringe
            #if new_state_tuple not in cost_so_far or new_cost < cost_so_far[new_state_tuple]:
                #cost_so_far[new_state_tuple] = new_cost
            heapq.heappush(fringe, (new_cost, neighbor, (new_row, new_col), depth + 1, new_path))
            nodes_generated += 1
            
        if dump_flag:
          write_search_to_file(current_state, fringe, explored, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size, file_name_prefix)

    print("No solution found.")
# End of UCS Algorithm code

# Beginning of IDS Algorithm code
    
# Function to get the index of the blank tile (0)
def get_blank_tile_index(state):
    return state.index(0)

# Function to swap tiles in the puzzle
def swap_tiles(state, i, j):
    state = list(state)
    state[i], state[j] = state[j], state[i]
    return tuple(state)

# Function to get possible moves
def get_neighbors_ids(state):
    neighbors = []
    blank_index = get_blank_tile_index(state)
    
    row, col = blank_index // 3, blank_index % 3
    
    # Define the possible moves (up, down, left, right)
    moves = []
    if row > 0: moves.append((-1, 0, "Down"))     # Move Up
    if row < 2: moves.append((1, 0, "Up"))    # Move Down
    if col > 0: moves.append((0, -1, "Right"))   # Move Left
    if col < 2: moves.append((0, 1, "Left"))   # Move Right
    
    for move in moves:
        new_row, new_col = row + move[0], col + move[1]
        new_index = new_row * 3 + new_col
        new_state = swap_tiles(state, blank_index, new_index)
        neighbors.append((new_state, state[new_index], move[2]))  # (new_state, cost, direction)
    
    return neighbors

# IDS with graph search
def ids_search(start_state, goal_state, dump_flag):
    def dls(state, depth):
        nonlocal nodes_popped, nodes_generated, nodes_expanded, max_fringe_size, path_cost
        
        fringe = deque([(state, 0, [])])  # (state, current_depth, path)
        visited = set()
        
        while fringe:
            if len(fringe) > max_fringe_size:
                max_fringe_size = len(fringe)
            
            current_state, current_depth, path = fringe.pop()
            nodes_popped += 1
            
            if current_state in visited:
                continue
            visited.add(current_state)
            nodes_expanded += 1
            
            if current_state == goal_state:
                path_cost = sum(cost for _, cost, _ in path)
                return path, current_depth
            
            if current_depth < depth:
                for neighbor, cost, direction in get_neighbors_ids(current_state):
                    if neighbor not in visited:
                        nodes_generated += 1
                        fringe.append((neighbor, current_depth + 1, path + [(neighbor, cost, direction)]))
        return None, None
    depth = 0
    while True:
        nodes_popped, nodes_generated, nodes_expanded, max_fringe_size = 0, 0, 0, 0
        path_cost = 0
        solution, solution_depth = dls(start_state, depth)
        
        if solution is not None:
            print(f"Nodes Popped: {nodes_popped}")
            print(f"Nodes Expanded: {nodes_expanded}")
            print(f"Nodes Generated: {nodes_generated}")
            print(f"Max Fringe Size: {max_fringe_size}")
            print(f"Solution Found at depth {solution_depth} with cost of {path_cost}.")
            print("Steps:")
            for _, cost, move in solution:
                print(f"        Move {cost} {move}")
            return
        
        depth += 1
# End of IDS Algorithm code

# Beginning of DLS Algorithm code

# Function to write search analysis to a file
def write_search_analysis_to_file(file_name_prefix, analysis_data):
     # Generate timestamp for the file name
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f"{file_name_prefix}-{timestamp}.txt"
    with open(file_name, 'w') as file:
        file.write("Depth-Limited Search Analysis\n")
        file.write(f"Depth Limit: {analysis_data['depth_limit']}\n")
        file.write(f"Nodes Popped: {analysis_data['nodes_popped']}\n")
        file.write(f"Nodes Expanded: {analysis_data['nodes_expanded']}\n")
        file.write(f"Nodes Generated: {analysis_data['nodes_generated']}\n")
        file.write(f"Max Fringe Size: {analysis_data['max_fringe_size']}\n")
        file.write(f"Solution Found at depth {analysis_data['solution_depth']} with cost of {analysis_data['solution_cost']}.\n")
        file.write("Fringe Contents:\n")
        for fringe_item in analysis_data['fringe']:
            state_str, cost, actions = fringe_item
            file.write(f"State:\n{state_str}\nCost: {cost}\nActions:\n")
            for action in actions:
                file.write(f"  Move {action[0]} {action[1]}\n")
        file.write("Closed Set Contents:\n")
        for state in analysis_data['closed_set']:
            file.write(f"State:\n{state}\n")
        file.write("Actions Taken:\n")
        for action in analysis_data['actions']:
            file.write(f"Move {action[0]} {action[1]}\n")

# Directions with corresponding moves (row, col) and human-readable names
MOVES3 = {'Down': (-1, 0), 'Up': (1, 0), 'Right': (0, -1), 'Left': (0, 1)}

# Utility function to find the position of 0 (blank) in the puzzle
def find_blank(puzzle):
    for i in range(3):
        for j in range(3):
            if puzzle[i][j] == 0:
                return i, j
    return None

# Utility function to swap two positions in a 2D list
def swap_positions(puzzle, pos1, pos2):
    new_puzzle = [row[:] for row in puzzle]
    new_puzzle[pos1[0]][pos1[1]], new_puzzle[pos2[0]][pos2[1]] = new_puzzle[pos2[0]][pos2[1]], new_puzzle[pos1[0]][pos1[1]]
    return new_puzzle

# Check if the current puzzle is the goal state
def is_goal(puzzle, goal_state):
    return puzzle == goal_state

# Function to generate successors of the current puzzle state
def generate_successors(puzzle, blank_pos):
    successors = []
    for direction, (dr, dc) in MOVES3.items():
        new_blank_pos = (blank_pos[0] + dr, blank_pos[1] + dc)
        if 0 <= new_blank_pos[0] < 3 and 0 <= new_blank_pos[1] < 3:
            new_puzzle = swap_positions(puzzle, blank_pos, new_blank_pos)
            tile_moved = puzzle[new_blank_pos[0]][new_blank_pos[1]]
            successors.append((new_puzzle, new_blank_pos, direction, tile_moved))  # (new state, new blank position, move, tile cost)
    return successors

# Depth-Limited Search (DLS) function
def dls(start_state, goal_state, depth_limit, dump_flag):
    blank_pos = find_blank(start_state)
    visited = set()
    fringe = deque([(start_state, blank_pos, [], 0, 0)])  # (state, blank_pos, path, depth, cost)
    nodes_popped = 0
    nodes_expanded = 0
    nodes_generated = 0
    max_fringe_size = 0
    fringe_contents = []
    closed_set = set()
    actions_taken = []
    
    file_name_prefix = 'trace'

    while fringe:
        max_fringe_size = max(max_fringe_size, len(fringe))
        current_state, blank_pos, path, current_depth, current_cost = fringe.pop()
        nodes_popped += 1
        
         # Convert current state to a string for output
        state_str = '\n'.join([' '.join(map(str, row)) for row in current_state])
        
        # Add current state to the fringe contents
        fringe_contents.append((state_str, current_cost, path))
        
        # If we've reached the goal, print the result
        if is_goal(current_state, goal_state):
            print(f"Nodes Popped: {nodes_popped}")
            print(f"Nodes Expanded: {nodes_expanded}")
            print(f"Nodes Generated: {nodes_generated}")
            print(f"Max Fringe Size: {max_fringe_size}")
            print(f"Solution Found at depth {current_depth} with cost of {current_cost}.")
            print("Steps:")
            for move in path:
                print(f"\tMove {move[0]} {move[1]}")
            
            analysis_data = {
                'depth_limit': depth_limit,
                'nodes_popped': nodes_popped,
                'nodes_expanded': nodes_expanded,
                'nodes_generated': nodes_generated,
                'max_fringe_size': max_fringe_size,
                'solution_depth': current_depth,
                'solution_cost': current_cost,
                'fringe': fringe_contents,
                'closed_set': list(closed_set),
                'actions': path
            }
            
            if dump_flag:
              write_search_analysis_to_file(file_name_prefix, analysis_data)
            return

        if current_depth < depth_limit:
            state_tuple = tuple(tuple(row) for row in current_state)
            if state_tuple not in visited:
                visited.add(state_tuple)
                nodes_expanded += 1
                successors = generate_successors(current_state, blank_pos)
                nodes_generated += len(successors)
                
                for successor in successors:
                    new_state, new_blank_pos, move_direction, tile_cost = successor
                    new_path = path + [(tile_cost, move_direction)]
                    fringe.append((new_state, new_blank_pos, new_path, current_depth + 1, current_cost + tile_cost))
    # If no solution found, write analysis to file
    analysis_data = {
        'depth_limit': depth_limit,
        'nodes_popped': nodes_popped,
        'nodes_expanded': nodes_expanded,
        'nodes_generated': nodes_generated,
        'max_fringe_size': max_fringe_size,
        'solution_depth': 'None',
        'solution_cost': 'None',
        'fringe': fringe_contents,
        'closed_set': list(closed_set),
        'actions': []
    }
    if dump_flag:
      write_search_analysis_to_file(file_name_prefix, analysis_data)

    print("No solution found within the depth limit.")
# End of DLS Algorithm code

        
# Beginning of Greedy Search Algorithm code      
def heuristic_greedy(state, goal):
    """Calculate the Manhattan distance heuristic."""
    dist = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                goal_i, goal_j = divmod(goal.index(state[i][j]), 3)
                dist += abs(i - goal_i) + abs(j - goal_j)
    return dist

def get_neighbors_greedy(state):
    """Generate all possible moves from the current state."""
    neighbors = []
    zero_pos = [(i, row.index(0)) for i, row in enumerate(state) if 0 in row][0]
    moves = {'Down': (-1, 0), 'Up': (1, 0), 'Right': (0, -1), 'Left': (0, 1)}
    for direction, (di, dj) in moves.items():
        new_i, new_j = zero_pos[0] + di, zero_pos[1] + dj
        if 0 <= new_i < 3 and 0 <= new_j < 3:
            new_state = [row[:] for row in state]
            new_state[zero_pos[0]][zero_pos[1]], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[zero_pos[0]][zero_pos[1]]
            neighbors.append((new_state, new_state[zero_pos[0]][zero_pos[1]], direction))
    return neighbors

def format_state(state):
    """Format the state for printing."""
    return '\n'.join(' '.join(str(cell) for cell in row) for row in state)

def write_trace_to_file(filename, trace_data):
    """Write the search trace to a file."""
    with open(filename, 'w') as file:
        file.write(trace_data)

def greedy_search(start, goal, dump_flag):
    """Perform greedy search to solve the 8 puzzle problem."""
    goal_flat = [num for row in goal for num in row]
    start_flat = [num for row in start for num in row]
    
    # Priority queue for the fringe, keeping track of the node with the lowest heuristic
    frontier = []
    heapq.heappush(frontier, (heuristic_greedy(start, goal_flat), 0, start, []))  # (heuristic, depth, state, path)
    visited = set()  # Closed set to store visited states
    visited.add(tuple(start_flat))
    
    nodes_popped = nodes_generated = nodes_expanded = max_fringe_size = 0
    trace_data = []
    
    if dump_flag:
        trace_data.append("Initial State:\n")
        #trace_data.append(f"Frontier: {list(map(lambda x: (x[1], x[2]), frontier))}\n")
        trace_data.append(f"Frontier:\n")
        for f in frontier:
            state_str = format_state(f[2])
            moves_str = " ".join(f"Move {tile} {direction}" for tile, direction in f[3])
            trace_data.append(f"    Heuristic: {f[0]}\n    State:\n{state_str}\n    Moves: {moves_str}\n")
        trace_data.append(f"Closed Set: {visited}\n")
        
    while frontier:
        # Pop the node with the lowest heuristic value
        _, depth, current_state, path = heapq.heappop(frontier)
        nodes_popped += 1
        
        if dump_flag:
            trace_data.append(f"Iteration {nodes_popped}:\n")
            trace_data.append(f"Nodes Popped: {nodes_popped}\n")
            trace_data.append(f"Nodes Expanded: {nodes_expanded}\n")
            trace_data.append(f"Nodes Generated: {nodes_generated}\n")
            trace_data.append(f"Max Fringe Size: {max_fringe_size}\n")
            #trace_data.append(f"Frontier: {list(map(lambda x: (x[1], x[2]), frontier))}\n")
            trace_data.append(f"Frontier:\n")
            for f in frontier:
                state_str = format_state(f[2])
                moves_str = " ".join(f"Move {tile} {direction}" for tile, direction in f[3])
                trace_data.append(f"    Heuristic: {f[0]}\n    State:\n{state_str}\n    Moves: {moves_str}\n")
            trace_data.append(f"Closed Set: {visited}\n")
        
        if current_state == goal:
            # Goal reached
            cost = sum(tile for tile, _ in path)
            """print(f"Nodes Popped: {nodes_popped}")
            print(f"Nodes Expanded: {nodes_expanded}")
            print(f"Nodes Generated: {nodes_generated}")
            print(f"Max Fringe Size: {max_fringe_size}")
            print(f"Solution Found at depth {depth} with cost of {cost}.")
            print("Steps:")
            for tile, direction in path:
                print(f"        Move {tile} {direction}")
            return"""
            result = f"Nodes Popped: {nodes_popped}\n"
            result += f"Nodes Expanded: {nodes_expanded}\n"
            result += f"Nodes Generated: {nodes_generated}\n"
            result += f"Max Fringe Size: {max_fringe_size}\n"
            result += f"Solution Found at depth {depth} with cost of {cost}.\n"
            result += "Steps:\n"
            for tile, direction in path:
                result += f"        Move {tile} {direction}\n"
            print(result)
            
            if dump_flag:
                trace_data.append(result)
                filename = f"trace-{datetime.now().strftime('%Y-%m-%d-%H-%M')}.txt"
                write_trace_to_file(filename, ''.join(trace_data))
            
            return
        
        nodes_expanded += 1
        # Expand neighbors
        for neighbor, tile, direction in get_neighbors_greedy(current_state):
            neighbor_flat = [num for row in neighbor for num in row]
            if tuple(neighbor_flat) not in visited:
                visited.add(tuple(neighbor_flat))
                nodes_generated += 1
                new_path = path + [(tile, direction)]
                heapq.heappush(frontier, (heuristic_greedy(neighbor, goal_flat), depth + 1, neighbor, new_path))
        
        max_fringe_size = max(max_fringe_size, len(frontier))
    
    print("No solution found.")
    if dump_flag:
        trace_data.append("No solution found.\n")
        filename = f"trace-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}.txt"
        write_trace_to_file(filename, ''.join(trace_data))
# End of Greedy Search Algorithm code


# Beginning of A* Search Algorithm code        
def write_data_to_file(filename, open_list, closed_set, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size, depth, g_values, f_values, goal_state):
    """ Write the search trace data to a file. """
    with open(filename, 'a') as file:
        file.write(f"Nodes Popped: {nodes_popped}\n")
        file.write(f"Nodes Expanded: {nodes_expanded}\n")
        file.write(f"Nodes Generated: {nodes_generated}\n")
        file.write(f"Max Fringe Size: {max_fringe_size}\n")
        file.write("Fringe:\n")
        for priority, cost, state, path in open_list:
            f_n = cost + heuristic(state, goal_state)
            file.write(f"    State: {state}, Path: {path}, Cost (g): {cost}, Depth: {len(path)}, Total Cost (f): {f_n}\n")
        file.write("Closed Set:\n")
        for state in closed_set:
            f_n = g_values.get(state, 0) + heuristic(state, goal_state)
            file.write(f"    State: {state}, Cost (g): {g_values.get(state, 0)}, Depth: {depth}, Total Cost (f): {f_n}\n")
        file.write("\n")
    
def heuristic(state, goal_state):
    """ Calculate the Manhattan distance heuristic. """
    h = 0
    for i in range(9):
        if state[i] != 0:
            goal_pos = goal_state.index(state[i])
            curr_pos = i
            goal_row, goal_col = divmod(goal_pos, 3)
            curr_row, curr_col = divmod(curr_pos, 3)
            h += abs(goal_row - curr_row) + abs(goal_col - curr_col)
    return h

def generate_moves(state):
    """ Generate possible moves from the current state. """
    moves = []
    zero_index = state.index(0)
    zero_row, zero_col = divmod(zero_index, 3)
    
    directions = [('Down', (-1, 0)), ('Up', (1, 0)), ('Right', (0, -1)), ('Left', (0, 1))]
    for direction, (drow, dcol) in directions:
        new_row, new_col = zero_row + drow, zero_col + dcol
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_state = list(state)
            new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
            move_tile = state[new_index]
            moves.append((tuple(new_state), direction, move_tile))
    return moves

def a_star_search(start_state, goal_state, move_costs, dump_flag):
    """ Perform A* search on the 8-puzzle problem. """
    open_list = []
    heapq.heappush(open_list, (0 + heuristic(start_state, goal_state), 0, start_state, []))
    closed_set = set()
    g_values = {start_state: 0}  # g(n): cost to reach the state
    nodes_popped = 0
    nodes_generated = 0
    nodes_expanded = 0
    max_fringe_size = 0
    
   # Collect trace data
    filename = f'trace-{time.strftime("%Y-%m-%d-%H-%M")}.txt'

    while open_list:
        _, cost, current_state, path = heapq.heappop(open_list)
        nodes_popped += 1
        closed_set.add(current_state)
        
        if current_state == goal_state:
             if dump_flag:
                write_data_to_file(filename, open_list, closed_set, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size, len(path), g_values, {}, goal_state)
             return {
                'nodes_popped': nodes_popped,
                'nodes_generated': nodes_generated,
                'nodes_expanded': nodes_expanded,
                'max_fringe_size': max_fringe_size,
                'solution_depth': len(path),
                'cost': cost,
                'steps': path
            }
            
        
        nodes_expanded += 1
        for new_state, direction, move_tile in generate_moves(current_state):
            if new_state not in closed_set:
                nodes_generated += 1
                new_cost = cost + move_costs[move_tile]
                g_values[new_state] = new_cost
                heapq.heappush(open_list, (new_cost + heuristic(new_state, goal_state), new_cost, new_state, path + [(move_tile, direction)]))
                max_fringe_size = max(max_fringe_size, len(open_list))
                #nodes_generated = len(new_cost)
                #max_fringe_size = max(len(open_list), len(new_cost))
                #write_data_to_file(new_state, open_list, closed_set, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)
                # Update trace data after generating a new state
        if dump_flag:
            write_data_to_file(filename, open_list, closed_set, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size, len(path), g_values, {}, goal_state)

    return None

def print_results(results):
    """ Print the results in the desired format. """
    if results:
        print(f"Nodes Popped: {results['nodes_popped']}")
        print(f"Nodes Expanded: {results['nodes_expanded']}")
        print(f"Nodes Generated: {results['nodes_generated']}")
        print(f"Max Fringe Size: {results['max_fringe_size']}")
        print(f"Solution Found at depth {results['solution_depth']} with cost of {results['cost']}.")
        print("Steps:")
        for move_tile, direction in results['steps']:
            print(f"        Move {move_tile} {direction}")
    else:
        print("No solution found.")
# End of A* Search Algorithm code

# Function to load start state from file for IDS and A* Search Algorithms
def load_state_from_file(file_path):
    """ Load the puzzle state from a file and return it as a tuple. Ignore the 'END OF FILE' marker. """
    puzzle = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line == "END OF FILE":
                break
            puzzle.extend([int(num) for num in line.split() if num.isdigit()])
    return tuple(puzzle)


def main():
    if len(sys.argv) < 3:
        print("Usage: expense_8_puzzle.py <start_file> <goal_file> <method> <dump-flag>")
        return
    
    start_file = sys.argv[1]
    goal_file = sys.argv[2]
    method = sys.argv[3] if len(sys.argv) > 3 else "a*"
    dump_flag = sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else False

    print("Method selected: ", method)
    print("\n")

    print("Running ", method)
    print("\n")
        
    if method == None:
        method = "a*"

    start_state = load_puzzle(start_file)
    goal_state = load_puzzle(goal_file)
    #print(goal_state)
    
    a_star_start = load_state_from_file(start_file)
    a_star_goal = load_state_from_file(goal_file)
    #goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    ids_start = load_state_from_file(start_file)
    ids_goal = load_state_from_file(goal_file)

    if method == "bfs":
        #result = bfs(start_state, goal_state)
        #print_solution(result)
        path, cost, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size = bfs(start_state, goal_state, dump_flag)
        if path is not None:
            print_output(path, cost, nodes_popped, nodes_expanded, nodes_generated, max_fringe_size)
        else:
            print("No solution found.")
    elif method == "ucs":
        ucs(start_state, goal_state, dump_flag)
    elif method == "ids":
        ids_search(ids_start, ids_goal, dump_flag)
    elif method == "dls":
        # Getting depth limit from the console
        depth_limit = int(input("Enter the depth limit: "))
        # For start_state = (2, 3, 6, 1, 0, 7, 4, 8, 5), must enter depth limit equal to 12 or 13 to get correct solution
        print("\n")
        dls(start_state, goal_state, depth_limit, dump_flag)
    elif method == "greedy":
        greedy_search(start_state, goal_state, dump_flag)
    else:
        #nodes_popped, nodes_expanded, nodes_generated, max_fringe_size, path, cost = a_star(start_state, goal_state)
        #move_costs = {i: i for i in range(9)}
        #print_results(results)
        move_costs = {i: i for i in range(9)}  # Cost of moving each tile is equal to the tile number

        results = a_star_search(a_star_start, a_star_goal, move_costs, dump_flag)
        print_results(results)
        
if __name__ == "__main__":
    main() 