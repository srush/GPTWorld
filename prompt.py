import io
from contextlib import redirect_stdout
tab = "    "

def animate(board, actions, show=False):
    print(tab + "p = ", board.player_pos )
    for i, action in enumerate(actions):
        #print(tab + "# Illegal next actions:", ",".join([m.value + " " + str(add(board.player_pos, Board.change(m)))  for m, msg in board.illegal_moves()]))
        for m, msg in board.illegal_moves():
            #if msg is not None:
            #    print(tab + msg)
            pass
        new_board, msg = board.move(action)
        print(tab + f"# {action.value} {Board.change(action)}  Next? {new_board.player_pos} Wall? {new_board.player_pos in new_board.wall_pos}")
        print(tab + "p = move(b, \"" + action.value + "\", p)", f"# {new_board.player_pos} Next Goal:", new_board.key_pos if new_board.key_pos else new_board.flag_pos)
        #print(tab + "assert pos ==", new_board.player_pos) 
        #print("\t# Active walls (only illegal positions):", ",".join(map(str, new_board.wall_pos)))
        #print("\t# Boundary is:",  add(new_board.flag_pos, (1 , 1)))
        #print("\tpos = ", str(new_board.player_pos))
        #print("\tassert pos not in board.walls")

        # print("\tassert pos[0] < 5")
        # print("\tassert pos[1] < 5")
        # if (i + 1) % 3 == 0:
        #     print("Board after actions")
        #     print()            
        if show:
            print(new_board)
        #     print()
            #print(f'\nActions ({every} total):')
        board = new_board
    return board

f = io.StringIO()
with redirect_stdout(f):
    print("# Consider a game on a hexagonal grid. Your objective is make legal action to get pickup a key and to reach a goal position. Here are the moves.")

    #board = Board.create_empty_board((5, 5)).create_wall((4, 4)).move(Actions.DOWN).move(Actions.RIGHT)
    comment = "change = {"
    for action in Actions:
        comment += f"{tab}\"{action.value}\" : {Board.change(action)}, \n"
    comment += "}"
    out = f"""
{comment}
def move(board, action, old_pos):
    # ACTIONS (must be legal)
    offet = change[action]
    board.move(action)
    pos = (old_pos[0] + offset[0], old_pos[1] + offset[1])
    assert 0 <= pos[0] < board.boundary[0]
    assert 0 <= pos[1] < board.boundary[1]
    assert pos not in board.walls
    if action == "PU":
        assert pos == board.key
    return pos
"""
    print(out)
        # print("\tupdate(board, ",  Board.change(action) , ")")
        # print("\tpos = board.player_pos")
        # print("\tassert 0 <= pos[0] < 5")
        # print("\tassert 0 <= pos[1] < 5")
        # print("\tassert pos not in board.walls")
        # print("\treturn pos")
    print()

    print("# Pickup can only be called on the Key position. These are the only valid actions.")


    #     print()
    #     print(board.player_pos)
    #     print('\nActions (1 total):')
    #     print(action)
    #     new_board = board.move(action)
    #     print()
    #     print("Board after actions")
    #     print()
    #     print(new_board.player_pos)
    #     print()
    ex = 0
    print("# Here is an example: ")
    def example(board, actions, show=False):
        global ex
        ex += 1
        print("#-------------")
        print("# EXAMPLE:")
        print(f"def example{ex}():")
        print(f"{tab}b = GameBoard(", board.board_state2(), ")")   
        board = animate(board, 
                actions, show)
        print(f"{tab}return b")
        print(f"#--------------")

    board = Board.create_empty_board((5, 5), (0, 2), (4, 4), (0, 0) ).create_wall((2, 2))
    actions = [Actions.RIGHT, Actions.PICKUP, Actions.DOWNLEFT,  Actions.DOWNLEFT,  Actions.DOWNRIGHT, Actions.RIGHT, Actions.DOWNRIGHT]
    example(board, actions)


    board = Board.create_empty_board((5, 5), (4, 0), (0, 0), (4, 4)).create_wall((2, 0)).create_wall((2, 4))
    actions = [Actions.LEFT, Actions.LEFT, Actions.PICKUP, Actions.UPRIGHT, Actions.UPRIGHT, Actions.UPLEFT, Actions.UPLEFT]
    example(board, actions)

    board = Board.create_empty_board((5, 5), (2, 0), (4, 4), (0, 0)).create_wall((2,2)).create_wall((3,1))
    actions = [Actions.DOWNRIGHT, Actions.DOWNLEFT, Actions.PICKUP, Actions.UPRIGHT, Actions.RIGHT, Actions.DOWNRIGHT, Actions.DOWNLEFT, Actions.DOWNRIGHT]
    example(board, actions)

    #print("# This example shows a failure that is fails because of an assertion.")
    #board = Board.create_empty_board((5, 5), (2, 0), (4, 4), (0, 0)).create_wall((0,2))
    # actions = [Actions.RIGHT]
    # example(board, actions)

    # board = Board.create_empty_board((4, 4)).create_wall((0, 1))
    # actions = [Actions.DOWN, Actions.DOWN, Actions.DOWN, Actions.RIGHT, Actions.RIGHT, Actions.RIGHT]
    # example(board, actions)


    # board = Board.create_empty_board((4, 4)).create_wall((1, 0)).create_wall((3, 3))
    # actions = [Actions.DOWN, Actions.RIGHT, Actions.DOWN, Actions.DOWN, Actions.DOWN, Actions.RIGHT, Actions.RIGHT]
    # example(board, actions)
    # print()
    # print(board)
    print("""
# ----
# Retry EXAMPLE:
def example4():
    b = GameBoard( init=(0, 0), flag=(4, 4), walls= [(1, 1), (3, 1)], boundary= (5, 5),  key= (2, 0) )
    p =  (0, 0)
    # DR (1, 1)  Next? (1, 1) Wall? True (trying again)
    # R (0, 2)  Next? (2, 0) Wall? False
    p = move(b, "R", p)
    ...
#---
""")
    
    print("# It is illegal to take actions that move you to any position with: active walls in the example, less than 0, or strictly outside the boundary.")
    print("# Do not move to these position or you will fail. To pick-up the key you must first move to its position. It is legal to be on the same position as the key." )
    print("# You will likely need to go back to the same positions that you have been in before after picking up the key, that is allowed." )
    
    print("# List the illegal action in a truthful manner. Every action is legal if it is in bounds and is not a wall. Walls are always illegal.")


    board = Board.create_empty_board((8, 15), (3, 1), (7, 13), (0, 0)).create_wall((2, 2)).create_wall((1, 1)).create_wall((5, 3)).create_wall((1, 11)).create_wall((5, 5)).create_wall((6, 6)).create_wall((6, 10)).create_wall((2, 6)).create_wall((4, 12))
    print()
    print()
    print("# Contraints for this example:", board.board_state()) 

    #print("# The following comments shows the action that are used in order")
    #print("# ")
    print()
    print("")
    print(f"# The following function shows the actions that are used to move from position 0,0 to the end goal without hitting a wall.")
    
    # print("def example():")
    # #print("\n" + tab + "# Start:")
    # print(tab + "# Contraints for this example:", board.board_state()) 
    # print(f"{tab}b = GameBoard(", board.board_state2(), ")")   
    #print("# Contraints for this example:", board.board_state()) 
    #print(f"board = GameBoard(", board.board_state2(), ")")   
    #print(f"# The following codes shows the actions that are used to move from position 0,0 to the end goal without hitting a wall.")
out = f.getvalue()
print(out)
