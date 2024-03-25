import json
import pickle
import random
from typing import Dict
import math
import signal
import sys
from .games.tictactoe import TicTacToe
from .games.mega_tictactoe import MegaTicTacToe

class MCTSNode:
    def __init__(self, game):
        self.game = game
        self.num_plays = 0
        self.cumulative_score = { 0: 0, 1: 0}

    def to_json(self):
        return {
            "num_plays": self.num_plays,
            "cumulative_score": self.cumulative_score
        }

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

    def save_tree_json(filename: str):
        print('saving tree to json')
        json_data = {game_hash: node.to_json() for game_hash, node in MCTS.memoized_states.items()}
        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=4)

    @staticmethod
    def load_tree_json(filename: str, load_from_hash):
        try:
            with open(filename, 'r') as f:
                print('loading tree from json')
                json_data = json.load(f)
                for game_hash, node_data in json_data.items():
                    game = load_from_hash(game_hash)
                    game_node = MCTSNode(game)
                    game_node.num_plays = node_data['num_plays']
                    game_node.cumulative_score = {int(k): v for k, v in node_data['cumulative_score'].items()}
                    MCTS.memoized_states[game_hash] = game_node
                print(f"Loaded tree from {filename} with {len(MCTS.memoized_states)} states")
        except FileNotFoundError:
            print(f"No tree found at {filename}, starting a new tree.")


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
        found_node = MCTS.memoized_states[game.get_hash()]
        # we set the game because there are possibly relevant state facts that aren't important to save in hash
        # e.g previous move can affect where you're allowed to play now, but isn't actually relevant when deciding best next move
        # to be more clear, we set the game bc the loaded game is loaded from hash which would destroy such info
        # but the provided game arg is the same hash-wise with that extra info
        found_node.game = game
        return found_node


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

def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Saving tree to megattt.json...')
    MCTS.save_tree_json('megattt.json')
    sys.exit(0)

# signal.signal(signal.SIGINT, signal_handler)


MCTS.load_tree_json('megattt.json', MegaTicTacToe.load_from_hash)
# MCTS.learn(MegaTicTacToe(), games=5000)
# MCTS.save_tree_json('megattt.json')

print('tree loaded')

# play against trained AI
game = MegaTicTacToe()
game.prettyprint()

player = 0

while not game.is_game_over():
    if player == 0:
        action = None
        avail = game.get_available_actions()
        while action not in avail:
            move = input('Enter b,r,c move like 200: ')
            board = int(move[0])
            r = int(move[1])
            c = int(move[2])
            action = {'row': r, 'col': c, 'board': board}
        game = game.apply_action(action)
    if player == 1:
        node = MCTS.load_node(game)
        game = MCTS.pick_next_node(node, is_learning=False).game

    game.prettyprint()
    player = 1 if player == 0 else 0

print('shutting down')


# TODO -s 
# 1. handle case where game init can be different before any actions are taken
# 2. handle chance nodes