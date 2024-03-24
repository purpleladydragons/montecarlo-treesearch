import random
import copy
from enum import Enum, auto
from typing import Dict
import math

class MCTSNode:
    def __init__(self, game):
        self.game = game
        self.num_plays = 0
        self.cumulative_score = { 0: 0, 1: 0}

    def record_scores(self, scores: Dict[int, float]):
        self.num_plays += 1
        for player, score in scores.items():
            self.cumulative_score[player] += score

    def ucb1(self, parent_plays, player, is_learning=True):
        EXPLORATION_CONSTANT = 0.2
        if self.num_plays == 0:
            if is_learning:
                return float('inf')
            return 0

        exploitation = self.cumulative_score[player] / self.num_plays
        exploration = EXPLORATION_CONSTANT * math.sqrt(2 * math.log(parent_plays) / self.num_plays)
    
        return exploitation + exploration
    
class MCTS:
    memoized_states = {}

    def __init__(self, game):
        self.root = MCTSNode(game)

    def load_node(game):
        if game.get_hash() not in MCTS.memoized_states:
            game_node = MCTSNode(game)
            MCTS.memoized_states[game.get_hash()] = game_node
        return MCTS.memoized_states[game.get_hash()]


    def pick_next_node(state, is_learning=True):
        actions = state.game.get_available_actions()
        next_nodes = []
        for action in actions:
            next_game = state.game.apply_action(action)
            next_node = MCTS.load_node(next_game)
            next_nodes.append((next_node, action))
        
        # we calculate the number of plays across all siblings, instead of using the parent
        # node directly in case that a child node has been seen before but from a different parent
        # ie this avoids the case of ln(0) in ucb1
        total_sibling_plays = sum(node.num_plays for node, _ in next_nodes)
        ucb_scores_and_nodes = []
        # we get player of _current_ state and aim to find children nodes that are favorable to current player
        player = state.game.get_player()
        for node, action in next_nodes:
            ucb = node.ucb1(total_sibling_plays, player, is_learning)
            ucb_scores_and_nodes.append((ucb, node, action))

        max_score = max(ucb_scores_and_nodes, key = lambda x: x[0])[0]
        top_scores = [t for t in ucb_scores_and_nodes if t[0] >= max_score]

        print('max ucb', max_score)

        # TODO we return node for simplicity, but practically an AI will want action not node
        chosen_node = random.choice(top_scores)[1]
        chosen_action = random.choice(top_scores)[2]

        return chosen_node


    def selfplay(state):
        played_states = [state]
        while not state.game.is_game_over():
            state = MCTS.pick_next_node(state)
            played_states.append(state)

        scores = state.game.get_scores()
        for state in played_states:
            state.record_scores(scores)

    def learn(original_game, games=100):
        original_state = MCTSNode(original_game)
        for i in range(games):
            print('game', i)
            MCTS.selfplay(original_state)


# should game provide next_states? or available_actions and it's up to us?
# it should prob give us available_actions: List[Action] and apply_action Action -> NewGameState

class TicTacToe:
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
        

MCTS.learn(TicTacToe(), games=5000)

# play against trained AI
game = TicTacToe()
game.prettyprint()

player = 0

while not game.is_game_over():
    if player == 0:
        move = input('Enter r,c move like 00: ')
        r = int(move[0])
        c = int(move[1])
        game = game.apply_action({'row': r, 'col': c})
    if player == 1:
        node = MCTS.load_node(game)
        game = MCTS.pick_next_node(node, is_learning=False).game

    game.prettyprint()
    player = 1 if player == 0 else 0


# TODO -s 
# 1. handle case where game init can be different before any actions are taken
# 2. handle chance nodes