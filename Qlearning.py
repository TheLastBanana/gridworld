from agent import *

class Qlearning(Agent):
    def reset(self):
        Agent.reset(self)
        self.Q = 0.00001 * rand(STATE_COUNT, ACTION_COUNT)
        self.epsilon = 0.5
        self.alpha = 0.01
        self.gamma = 1
    
    def do_step(self, S, act):
        Agent.do_step(self, S, act)
        
        # Epsilon-greedy action selection
        if ranf() <= self.epsilon:
            # Choose a random action (0 or 1)
            A = randint(ACTION_COUNT)
        else:
            # Choose the best action for this state
            A = argmax(self.Q[S])
        
        # Observe reward and new state
        R, Sp = act(A)
        
        # max_a(Q(S', a))
        nextmax = 0 if Sp == TILE_GOAL else max(self.Q[Sp])
        
        # Update Q for this state/action pair
        self.Q[S][A] += self.alpha * (R + self.gamma * nextmax - self.Q[S][A])
