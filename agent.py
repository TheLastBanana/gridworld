import random

TILE_GOAL = 16

class Agent():
    def __init__(self):
        """
        Initialize the learning agent.
        """
        init_episode()
    
    def init_episode(self):
        """
        Initializes an episode. Override this to also clear any data!
        """
        self.step = 0

    def step(self, S, act):
        """
        Make the agent take a single step. The agent is given its current state
        and a function to call which takes an action and returns a pair of
        (reward, state).
        Possible actions are:
            0 = go right
            1 = go up
            2 = go left
            3 = go down
        """
        act(random.randint(0, 3))
