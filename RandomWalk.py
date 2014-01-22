from agent import *

class RandomWalk(Agent):
    def do_step(self, S, act):
        Agent.do_step(self, S, act)
        
        R, Sp = act(randint(ACTION_COUNT))
        self.G += R
