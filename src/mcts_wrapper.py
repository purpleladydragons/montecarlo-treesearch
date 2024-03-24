import pickle
import random
from typing import Dict
import math
from .games.tictactoe import TicTacToe
from .games.mega_tictactoe import MegaTicTacToe

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

    def save_tree(filename: str):
        print('saving tree')
        with open(filename, 'wb') as f:
            pickle.dump(MCTS.memoized_states, f)

    def load_tree(filename: str):
        try:
            with open(filename, 'rb') as f:
                print('loading tree')
                MCTS.memoized_states = pickle.load(f)
                print(f"Loaded tree from {filename} with {len(MCTS.memoized_states)} states")
        except FileNotFoundError:
            print(f"No tree found at {filename}, starting a new tree.")

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


MCTS.load_tree('megattt.pkl')
MCTS.learn(MegaTicTacToe(), games=1000)
MCTS.save_tree('megattt.pkl')

# play against trained AI
game = MegaTicTacToe()
game.prettyprint()

player = 0

while not game.is_game_over():
    if player == 0:
        move = input('Enter b,r,c move like 200: ')
        board = int(move[0])
        r = int(move[1])
        c = int(move[2])
        game = game.apply_action({'row': r, 'col': c, 'board': board})
    if player == 1:
        node = MCTS.load_node(game)
        game = MCTS.pick_next_node(node, is_learning=False).game

    game.prettyprint()
    player = 1 if player == 0 else 0


# TODO -s 
# 1. handle case where game init can be different before any actions are taken
# 2. handle chance nodes