import os
import sys
sys.path.insert(0, "/home/srush/Projects/MiniChain/venv/lib/python3.10/site-packages")
print(sys.path)
import gradio as gr
from dataclasses import dataclass
from chalk import *
from colour import Color
import inspect
import os
import openai
from typing import List, Tuple, Optional
from enum import Enum
import io
from contextlib import redirect_stdout
import imageio
import tiktoken
import time
openai.api_key = ""
tab = "    "

def start2(prompt, board, api_key):
    out = ""
    # for chunk in openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[{
    #         "role": "user",
    #         "content": prompt,
           
    #     }],
    #     stream=True,
    #     temperature= 0
    # ):
    board = board#Game(boundary=(9, 9), key=(1, 1), flag=(2, 2), init=(0, 0), walls=[(2, 0)])
    actions = [Actions.DOWNRIGHT, Actions.RIGHT, Actions.DOWNRIGHT, Actions.PICKUP, Actions.DOWNRIGHT]
    contents = example(board, actions)
    print(contents)
    # encoding = tiktoken.encoding_for_model("gpt-4")
    # num_tokens = encoding.encode(string)

    for content in contents:
        time.sleep(0.005)
        content = content
        if content is not None:
            out += content
            print(content, end="")
            yield out
    yield out
    
def start(prompt, board, api_key):
    out = ""
    # encoding = tiktoken.encoding_for_model("gpt-4")
    # num_tokens = encoding.encode(string)
    content = ""
    openai.api_key = api_key
    for chunk in openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": prompt,
           
        }],
        stream=True,
        temperature= 0
    ):

    # for content in contents:
        time.sleep(0.005)
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            out += content
            print(content, end="")
            yield out
    yield out

def num_tokens_from_string(string: str, encoding_name: str="gpt-4") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


# + [markdown] id="LMTjwXdD7v-I"
# ## Game Code
#
# This code creates a mini-game to play. It takes place on a hexagon. You are represented by a circle. You need to first pick up a key represented by a triangle. You finally need to make it to the cross to finish the game. The actions show each of the directions you can move.
#
#

# + id="Fv3eTRKiV2ZB" cellView="form"
#@title Game Code

# Possible Actions
class Actions(Enum):
    UPRIGHT = "UR"
    RIGHT = "R"
    DOWNRIGHT = "DR"
    DOWNLEFT = "DL"
    LEFT = "L"
    UPLEFT = "UL"
    PICKUP = "Pickup"

# Movements
change = {    
    Actions.UPRIGHT : (-1, 1), 
    Actions.RIGHT : (0, 2), 
    Actions.DOWNRIGHT : (1, 1), 
    Actions.DOWNLEFT : (1, -1), 
    Actions.LEFT : (0, -2), 
    Actions.UPLEFT : (-1, -1), 
    Actions.PICKUP : (0, 0), 
}
change_str = {action.value: change[action] for action in Actions}
def add(a, b):
    return a[0] + b[0], a[1] + b[1]

@dataclass
class Board:
    grid: List[str]
    player_pos: Tuple[int, int]
    flag_pos: Tuple[int, int]
    wall_pos:List[Tuple[int, int]]
    key_pos:Optional[Tuple[int, int]]

    def move(self, action: Actions) -> 'Board':
        "Move by creating a new board."
        d_m = change[action]        
        if action == Actions.PICKUP:
            if self.player_pos == self.key_pos:
                return Board(self.grid, self.player_pos, self.flag_pos, self.wall_pos, None)
            else:
                return self
        
        new_player_pos = add(self.player_pos, d_m)
        # Out of bounds
        if new_player_pos[0] < 0 or new_player_pos[0] >= len(self.grid):
            return self
        if new_player_pos[1] < 0 or new_player_pos[1] >= len(self.grid[0]):
            return self
        # Can't move through walls
        if self.grid[new_player_pos[0]][new_player_pos[1]] == 'W':
            return self
            
        new_grid = [row[:] for row in self.grid] # Create a copy of the grid
        new_grid[self.player_pos[0]][self.player_pos[1]] = '.'
        new_grid[new_player_pos[0]][new_player_pos[1]] = '@'
        return Board(new_grid, new_player_pos, self.flag_pos, self.wall_pos, self.key_pos)
    
    def __str__(self) -> str:
        return '\n'.join(''.join(row) for i, row in enumerate(self.grid))

    @classmethod
    def create_empty_board(cls, size: Tuple[int, int], key_pos, flag_pos, init, wall_pos) -> 'Board':
        grid = [['.' if i % 2 == j % 2  else " " for i in range(size[1])] for j in range(size[0])]
        player_pos = init
        flag_pos = flag_pos
        grid[player_pos[0]][player_pos[1]] = '@'
        grid[flag_pos[0]][flag_pos[1]] = 'P'
        grid[key_pos[0]][key_pos[1]] = 'K'
        for pos in wall_pos:
            grid[pos[0]][pos[1]] = 'W'
        return cls(grid, player_pos, flag_pos, wall_pos, key_pos)

