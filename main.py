from tkinter import *
from tkinter import simpledialog
from tkinter import filedialog
import pickle
import agent

from collections import namedtuple

DEFAULT_W = 16
DEFAULT_H = 16
DEFAULT_TILEW = 32
DEFAULT_TILEH = 32

TILE_WALL = -1
TILE_GOAL = 16

SavedWorld = namedtuple("SavedWorld", ["agentindex", "w", "h", "tiles"])

class ResizeDlg(simpledialog.Dialog):
    def __init__(self, master, w, h):
        # String variable inputs
        self.w = StringVar()
        self.w.set(w)
        
        self.h = StringVar()
        self.h.set(h)
        
        # Init
        master.title("Resize")
        simpledialog.Dialog.__init__(self, master)
    
    def body(self, master):
        label = Label(master)
        label["text"] = "Width:"
        label.grid(row=0, column=0)
        
        label = Label(master)
        label["text"] = "Height:"
        label.grid(row=1, column=0)
        
        self.wentry = Entry(master)
        self.wentry["textvariable"] = self.w
        self.wentry.grid(row=0, column=1)
        
        self.hentry = Entry(master)
        self.hentry["textvariable"] = self.h
        self.hentry.grid(row=1, column=1)
        
    def apply(self):
        w = int(self.w.get())
        h = int(self.h.get())
        self.result = w, h

