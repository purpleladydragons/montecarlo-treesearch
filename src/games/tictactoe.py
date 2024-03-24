from enum import Enum, auto
import copy
from .game import Game

class TicTacToe(Game):
    class Action(Enum):
        def __init__(self, row=None, col=None):
            self.row = row
            self.col = col

        Place = auto()

    def __init__(self):
        self.board = [['.' for c in range(3)] for r in range(3)]
        self.player = 'X'

    def get_player(self):
        if self.player == 'X':
            return 0
        return 1

    def prettyprint(self):
        print("Current Board:")
        for row in self.board:
            print(" | ".join(row))
            print("-" * 9)

    def is_game_over(self):
        # Check for a win in rows, columns, and diagonals
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != '.':
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != '.':
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '.' or \
           self.board[0][2] == self.board[1][1] == self.board[2][0] != '.':
            return True

        # Check for a draw (no empty spaces left)
        for row in self.board:
            if '.' in row:
                return False
        return True

    def get_scores(self):
        # Check for a win in rows, columns, and diagonals for 'X'
        scores = {0: 0, 1: 0}
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == 'X' or \
               self.board[0][i] == self.board[1][i] == self.board[2][i] == 'X':
                scores[0] = 1
                scores[1] = -1
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == 'X' or \
           self.board[0][2] == self.board[1][1] == self.board[2][0] == 'X':
            scores[0] = 1
            scores[1] = -1

        # Check for a win in rows, columns, and diagonals for 'O'
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == 'O' or \
               self.board[0][i] == self.board[1][i] == self.board[2][i] == 'O':
                scores[0] = -1
                scores[1] = 1
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == 'O' or \
           self.board[0][2] == self.board[1][1] == self.board[2][0] == 'O':
            scores[0] = -1
            scores[1] = 1

        return scores

    def get_hash(self):
        s = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                s.append(self.board[r][c])

        return self.player + '|' + ''.join(s)

    def apply_action(self, action):
        next_state = copy.deepcopy(self)
        row = action['row']
        col = action['col']

        next_state.board[row][col] = next_state.player
        next_state.player = 'X' if next_state.player == 'O' else 'O'

        return next_state

    def get_available_actions(self):
        actions = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.board[row][col] == '.':
                    actions.append({'row': row, 'col': col})

        return actions
 