from Qlearning import *
import math

class Qlearning_LAO(Qlearning):
    def reset(self):
        Qlearning.reset(self)
        
        self.lastObs = -1
        self.lastAction = -1
        
    def init_Q(self):
        self.Q = zeros((STATE_COUNT * (STATE_COUNT + 1) * (ACTION_COUNT + 1),
                       ACTION_COUNT))
        
    def get_S(self, obs):
        """
        Returns the agent state, which is based on current and last state.
        """
        return (self.lastObs + 1) * STATE_COUNT * ACTION_COUNT \
               + (self.lastAction + 1) * STATE_COUNT \
               + obs
        
    def init_episode(self):
        Qlearning.init_episode(self)
        self.lastObs = -1
        self.lastAction = -1
        
    def do_step(self, S, act, logfile=None):
        Agent.do_step(self, S, act, logfile)
        
        # Observation -> agent state
        tempS = S
        S = self.get_S(S)
        self.lastObs = tempS
        
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
        
        # Observe reward and new observation
        R, Sp = act(A)
        self.lastAction = A
        
        # Update return
        self.G += R
        
        # max_a(Q(S', a))
        nextmax = 0 if Sp == TILE_GOAL else max(self.Q[self.get_S(Sp)])
        
        # Update Q for this state/action pair
        delta = R + self.gamma * nextmax - self.Q[S][A]
        self.Q[S][A] += self.alpha * delta
        
        if logfile:
            logfile.write("{}\n".format(abs(delta)))
        
        return Sp

    def init_info(self, master):
        # Cordon off parent info
        frame = Frame(master)
        frame["padx"] = 0
        frame["pady"] = 0
        frame.grid(row=0, columnspan=2)
        Qlearning.init_info(self, frame)
        
        # Last observation
        label = Label(master)
        label["text"] = "Last obs.:"
        label.grid(row=1, column=0)
        
        self.lastObs_var = StringVar()
        label = Label(master)
        label["textvariable"] = self.lastObs_var
        label["width"] = 8
        label.grid(row=1, column=1)
        
        # Last observation
        label = Label(master)
        label["text"] = "Last action:"
        label.grid(row=2, column=0)
        
        self.lastAction_var = StringVar()
        label = Label(master)
        label["textvariable"] = self.lastAction_var
        label["width"] = 8
        label.grid(row=2, column=1)

    def update_info(self):
        Qlearning.update_info(self)
        
        self.lastObs_var.set(self.lastObs)
        self.lastAction_var.set(self.lastAction)