class GridWorld(Tk):
    def __init__(self, w = DEFAULT_W, h = DEFAULT_H,
                 tileW = DEFAULT_TILEW, tileH = DEFAULT_TILEH):
        Tk.__init__(self)
        
        # Store whether mouse is currently creating or destroying walls
        self.makewall = True
        
        # Store whether the agent is being dragged
        self.dragagent = False
        
        # The agent's tile index
        self.agentindex = 0
        
        # Set up window
        self.title("GridWorld")
        self.bind("<Escape>", self._close)
        self.bind("<Control-s>", self.cmd_save)
        self.bind("<Control-o>", self.cmd_open)
        self.bind("<Control-r>", self.cmd_resize)
        
        # Set up menu bar
        self.menu = Menu(self)
        
        self.filemenu = Menu(self.menu,tearoff = 0)
        self.filemenu.add_command(label="Save", command=self.cmd_save)
        self.filemenu.add_command(label="Open", command=self.cmd_open)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        
        self.optmenu = Menu(self.menu, tearoff = 0)
        self.optmenu.add_command(label="Resize", command=self.cmd_resize)
        self.menu.add_cascade(label="Options", menu=self.optmenu)
        
        self.config(menu = self.menu)
        
        # Set up canvas
        self.w = w
        self.h = h
        self.tileW = tileW
        self.tileH = tileH
        self.canvas = Canvas(self)
        self.canvas["borderwidth"] = 1
        self.canvas["relief"] = RIDGE
        self.canvas.bind("<Button-1>", self._canv_lclick)
        self.canvas.bind("<B1-Motion>", self._canv_lmove)
        self.canvas.bind("<ButtonRelease-1>", self._canv_lrelease)
        self.canvas.bind("<Button-3>", self._canv_rclick)
        self.canvas.pack()
        
        test = Button(self)
        test.pack()
        
        self.resize(w, h)
    
    def get_state(self):
        """
        Gets the current state.
        """
        return self.tiles[agentindex]
    
    def sample(self, action):
        """
        Takes an action and returns (reward, state)
        Possible actions are:
            0 = go right
            1 = go up
            2 = go left
            3 = go down
        """
        x, y = _indextopos(self.agentindex)
        x += int(action == 0) - (action == 2)
        y += int(action == 3) - (action == 1)
        newindex = _postoindex(x, y)
        
        if not(x < 0 or y < 0 or x > self.w - 1 or y > self.h - 1
            or self.tiles[newindex] == TILE_WALL):
            
            self.agentindex = newindex
        
        newstate = self.get_state()
        return newstate, 1 if newstate == TILE_GOAL else 0
        
    def resize(self, w, h):
        """
        Resize the grid and add new tiles
        """
        self.w = w
        self.h = h
        self.agentindex = 0
        
        newW = self.w * self.tileW
        newH = self.h * self.tileH
        
        # Add tiles
        self.tiles = [0] * w * h
        for t in range(w * h):
            self._updt_tile(t)
        
        # Resize canvas
        self.canvas["width"] = newW
        self.canvas["height"] = newH
        self.canvas.pack()
        
        self.redraw()
        
    def redraw(self):
        """
        Redraw the canvas.
        """
        self.canvas.delete("all")
        cW = self.w * self.tileW
        cH = self.h * self.tileH
        
        # Horizontal lines
        for x in range(self.w):
            tileX = x * self.tileW
            self.canvas.create_line(tileX, 0, tileX, cH, fill="grey50")
        
        # Vertical lines
        for y in range(self.h):
            tileY = y * self.tileH
            self.canvas.create_line(0, tileY, cW, tileY, fill="grey50")
            
        # Tiles
        for t in range(self.w * self.h):
            x, y = self._indextopos(t)
            x *= self.tileW
            y *= self.tileH
            
            filled = False
            # Draw wall
            if self.tiles[t] == TILE_WALL:
                filled = True
                self.canvas.create_rectangle(x,
                                             y,
                                             x + self.tileW,
                                             y + self.tileH,
                                             fill="black")
            # Draw goal
            elif self.tiles[t] == TILE_GOAL:
                filled = True
                self.canvas.create_rectangle(x + 1,
                                             y + 1,
                                             x + self.tileW,
                                             y + self.tileH,
                                             fill="green",
                                             outline="green")
            
            # Draw agent
            if self.agentindex == t:
                self.canvas.create_oval(x + 3,
                                        y + 3,
                                        x + self.tileW - 2,
                                        y + self.tileH - 2,
                                        fill="red")
            
            # Draw tile number
            if not filled:
                self.canvas.create_text(x + self.tileW * 0.5,
                                        y + self.tileH * 0.5,
                                        text = "{}".format(self.tiles[t]))
            
        
    def cmd_resize(self, event=None):
        resize = ResizeDlg(self, self.w, self.h)
        
        # Resize is good to go
        if resize.result:
            w, h = resize.result
            self.resize(w, h)
            
    def cmd_save(self, event=None):
        opts = {}
        opts["defaultextension"] = ".gwd"
        opts["filetypes"] = [("GridWorlds", ".gwd")]
        opts["parent"] = self
        opts["initialdir"] = "./worlds"
        opts["title"] = "Save world"
        
        f = filedialog.asksaveasfile(mode="wb+", **opts)
        if not f: return
        
        world = SavedWorld(self.agentindex, self.w, self.h, self.tiles)
        pickle.dump(world, f)
        f.close()
        
    def cmd_open(self, event=None):
        opts = {}
        opts["defaultextension"] = ".gwd"
        opts["filetypes"] = [("GridWorlds", ".gwd")]
        opts["parent"] = self
        opts["initialdir"] = "./worlds"
        opts["title"] = "Load world"
        
        f = filedialog.askopenfile(mode="rb", **opts)
        if not f: return
        
        world = pickle.load(f)
        f.close()
        
        self.resize(world.w, world.h)
        self.tiles = world.tiles[:]
        for t in range(self.w * self.h):
            self._updt_tile(t)
        self.agentindex = world.agentindex
            
        self.redraw()
        
    def _postoindex(self, x, y):
        return x + y * self.w
        
    def _indextopos(self, index):
        return (index % self.w,
                index // self.w)
                
    def _screentotiles(self, x, y):
        return (x // self.tileW,
                y // self.tileH)
                
    def _tileneighbours(self, ind):
        x, y = self._indextopos(ind)
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
            
    def _tileblocked(self, x, y):
        ind = self._postoindex(x, y)
        
        if x < 0: return True
        if x > self.w - 1: return True
        if y < 0: return True
        if y > self.h - 1: return True
        if self.tiles[ind] == TILE_WALL: return True
        
        return False
        
    def _updt_tile(self, ind):
        if self.tiles[ind] == TILE_WALL or self.tiles[ind] == TILE_GOAL:
            return
        
        x, y = self._indextopos(ind)
        self.tiles[ind] = 1 * int(self._tileblocked(x, y - 1)) + \
                          2 * int(self._tileblocked(x - 1, y)) + \
                          4 * int(self._tileblocked(x + 1, y)) + \
                          8 * int(self._tileblocked(x, y + 1))
                          
    def _canv_lclick(self, event=None):
        """
        Called when the canvas is left-clicked.
        """
        pos = self._screentotiles(event.x, event.y)
        ind = self._postoindex(*pos)
        
        # Start dragging agent
        if self.agentindex == ind:
            self.dragagent = True
        
        # Start making walls
        self.makewall = self.tiles[ind] != TILE_WALL
        
        self._canv_lmove(event)
            
    def _canv_lmove(self, event=None):
        """
        Called when the canvas is left-clicked and the mouse moves.
        """
        x, y = self._screentotiles(event.x, event.y)
        if x < 0 or x > self.w - 1 or y < 0 or y > self.h - 1:
            return
        
        ind = self._postoindex(x, y)
        
        # Drag agent
        if self.dragagent:
            # Don't drag into wall
            if self.tiles[ind] != TILE_WALL:
                self.agentindex = ind
        
        # Draw walls
        else:
            # Can't draw over goal
            if self.tiles[ind] == TILE_GOAL or self.agentindex == ind:
                return
            
            # Make position a wall/empty
            self.tiles[ind] = TILE_WALL if self.makewall else 0
            
            # Update neighbouring tiles
            for t in self._tileneighbours(ind):
                self._updt_tile(t)
        
        # Redraw
        self.redraw()
        
    def _canv_lrelease(self, event=None):
        """
        Called when left-click is released on the canvas.
        """
        self.dragagent = False
        
    def _canv_rclick(self, event=None):
        """
        Called when the canvas is right-clicked.
        """
        pos = self._screentotiles(event.x, event.y)
        ind = self._postoindex(*pos)
        
        # Can't put goal in a wall
        if self.tiles[ind] == TILE_WALL:
            return
        
        # Make position a goal/not a goal
        if self.tiles[ind] == TILE_GOAL:
            self.tiles[ind] = 0
            self._updt_tile(ind)
        else:
            self.tiles[ind] = TILE_GOAL
        
        # Redraw
        self.redraw()
            
    def _close(self, event=None):
        self.destroy()
        
app = GridWorld()
app.mainloop()