class Game:
    def __init__(self, init, flag, walls, key, boundary):
        "Create the version of the game that the AI sees."
        self.boundary = boundary
        self.board = Board.create_empty_board(boundary, key, flag, init, walls)
        self.original = self.board
        self.actions = []

    def move(self, action):
        self.board = self.board.move(action)
        self.actions.append(action)

    @property
    def walls(self):
        return self.board.wall_pos

    def __repr__(self) -> str:
        walls = ",".join(map(str, self.board.wall_pos))
        return f"Game(init={self.board.player_pos}, flag={self.board.flag_pos}, walls={self.board.wall_pos}, boundary={self.boundary}, key={self.board.key_pos})"

# This is the version of move that the AI can see.
def move(game, action, old_pos):
    # ACTIONS (must be legal)
    game.move(Actions(action))
    offset = change_str[action]
    pos = (old_pos[0] + offset[0], old_pos[1] + offset[1])
    
    assert 0 <= pos[0] < game.boundary[0], "Row position out of bounds"
    assert 0 <= pos[1] < game.boundary[1], "Col position out of bounds"
    assert pos not in game.walls, f"Walked into wall {pos}"
    if action == "PU":
        assert pos == game.key, f"Not over key"
    return pos


# + [markdown] id="PDOcPiQq8u_Y"
# We can look at the board by drawing it. 

# + colab={"base_uri": "https://localhost:8080/", "height": 221} id="Ic7WgOTi8uF1" outputId="4dc07cb9-9e5f-4d28-d4ea-470ad4b13141"
#@title Drawing code
def draw_board(grid, num=0):
    hex = regular_polygon(6, 1).rotate_by(1/12).line_width(0.5).fill_color(Color("white"))
    w = hex.get_envelope().width
    canvas = empty()
    for r, b in enumerate(grid):
        def show(v):
            if v == ".":
                return hex
            if v == "@":
                return hex + circle(0.35).fill_color(Color("red")) 
            if v == "P":
                x = rectangle(0.25, 0.7).fill_color(Color("blue")).line_width(0)
                return hex + (x.rotate_by(0.25/2) + x.rotate_by(-0.25/2))
            if v == "K":
                return hex + triangle(0.75).fill_color(Color("purple"))
            if v == "W":
                return hex.fill_color(Color("black"))
            if v ==" ":
                return hex
        row = hcat(show(v) for i, v in enumerate(b[1 if r %2 else 0::2]))
        canvas += row.translate(w * 0.5 if r%2 else 0, 1.5 * r)
    canvas = canvas.center_xy().frame(0.5)
    canvas = rectangle(canvas.get_envelope().width, canvas.get_envelope().height).line_width(0.5).fill_color(Color("orange")) + canvas
    canvas.render_svg(f"pic{num}.svg", 256)
    return canvas



# + colab={"base_uri": "https://localhost:8080/", "height": 424} id="nqgPKLu0AMhU" outputId="19e4c6d0-b792-4a34-f4c4-81902974c346"
# game = Game(boundary=(5, 5), key=(0, 2), flag=(4, 4), init=(0, 0), walls=[(2, 2)])
# display(draw_board(game.board.grid))
# move(game, "DR", (0,0))
# display(draw_board(game.board.grid))


# + [markdown] id="PhqF9af5_jvh"
# ## Prompt Code
#
# The puzzle is to write prompt code to make the model accomplish this task. We have provided some scaffolding code for you. The code creates:
#
# * A header for describing the game. 
# * A function `make_fun` that shows the AI how to move in code. 
# * A footer to describe the final game board that you want the mode to solve. 
#
# You can fill this in a watch how the model moves around.

# + id="jFf7TCOJaVHX"
#@title Make the Prompt
def make_fun(board, actions):
    "This function generates python code for few-shot examples"
    out = tab + "p = " + str(board.player_pos)
    for i, action in enumerate(actions):
        new_board = board.move(action)
        out += f"""
    # TODO ADD CODE
    p = move(b, "{action.value}", p) # TODO ADD CODE"""
        board = new_board
    return out

