from agent import *
import random

class Qlearning(Agent):
    def reset(self):
        Agent.reset(self)
        self.Q = zeros((STATE_COUNT, ACTION_COUNT))
        self.epsilon = 0.1
        self.alpha = 0.1
        self.gamma = 1
    
    def do_step(self, S, act):
        Agent.do_step(self, S, act)
        
        # Epsilon-greedy action selection
        if ranf() <= self.epsilon:
            # Choose a random action (0 or 1)
            A = randint(ACTION_COUNT)
        else:
            # Choose the best action for this state
            Qs = self.Q[S]
            maxQ = max(Qs)
            As = where(Qs == maxQ)[0]
            A = random.choice(As)
        
        # Observe reward and new state
        R, Sp = act(A)
        
        # Update return
        self.G += R
        
        # max_a(Q(S', a))
        nextmax = 0 if Sp == TILE_GOAL else max(self.Q[Sp])
        
        # Update Q for this state/action pair
        self.Q[S][A] += self.alpha * (R + self.gamma * nextmax - self.Q[S][A])
