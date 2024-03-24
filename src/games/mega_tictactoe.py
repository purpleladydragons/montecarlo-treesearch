from .game import Game
import copy

class MegaTicTacToe(Game):
    def __init__(self):
        self.boards = [[['.' for _ in range(3)] for _ in range(3)] for _ in range(9)]
        self.global_board = [['.' for _ in range(3)] for _ in range(3)]
        self.player = 'X'

    def get_player(self):
        return 0 if self.player == 'X' else 1

    def get_hash(self):
        boards_str = '|'.join([''.join([''.join(row) for row in board]) for board in self.boards])
        return f"{self.player}|{boards_str}"

    def get_available_actions(self):
        actions = []
        for board_index, board in enumerate(self.boards):
            global_row, global_col = divmod(board_index, 3)
            if self.global_board[global_row][global_col] != '.':
                continue  # Skip this board as it's already won or drawn
            # Check if the global board corresponding to this board is already won
            if self.global_board[global_row][global_col] != '.':
                continue  # Skip this board as it's already won
            for row_index, row in enumerate(board):
                for col_index, cell in enumerate(row):
                    if cell == '.':
                        actions.append({'row': row_index, 'col': col_index, 'board': board_index})
        return actions

    def apply_action(self, action):
        new_game = copy.deepcopy(self)

        board_index = action['board']
        global_row, global_col = divmod(board_index, 3)
        row = action['row']
        col = action['col']
        new_game.boards[board_index][row][col] = new_game.player

        # Check if the current board has been won or is a draw
        board = new_game.boards[board_index]
        winner = new_game._check_winner_mini_board(board)
        if winner:
            new_game.global_board[global_row][global_col] = winner
        elif new_game._is_draw(board):
            new_game.global_board[global_row][global_col] = 'D'  # D for Draw

        # Switch player
        new_game.player = 'X' if new_game.player == 'O' else 'O'
        return new_game

    def _check_winner_mini_board(self, board):
        # Check rows and columns
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != '.':
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != '.':
                return board[0][i]
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != '.' or \
            board[0][2] == board[1][1] == board[2][0] != '.':
            return board[1][1]
        return None

    def _is_draw(self, board):
        for row in board:
            if '.' in row:
                return False
        return True


    def is_game_over(self):
        # Check for a win in rows, columns, and diagonals on the global board
        for i in range(3):
            if self.global_board[i][0] == self.global_board[i][1] == self.global_board[i][2] != '.':
                print('row')
                return True
            if self.global_board[0][i] == self.global_board[1][i] == self.global_board[2][i] != '.':
                print('col')
                return True
        if self.global_board[0][0] == self.global_board[1][1] == self.global_board[2][2] != '.' or \
           self.global_board[0][2] == self.global_board[1][1] == self.global_board[2][0] != '.':
            print('diag')
            print(self.global_board)
            return True

        # Check for a draw (no empty spaces left on the global board)
        if all(self.global_board[row][col] != '.' for row in range(3) for col in range(3)):
            print('draw')
            return True

        return False

    def get_scores(self):
        scores = {0: 0, 1: 0}
        # Check for a win in rows, columns, and diagonals on the global board
        for i in range(3):
            if self.global_board[i][0] == self.global_board[i][1] == self.global_board[i][2] != '.':
                winner = 0 if self.global_board[i][0] == 'X' else 1
                scores[winner] = 1
                scores[1 - winner] = -1
                return scores
            if self.global_board[0][i] == self.global_board[1][i] == self.global_board[2][i] != '.':
                winner = 0 if self.global_board[0][i] == 'X' else 1
                scores[winner] = 1
                scores[1 - winner] = -1
                return scores
        if self.global_board[0][0] == self.global_board[1][1] == self.global_board[2][2] != '.' or \
           self.global_board[0][2] == self.global_board[1][1] == self.global_board[2][0] != '.':
            winner = 0 if self.global_board[1][1] == 'X' else 1
            scores[winner] = 1
            scores[1 - winner] = -1
            return scores

        # Check for a draw
        if all(self.global_board[row][col] != '.' for row in range(3) for col in range(3)):
            scores[0] = 0
            scores[1] = 0
            return scores

        return scores

    def prettyprint(self):
        print("Full 9x9 Board:")
        for big_row in range(3):
            for small_row in range(3):
                for big_col in range(3):
                    print(" | ".join(self.boards[big_row * 3 + big_col][small_row]), end=" ")
                    if big_col < 2:
                        print("||", end=" ")
                print()
            if big_row < 2:
                print("=" * 53)
        print("\nGlobal 3x3 Board:")
        for row in range(0, 9, 3):
            print(" | ".join(self.global_board[row // 3]))
            if row < 6:
                print("-" * 5)
