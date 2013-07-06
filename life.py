import sys
import curses
import locale
from terminal import *

def main():
    # Start curses screen and enable colors
    stdscr = curses.initscr()
    curses.start_color()
    # React to keys instantly
    curses.cbreak()

    # Get terminal size
    (width, height) = get_term_size()

    # Define grid
    grid = [(width-5)*[0] for i in range(height-5)]

    # Make initial grid be Conway's R-pentomino
    grid[len(grid)/2 - 1][len(grid[0])/2] = 1
    grid[len(grid)/2 + 0][len(grid[0])/2] = 1
    grid[len(grid)/2 + 1][len(grid[0])/2] = 1
    grid[len(grid)/2 - 1][len(grid[0])/2 + 1] = 1
    grid[len(grid)/2 + 0][len(grid[0])/2 - 1] = 1

    # Draw initial grid
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdscr.addstr(0, width/2-5, 'GAME OF LIFE', curses.color_pair(1))
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    stdscr.addstr(1, 0, '-'*( len(grid[0]) + 5), curses.color_pair(2))
    update_screen(grid, stdscr)
    stdscr.addstr(len(grid)+2, 0, '-'*( len(grid[0]) + 5), curses.color_pair(2))

    # Read initial config
    read_initial_conf(grid, stdscr)

    # Step through grid
    prompt = ('ITER %d: Type anything to continue, the number of steps to ' + 
              'perform (or quit to exit): ')
    iter_step = 1
    update_screen(grid, stdscr)
    while True:
        # Wait for user
        stdscr.addstr(len(grid)+3, 0, '%s' % (prompt % iter_step))
        stdscr.clrtoeol()
        play = stdscr.getstr()
        if play == 'quit':
            break
        try:
            batch_steps = int(play)
        except:
            batch_steps = 1
            pass
        for i in range(batch_steps):
            # Define auxiliary grid matrix
            new_grid = [len(grid[0])*[0] for i in range(len(grid))]
            # Update grid
            next_step(grid, new_grid)
            grid, new_grid = new_grid, grid
            # Print updated grid
            update_screen(grid, stdscr)
        iter_step += batch_steps

    # Retore terminal settings and clean up
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()

    return 0

def update_screen(grid, stdscr):
    """ update_screen: Takes the grid and updates the terminal to display it.
    (Making this function more efficient and informative is a to-do)
    """
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_RED)
    for i, line in enumerate(grid):
        stdscr.addstr(2+i, 0, '%3d'%i, curses.color_pair(4))
        for j, element in enumerate(line):
            if element:
                stdscr.addstr(2+i, 4+j, str(element), curses.color_pair(5))
            else:
                stdscr.addstr(2+i, 4+j, '-')
    stdscr.refresh()

def read_initial_conf(grid, stdscr):
    """ read_initial_conf: Reads coordinates from the user to configure the
    initial game's grid.
    It takes an already defined grid and modifies it according to user input.
    (It shouldn't let invalid input leak)
    """
    done = False
    prompt = 'CONFIG %d: Type coordinates to toggle (or start to finish) %s: '
    config_step = 0
    last_coord = ''
    while True:
        # While input isn't valid, try reading and parsing it
        coord = []
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        stdscr.addstr(len(grid)+3, 0, prompt % (config_step, last_coord),
                                                    curses.color_pair(3))
        stdscr.clrtoeol()

        while coord == []:
            # Read user's command
            cmd = stdscr.getstr()
            # Break if user is finished
            if cmd == 'start' or cmd == '':
                done = True
                break
            try:
                cmd = cmd.split()
                coord = [int(cmd[i]) for i in range(2)]
            except:
                curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
                stdscr.addstr(len(grid)+3, 0, '[Invalid input] %s' %
                                 (prompt % (config_step, last_coord)),
                                 curses.color_pair(3))
                stdscr.clrtoeol()
            last_coord = str(coord)
            config_step += 1
        # Total break if user is finished
        if done:
            break
        # Update grid (it actually toggles the grid position provided)
        grid [coord[1]][coord[0]] = (grid[coord[1]][coord[0]] + 1) % 2
        update_screen(grid, stdscr)

def next_step(grid, new_grid):
    """ next_step: Computes the grid's next step and stores it in the list
    new_grid. The latter needing to have been previously defined.
    """
    # For each column in grid...
    for x in range(0, len(grid[0])):
        # Iterate through each line in grid
        for y in range(0, len(grid)):
            # Count live cells around (x, y)
            live_neighbors = healthy_neighbors(x, y, grid)
            # Apply Game of Life's rules
            if grid[y][x]:
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[y][x] = 0
                else:
                    new_grid[y][x] = grid[y][x]
            else:
                if live_neighbors == 3:
                    new_grid[y][x] = 1

def healthy_neighbors(x, y, grid):
    """ healthy_neighbors: Returns the number of live cells neighboring the 
    given coordinate. Given it treats the grid as a loop (making this
    optional is a to-do) it should be able to handle most dumb calls.
    """
    live_neighbors = 0
    for i in range(-1, 2):
        testx = (x+i) % len(grid[0])
        for j in range(-1, 2):
            testy = (y+j) % len(grid)
            if j == 0 and i == 0:
                continue
            if grid[testy][testx] == 1:
                live_neighbors += 1
    return live_neighbors

if __name__ == '__main__':
    main()
