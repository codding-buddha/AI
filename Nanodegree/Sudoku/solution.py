assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]


rows = 'ABCDEFGHI'
cols = '123456789'

# Constants used within methods to avoid recalculation

# All boxes
boxes = cross(rows, cols)

# Units, Diagonal rows unit is added for the diagonal sudoku
row_units = [cross(r, cols) for r in rows]
column_untis =  [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in (rows[0:3], rows[3:6], rows[6:9]) for cs in (cols[0:3], cols[3:6], cols[6:9])]
# Diagonal rows unit 
diagonal_units = [[rows[i]+cols[i] for i in range(9)], [rows[i]+cols[9-i-1] for i in range(9)]]

# Combined list of units
unitlist = row_units + column_untis + square_units + diagonal_units

# Units lookup per box
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

# Peers lookup per box
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Iterate each unit and eliminate values if nakedtwins found
    for unit in unitlist:
        twins = []
        # Flat map of values for current unit
        flat_values = list(map(lambda x: values[x], unit))
        # lookup for nakedtwins value found
        visited = set()
        # Iterate through all boxes in the unit and populate twins list
        for box in unit:
            box_val = values[box]
            # If val length is not zero,
            # or there is no twin
            # or value is already considered then continue
            if len(box_val) != 2 or flat_values.count(box_val) != 2 or box_val in visited:
                continue

            # Twin found
            visited.add(box_val)
            twins.append(box)

        # Iterate through all found twins in the given unit
        # and eliminate duplicates values from peers in the same unit
        for twin in twins:
            twin_val = values[twin]
            for box in unit:
                box_val = values[box]
                # if peer contains twin value then reduce the posibilites
                if len(box_val) > 2 and not set(box_val).isdisjoint(set(twin_val)):
                    new_val = ''.join(digit for digit in box_val if digit not in twin_val)
                    assign_value(values, box, new_val)
    return values



def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'.
            If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
    all_digits = '123456789'
    empty = '.'
    return {box: value  if value != empty else all_digits
            for box, value in zip(boxes, grid)}

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def is_solved(board, box=None):
    """Checks if given board or box of board is already solved

    A solved box will have single value, and solved board will have no unsolved box
    if box is None then returns the status of board

    Args:
        board: Sudoku board in dictionary form
        box: board index in the form string with rowindex followed by colindex

    Returns:
        if box is None then returns the status of board otherwise if box has determined value or not
    """
    if box is None:
        return all(len(board[box]) == 1 for box in board.keys())
    else:
        return len(board[box]) == 1


def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_boxes = [box for box in values.keys() if is_solved(values, box)]
    for box in solved_boxes:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))

    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a values
    that only fits in one box, assign the value to this box.

    Args:
        values: Sudoku in dictionary form

    Returns: Resulting Sudoku in dictionary form after fillint in only choices

    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)

    return values


def reduce_puzzle(values):
    """Reduces puzzle by apply constraints repeatedly

    Args:
        values: Sudoku in dictionary form

    Returns:
        board with constraints applied to it
    """

    stalled = False
    while not stalled:
        # Count of boxes having determined values before elimination
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Elimination Strategy
        values = eliminate(values)

        # NakedTwins Strategy
        values = naked_twins(values)

        # Only Choice Strategy
        values = only_choice(values)

        # Count of boxes having determined values after elimination
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        # Check for progress
        stalled = solved_values_before == solved_values_after

        # If there is box with zero available
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    """Using DFS and propagation, create a search tree and solve the sudoku"""

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    if is_solved(values):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    _, search_node = min((len(values[box]), box) for box in values.keys() if len(values[box]) > 1)

    # Now use recursion to solve each one of the resulting sudokus,
    # and if one returns a value (not False), return that answer
    possible_values = [digit for digit in values[search_node]]

    for possible_value in possible_values:
        new_sudoku = values.copy()
        new_sudoku[search_node] = possible_value
        result = search(new_sudoku)
        # If result is not False then solution is Found, else continue with other possibilities
        if result:
            return result

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Get dictionary representation of the board
    board = grid_values(grid)
    # search possible solution for the puzzle
    return search(board)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