def example(game, actions):
    """
    This code makes a few shot example. You don't need to edit it.
    """
    return f"""
def my_example():
    b = {repr(game)} 
{make_fun(game.board, actions)}
    return b
"""


ex = 0
def prompt(game):
    """
    You should fill these sections out to teach the AI how to play the game.

    Or you may do your own thing :)
    """
    print(f"""
# TODO: DESCRIBE THE GAME

# TODO: DESCRIBE THE ACTIONS
change_str = {change_str}

{inspect.getsource(move)}
""")

    def example(game, actions):
        """
        This code makes a few shot example. You don't need to edit it.
        """
        global ex
        ex += 1
        print(f"""
def example{ex}():
    b = {repr(game)} 
{make_fun(game.board, actions)}
    return b
# ------------
""")

    # Create a few shot example (you may not need this)
    board = Game(boundary=(3, 3), key=(1, 1), flag=(2, 2), init=(0, 0), walls=[(2, 0)])
    actions = [Actions.DOWNRIGHT, Actions.PICKUP, Actions.DOWNRIGHT]
    example(board, actions)

    # Test case
    print(f"""
# ----
# TODO: ADD any custom example code
#---
# TODO: FINAL description.

# Contraints for this function:", {repr(game)}
# Please fill this in with code like the examples above (do not provide a description):
# 
# The following function `my_example` instantiates a GameBoard called b with these constraints.

""")    
    


# + [markdown] id="-iecyV7nAbFT"
# This code lets you make a game and see the output for a prompt for that game. There are easy, medium, and hard games. 

# + colab={"base_uri": "https://localhost:8080/"} id="cOneYFok_OMe" outputId="97080186-7322-4ba9-b500-095fb39071aa"
# Easy
easy_game = Game(boundary=(3, 3), key=(1, 1), flag=(2, 2), init=(0, 0), walls=[])

# Medium
medium_game = Game(boundary=(5, 5), key=(3, 1), flag=(4, 4), init=(0, 0), walls=[(1, 1)])

# Hard (This is the main one)
hard_game = Game(boundary=(8, 15), key=(3, 1), flag=(7, 13), init=(0, 0), walls=[(2, 2), (1, 1), (5, 3), (1, 11), (5, 5), (6, 6), (6, 10), (2, 6), (4, 12)])

# Evil
evil_game = Game(boundary=(8, 15), key=(5, 1), flag=(7, 13), init=(0, 0), walls=[(2, 2), (3, 3), (4, 2), (1, 1), (2, 4), (7, 11), (5, 3), (1, 11), (5, 5), (6, 6), (6, 10), (2, 6), (4, 12)])

games = {"Easy": easy_game, "Medium": medium_game, "Hard": hard_game, "Evil": evil_game}

# Animate the outputs as a GIF
def animate(l):
    images = []
    for i in range(l):
        images.append(imageio.v2.imread(f"pic{i}.png"))
    return imageio.v2.mimsave('movie.gif', images, **{ 'duration': 0.5 })


def load(inp):
    if inp in games:
        board = games[inp]
    else:
        board = eval(inp)
    draw_board(board.board.grid, 0).render_svg("tmp.svg")
    
    return ["tmp.svg"], repr(board)

