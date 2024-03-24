from abc import ABC, abstractmethod

class Game(ABC):
    @abstractmethod
    def get_hash(self):
        pass

    @abstractmethod
    def get_player(self):
        pass

    @abstractmethod
    def is_game_over(self):
        pass

    @abstractmethod
    def get_scores(self):
        pass

    @abstractmethod
    def apply_action(self, action):
        pass

    @abstractmethod
    def get_available_actions(self):
        pass

    @abstractmethod
    def prettyprint(self):
        pass