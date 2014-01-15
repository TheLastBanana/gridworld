import pickle
from collections import namedtuple

DEFAULT_W = 16
DEFAULT_H = 16

TILE_WALL = -1
TILE_GOAL = 16

SavedWorld = namedtuple("SavedWorld", ["agentstart", "w", "h", "tiles"])

class GridWorld():
    """
    A tile-based world with a single agent.
    """
    def __init__(self, w=DEFAULT_W, h=DEFAULT_W, goalcallback=None):
        self.resize(w, h)
        self.goalcallback = goalcallback
        
    def resize(self, w, h):
        """
        Resize the grid and add new tiles
        """
        self.w = w
        self.h = h
        self.agentindex = self.agentstart = 0
        
        # Add tiles
        self.tiles = [0] * w * h
        for t in range(w * h):
            self.updt_tile(t)
    
    def initworld(self):
        """
        Restart the world.
        """
        self.agentindex = self.agentstart
    
    def get_state(self):
        """
        Gets the current state.
        """
        return self.tiles[self.agentindex]
    
    def sample(self, action):
        """
        Takes an action and returns (reward, state)
        Possible actions are:
            0 = go right
            1 = go up
            2 = go left
            3 = go down
        """
        x, y = self.indextopos(self.agentindex)
        x += int(action == 0) - (action == 2)
        y += int(action == 3) - (action == 1)
        newindex = self.postoindex(x, y)
        
        if not(x < 0 or y < 0 or x > self.w - 1 or y > self.h - 1
            or self.tiles[newindex] == TILE_WALL):
            
            self.agentindex = newindex
        
        newstate = self.get_state()
        
        # We've reached the goal!
        if newstate == TILE_GOAL:
            if self.goalcallback: self.goalcallback()
        
        return newstate, 1 if newstate == TILE_GOAL else 0
        
    def postoindex(self, x, y):
        """
        Converts a position to a tile index.
        """
        return x + y * self.w
        
    def indextopos(self, index):
        """
        Converts a tile index to a position.
        """
        return (index % self.w,
                index // self.w)
   
    def tileneighbours(self, ind):
        x, y = self.indextopos(ind)
        tiles = [ind]
        
        if x > 0:
            tiles.append(ind - 1)
            if y > 0: tiles.append(ind - self.w - 1)
            if y < self.h - 1: tiles.append(ind + self.w - 1)
        
        if x < self.w - 1:
            tiles.append(ind + 1)
            if y > 0: tiles.append(ind - self.w + 1)
            if y < self.h - 1: tiles.append(ind + self.w + 1)
                
        if y > 0: tiles.append(ind - self.w)
        
        if y < self.h - 1: tiles.append(ind + self.w)
        
        return tiles
            
    def tileblocked(self, x, y):
        """
        Returns True if a tile is either a wall or invalid, else False.
        """
        ind = self.postoindex(x, y)
        
        if x < 0: return True
        if x > self.w - 1: return True
        if y < 0: return True
        if y > self.h - 1: return True
        if self.tiles[ind] == TILE_WALL: return True
        
        return False
        
    def updt_tile(self, ind):
        """
        Updates a tile's value.
        """
        if self.tiles[ind] == TILE_WALL or self.tiles[ind] == TILE_GOAL:
            return
        
        x, y = self.indextopos(ind)
        self.tiles[ind] = 1 * int(self.tileblocked(x, y - 1)) + \
                          2 * int(self.tileblocked(x - 1, y)) + \
                          4 * int(self.tileblocked(x + 1, y)) + \
                          8 * int(self.tileblocked(x, y + 1))

    def save(self, filename):
        """
        Saves the gridworld to a given filename.
        """
        world = SavedWorld(self.agentstart,
                           self.w,
                           self.h,
                           self.tiles)
                           
        with open(filename, "wb+") as f:
            pickle.dump(world, f)
        
    def load(self, filename):
        """
        Loads the gridworld from a given filename.
        """
        for t in range(self.w * self.h):
            self.updt_tile(t)
            
        with open(filename, "rb") as f:
            world = pickle.load(f)
            
            self.agentstart = world.agentstart
            self.w = world.w
            self.h = world.h
            self.tiles = world.tiles[:]