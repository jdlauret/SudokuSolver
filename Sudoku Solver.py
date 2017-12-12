assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    # returns box notation for grid ie. A1, B1, A2, B2
    return [s+t for s in a for t in b]


# contains all boxes for grid
boxes = cross(rows, cols)

# contains all rows in grid
row_units = [cross(r, cols) for r in rows]

# contains all columns in grid
col_units = [cross(rows, c) for c in cols]

# contains all squares in grid
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

# contains first diagonal
diagonal1 = [a[0]+a[1] for a in zip(rows, cols)]

# contains second diagonal
diagonal2 = [a[0]+a[1] for a in zip(rows, cols[::-1])]

# contains both diagonal
diagonal_units = [diagonal1, diagonal2]


def assign_value(values, box, value):
    # Assigns a value to a given box. If it updates the board record it.

    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def grid_values(grid):
    # converts a string containing the board layout into a dictionary
    grid_dict = {}
    values = '123456789'
    for i, char in enumerate(grid):
        if char == '.':
            grid_dict[boxes[i]] = values
        else:
            grid_dict[boxes[i]] = char
    return grid_dict


def display(values):
    # prints a representation of the sudoku board based on the values contained within in the dictionary
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in cols))
        if r in 'CF':
            print(line)
    return


def naked_twins(values):
    # naked_twins searches for naked twins and removes values from the relevant peers

    # finds twin candidates
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    twin_candidates = []
    for box in boxes:
        if len(values[box]) == 2:
            if box not in twin_candidates:
                twin_candidates.append(box)

    # finds if any of the candidates are peers of each other
    pairs = []
    for candidate in twin_candidates:
        for i in range(0, len(twin_candidates)):
            if candidate != twin_candidates[i]:
                if twin_candidates[i] in peers[candidate]:
                    if values[twin_candidates[i]] == values[candidate]:
                        if sorted([twin_candidates[i], candidate]) not in pairs:
                            pairs.append(sorted([twin_candidates[i], candidate]))

    # finds all peers of a twins and removes the values found in the twin from the peers
    for pair in pairs:
        box_1 = pair[0]
        box_2 = pair[1]
        for unit in unit_list:
            if box_1 in unit\
                    and box_2 in unit:
                for box in unit:
                    if box not in solved_values\
                            and box not in pair:
                        for digit in values[box_1]:
                            new_value = values[box].replace(digit, '')
                            assign_value(values, box, new_value)

    # returns the adjusted values
    return values


def eliminate(values):
    # eliminate finds solved boxes and removes the solved value from all of it's peers
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        value = values[box]
        for peer in peers[box]:
            new_value = values[peer].replace(value, '')
            assign_value(values, peer, new_value)

    return values


def only_choice(values):
    # only_choice searches for if there is only one box in a unit which would allow a certain value,
    # then that box is assigned that value
    for unit in unit_list:
        for digit in '123456789':
            digits_found = []
            for cell in unit:
                if digit in values[cell]:
                    digits_found.append(cell)
            if len(digits_found) == 1:
                assign_value(values, digits_found[0], digit)
    return values


def reduce_puzzle(values):
    # reduce_puzzle runs a set of values through eliminate(), only_choice(), and naked_twins()
    # until the values before and after are the same
    # if the values are the same it exits the loop and returns the values
    # if any values are completely removed resulting in a length of 0
    # the function returns a False
    stalled = False
    while not stalled:
        if isinstance(values, str):
            values = grid_values(values)
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = only_choice(
            naked_twins(
                eliminate(values)
            )
        )
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    # uses reduce_puzzle
    # creates a search tree by finding the box with the minimum number of possible options
    # creates a copy for each possible options contained in the box
    # attempts to solve each of the possible options recursively with the left most option first
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values

    num, box = min(
        # creates list of tuples and searches for the min value in the list
        (len(values[box]), box)
        for box in boxes if len(values[box]) > 1
    )

    for value in values[box]:
        new_sudoku = values.copy()
        new_sudoku[box] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    # used string input and coverts it to a grid
    # then hands off the grid to search to be solved
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    """
    HOW TO USE:
    Find any sudoku puzzle you want to solve
    A good place to look is http://sudoku.menu/
    If you select a puzzle where the diagonals can be solved make sure to change solve_diagonals to True
    """
    solve_diagonals = False
    # Example Puzzles

    diagonal_sudoku = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    very_hard_sudoku = '.46.1......28.....1.32.......872.4...9.....2...7.613.......71.2.....58......9.73.'

    if solve_diagonals:
        # list with all units
        unit_list = row_units + col_units + square_units + diagonal_units
    else:
        unit_list = row_units + col_units + square_units

    units = dict((s, [u for u in unit_list if s in u]) for s in boxes)
    peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

    # contains the grid in a string format
    # displays solved grid
    # visualizes the solving of the grid
    display(solve(very_hard_sudoku))