draw_board(hard_game.board.grid, 0).render_svg("hard.svg")
draw_board(easy_game.board.grid, 0).render_svg("easy.svg")
with gr.Blocks() as app:

    # test = gr.Code(label="test")
    # im2 = gr.Gallery()
    # im2.style(preview=True)
    gr.Markdown("""
# GPTWorld

GPTWorld is a prompting game. Your goal is to get an LLM to complete a maze. If you can do this successfully, it will be able to navigate itself through the world from the start (o) to the key the exit (x). In the bottom right we show you a sample target output of GPT for a maze. Your goal is to get the model to generate this from scratch for an unseen maze.


The game takes place on a hexagonal grid with walls. Even rows are labeled (0,0), (0, 2), (0,4) and odd rows are labeled (1, 1), (1, 3), (1, 5). This was done to make the puzzle a bit less common.

""")
    
    with gr.Row():
        with gr.Column():
            game_desc = gr.Text(label="Game")
            examples = gr.Radio(show_label=False,
                            choices=["Easy", "Medium", "Hard", "Evil"])
            api_key = gr.Text(label="OpenAI Key", type="password",
                              value=os.environ.get("OPENAI_API_KEY"))
            prompt = gr.Code(label="prompt", language="python", lines=40, value=f"""
# A prompt to describe this game to the GPT model.

# Ideas: 
# * Describe how the game works 
# * Give code examples that solve similar mazes.
# * Give examples to explain the reasoning process

# For example you might want to tell it how the moves work

change_str = {change_str}

# Or make up a clear implementation for the move function

def move(board, action, old_pos):
    # ACTIONS (must be legal)
    board.move(action)
    offset = change_str[action]
    pos = (old_pos[0] + offset[0], old_pos[1] + offset[1])
    assert 0 <= pos[0] < board.boundary[0]
    assert 0 <= pos[1] < board.boundary[1]
    assert pos not in board.walls
    if action == "Pickup":
        assert pos == board.key
    return pos

# You can test your code on the right side.

# Finally use %GAME% to inject the game description above.
""")
            with gr.Row():
                start_btn = gr.Button("Prompt >")
                cancel_btn = gr.Button("Cancel")
        with gr.Column():
            im = gr.Gallery()
            im.style(preview=True)

            output = gr.Code(language="python", value="""def my_example():
    b = Game(init=(0, 0), flag=(2, 2), walls= [], boundary= (3, 3), key= (1, 1)) 
    p = (0, 0)
    # This is the code you want it to generate.
    p = move(b, "DR", p) 
    p = move(b, "Pickup", p)
    p = move(b, "DL", p)
    p = move(b, "R", p)
    return b
""", lines=50)
            msg_box = gr.Text(label="Errors")
            counter = gr.Slider(label="length", minimum=0, maximum=3000)
            run_btn = gr.Button("Rerun ^")


            
    examples.change(load, inputs=[examples], outputs=[im, game_desc])
    game_desc.submit(load, inputs=[game_desc], outputs=[im, game_desc])
    def run(data):

        board = eval(data[game_desc]) #games[data[examples]]
        inp = data[prompt].replace("%GAME%", repr(board))
        print(inp)
        q = {}
        i = 0
        count = 0
        im_ = [f"tmp.svg"]
        yield {im: im_, counter: 0, output: "", msg_box: ""}

        for prefix in start(inp, board, data[api_key]):
            ps = prefix.split("\n")
            count += 1

            if len(ps) > 3 and not ps[-2].strip().startswith("#") and prefix.endswith("\n"):
                print("rendering")
                try:
                    exec(prefix + f"\n    return b\nq['board'] = my_example({repr(board)})")
                except AssertionError as e:
                    print("fail")
                    yield {im: [f"pic{j}.svg" for j in range(i)], counter: count, output: prefix, msg_box: f"You made an illegal move: {e}"}
                    return
                draw_board(q["board"].board.grid, i).render_svg("tmp.svg")
                i += 1
                im_ = [f"pic{j}.svg" for j in [i-1]]
                yield {im: im_, counter: count, output: prefix}
            else:
                yield {im: im_, counter: count, output: prefix}
        yield {im: [f"pic{j}.svg" for j in range(i)], counter: count, output: prefix}
    start_prompt = start_btn.click(run, inputs={prompt, game_desc, api_key}, outputs={im, output, counter, msg_box})
    cancel_btn.click(None, cancels=[start_prompt])
    def run2(data):
        c = data[output]
        print(c)
        i = 0
        for j in range(len(c)):
            q = {}
            prefix = c[:j]
            ps = prefix.split("\n")
            if len(ps) > 3 and not ps[-2].strip().startswith("#") and prefix.endswith("\n"):
                print("rendering", prefix)
                exec(prefix + "\n    return b\nq['board'] = my_example()")
                draw_board(q["board"].board.grid, i)
                i += 1
        animate(i)
        out =  {im: [f"pic{j}.svg" for j in range(i)]}
        print(out)
        return out
    run_btn.click(run2, inputs={output}, outputs={im})


    
app.queue().launch()


# f = io.StringIO()
# with redirect_stdout(f):
#     ex = 0
#     prompt(game)
# my_prompt = f.getvalue()
# print(my_prompt)

# # + id="LONWUsBLjOHo" colab={"base_uri": "https://localhost:8080/", "height": 1000} outputId="472afd19-48c1-4924-cabd-639b5e2ad298"
# # Run an LLM and execute it as it runs. 
# q = {}
# i = 0
# for prefix in start(my_prompt):
#     ps = prefix.split("\n")
#     if len(ps) > 3 and not ps[-2].strip().startswith("#") and prefix.endswith("\n"):
#         exec(prefix + "\n    return b\nq['board'] = my_example()")
#         display(draw_board(q["board"].board.grid, i))
#         i += 1


# animate(i)
# display(Image("movie.gif"))


# # Print the number of tokens used
# print("Input Tokens:", num_tokens_from_string(my_prompt))
# print("Output Tokens:", num_tokens_from_string(prefix))

