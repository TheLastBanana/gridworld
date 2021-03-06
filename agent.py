import random
from pylab import *
from tkinter import *

TILE_GOAL = 16

STATE_COUNT = 16
ACTION_COUNT = 4

class Agent():
    def __init__(self):
        """
        Initialize the learning agent.
        """
        self.reset()
        
    def reset(self):
        """
        Resets all agent data.
        """
        self.testmode = False
        self.run = 0
        self.episode = 0
        self.step = 0
        self.returnSum = 0
        self.G = 0
        self.init_Q()
        
    def init_Q(self):
        """
        Initialize Q values.
        """
        self.Q = zeros((STATE_COUNT, ACTION_COUNT), dtype=float)
        
    def get_Qs(self, S):
        """
        Returns Q values for the given OBSERVATION state.
        """
        return self.Q[self.get_S(S)]
        
    def get_S(self, obs):
        """
        Given the observation state, returns the agent state.
        """
        return obs
        
    def set_testmode(self, enabled):
        """
        Turn test mode on or off. When in test mode, the agent should:
        - Disable learning
        - Behave deterministically
        """
        self.testmode = enabled
        
    def init_run(self):
        """
        Resets all run data and starts a new run.
        Override this to reset data!
        """
        self.returnSum = 0
        self.run += 1
        self.episode = -1
        self.init_Q()
        self.init_episode()
    
    def init_episode(self):
        """
        Initializes an episode.
        """
        self.returnSum += self.G
        self.G = 0
        self.step = 0
        self.episode += 1

    def do_step(self, S, act, logfile=None):
        """
        Make the agent take a single step. The agent is given its current state
        and a function to call which takes an action and returns a pair of
        (reward, state).
        Possible actions are:
            0 = go right
            1 = go up
            2 = go left
            3 = go down
            
        This function should return the new state.
        Override this!
        """
        self.step += 1
        return S
        
    def init_options(self, master):
        """
        Override this to add options to the agent options panel.
        """
        pass
        
    def init_info(self, master):
        """
        Override this to add options to the agent info panel.
        """
        # Step
        label = Label(master)
        label["text"] = "Step:"
        label.grid(row=0, column=0)
        
        self.step_var = StringVar()
        label = Label(master)
        label["textvariable"] = self.step_var
        label["width"] = 8
        label.grid(row=0, column=1)
        
        # Episode
        label = Label(master)
        label["text"] = "Episode:"
        label.grid(row=1, column=0)
        
        self.episode_var = StringVar()
        label = Label(master)
        label["textvariable"] = self.episode_var
        label["width"] = 8
        label.grid(row=1, column=1)
        
        # Average return
        label = Label(master)
        label["text"] = "Avg return:"
        label.grid(row=2, column=0)
        
        self.avg_return_var = StringVar()
        label = Label(master)
        label["textvariable"] = self.avg_return_var
        label["width"] = 8
        label.grid(row=2, column=1)
        
    def update_info(self):
        """
        Override this to update the agent info panel.
        """
        self.step_var.set(self.step)
        self.episode_var.set(self.episode)
        
        if self.episode > 0:
            avgret = self.returnSum / self.episode
            self.avg_return_var.set("{:.3f}".format(avgret))
        else:
            self.avg_return_var.set("NaN")
