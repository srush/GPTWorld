from typing import List, Tuple, Optional
from enum import Enum

class Actions(Enum):
    UPRIGHT = "UR"
    RIGHT = "R"
    DOWNRIGHT = "DR"
    DOWNLEFT = "DL"
    LEFT = "L"
    UPLEFT = "UL"
    PICKUP = "Pickup"
    # Add more actions here if needed

class Board:
    def __init__(self, grid: List[str], player_pos: Tuple[int, int], 
                 flag_pos: Tuple[int, int], wall_pos:List[Tuple[int, int]], 
                 key_pos:Optional[Tuple[int, int]]):
        self.grid = grid
        self.player_pos = player_pos
        self.flag_pos = flag_pos
        self.wall_pos = wall_pos
        self.key_pos = key_pos

    @staticmethod
    def change(action):
        if action == Actions.UPRIGHT:
            dx, dy = -1, 1
        elif action == Actions.UPLEFT:
            dx, dy = -1, -1
        elif action == Actions.DOWNLEFT:
            dx, dy = 1, -1
        elif action == Actions.DOWNRIGHT:
            dx, dy = 1, 1
        elif action == Actions.LEFT:
            dx, dy = 0, -2
        elif action == Actions.RIGHT:
            dx, dy = 0, 2
        elif action == Actions.PICKUP:
            dx, dy = 0, 0
        return dx, dy

    def move(self, action: Actions) -> 'Board':
        dx, dy = 0, 0
        if action == Actions.UPRIGHT:
            dx, dy = -1, 1
        elif action == Actions.UPLEFT:
            dx, dy = -1, -1
        elif action == Actions.DOWNLEFT:
            dx, dy = 1, -1
        elif action == Actions.DOWNRIGHT:
            dx, dy = 1, 1
        elif action == Actions.LEFT:
            dx, dy = 0, -2
        elif action == Actions.RIGHT:
            dx, dy = 0, 2
        elif action == Actions.PICKUP:
            dx, dy = 0, 0
            if self.player_pos[0] == self.key_pos[0] and self.player_pos[1] == self.key_pos[1]:
                return Board(self.grid, self.player_pos, self.flag_pos, self.wall_pos, None), "pickup"
            else:
                return self, "nokey"

        else:
            # Handle other actions here if needed
            print("fail")
        
        new_player_pos = (self.player_pos[0] + dx, self.player_pos[1] + dy)
        if self.grid[new_player_pos[0]][new_player_pos[1]] == 'W':
            # Can't move through walls
            return self, "WALL"
            
        new_grid = [row[:] for row in self.grid] # Create a copy of the grid
        new_grid[self.player_pos[0]][self.player_pos[1]] = '.'
        new_grid[new_player_pos[0]][new_player_pos[1]] = '@'
        return Board(new_grid, new_player_pos, self.flag_pos, self.wall_pos, self.key_pos), "Good"
    
    def create_wall(self, pos: Tuple[int, int]) -> 'Board':
        if self.grid[pos[0]][pos[1]] in ( '@', 'P'):
            # Can't place a wall on top of another object
            return self
        
        new_grid = [row[:] for row in self.grid] # Create a copy of the grid
        new_grid[pos[0]][pos[1]] = "W"
        return Board(new_grid, self.player_pos, self.flag_pos, self.wall_pos + [pos], self.key_pos)
    
    
    def __str__(self) -> str:
        # return '\n'.join((' ' * i %2) + ' '.join(row) for i, row in enumerate(self.grid))
        return '\n'.join(''.join(row) for i, row in enumerate(self.grid))
    
    def illegal_moves(self):
        for action in Actions:
            dx, dy = self.change(action)
            new_player_pos = (self.player_pos[0] + dx, self.player_pos[1] + dy)
            if new_player_pos[0] < 0 or new_player_pos[0] > self.flag_pos[0]:
                #yield action, f"assert not 0 <= {new_player_pos[0]} < {self.flag_pos[0] + 1}"
                continue
            if new_player_pos[1] < 0 or new_player_pos[1] > self.flag_pos[1]:
                #yield action, f"assert not 0 <= {new_player_pos[1]} < {self.flag_pos[0] + 1}"
                continue
            if action == Actions.PICKUP and not(self.key_pos is not None and self.player_pos[0] == self.key_pos[0] and self.player_pos[1] == self.key_pos[1]):
                yield action, f"assert {new_player_pos} != board.key"
                continue
            if self.grid[new_player_pos[0]][new_player_pos[1]] == 'W':
                yield action, f"assert {new_player_pos} in board.walls"
                continue
            continue

    def board_state(self) -> str:
        walls = ",".join(map(str, self.wall_pos))
        return f"Flag: {self.flag_pos} | Walls (illegal): {walls} | Boundary: {add(self.flag_pos, (1, 1))} | Key: {self.key_pos}"
    def board_state2(self) -> str:
        walls = ",".join(map(str, self.wall_pos))
        return f"init={self.player_pos}, flag={self.flag_pos}, walls= {self.wall_pos}, boundary= {add(self.flag_pos, (1, 1))},  key= {self.key_pos}"

    def player_state(self) -> str:
        msg = " K"  if self.key_pos is None else ""
        return f"{self.player_pos}{msg}"

    @classmethod
    def create_empty_board(cls, size: Tuple[int, int], key_pos, flag_pos, init) -> 'Board':
        grid = [['.' if i % 2 == j % 2  else " " for i in range(size[1])] for j in range(size[0])]
        player_pos = init
        flag_pos = flag_pos
        grid[player_pos[0]][player_pos[1]] = '@'
        grid[flag_pos[0]][flag_pos[1]] = 'P'
        grid[key_pos[0]][key_pos[1]] = 'K'
        return cls(grid, player_pos, flag_pos, [], key_pos)
def add(a, b):
    return a[0] + b[0], a[1] + b[1]

class GameBoard:
    def __init__(self, init, flag, walls, key, boundary):
        self.board = Board.create_empty_board(boundary, key, flag, init)
        for wall in walls:
            self.board = self.board.create_wall(wall)
        self.original = self.board

        self.actions = []
    def move(self, action):
        self.board, _ = self.board.move(action)
        self.actions.append(action)

    @property
    def walls(self):
        return self.board.wall_pos
