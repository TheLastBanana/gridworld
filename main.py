from tkinter import *
from tkinter import simpledialog
from tkinter import filedialog
import agent, Qlearning
import gridworld
import math

DEFAULT_TILEW = 32
DEFAULT_TILEH = 32

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

class GUI(Tk):
    def __init__(self, w = gridworld.DEFAULT_W, h = gridworld.DEFAULT_H,
                 tileW = DEFAULT_TILEW, tileH = DEFAULT_TILEH):
        Tk.__init__(self)
        
        # The current agent type
        self.agent = Qlearning.Qlearning()#agent.Agent()
        
        # Store whether mouse is currently creating or destroying walls
        self.makewall = True
        
        # Store whether the agent is being dragged
        self.dragagent = False
        
        # ID of the running agent alarm
        self.agentalarm = None
        
        # How often the agent makes a step (in milliseconds)
        self.agentrate = 1
        
        # Whether the simulation has been started yet
        self.running = False
        
        # Whether the agent will be starting a new episode next step.
        self.new_episode = False
        
        # The currently-hovered tile
        self.cur_index = -1
        
        # The grid world
        self.gw = gridworld.GridWorld()
        
        # Set up window
        self.title("GridWorld")
        self.bind("<Escape>", self._close)
        self.bind("<Control-s>", self.cmd_save)
        self.bind("<Control-o>", self.cmd_open)
        self.bind("<Control-r>", self.cmd_resize)
        self.bind("<space>", self.cmd_runpause)
        self.bind("<r>", self.cmd_reset)
        
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
        self.gw.w = w
        self.gw.h = h
        self.tileW = tileW
        self.tileH = tileH
        self.canvas = Canvas(self)
        self.canvas["borderwidth"] = 1
        self.canvas["relief"] = RIDGE
        self.canvas.bind("<Button-1>", self._canv_lclick)
        self.canvas.bind("<B1-Motion>", self._canv_lmove)
        self.canvas.bind("<ButtonRelease-1>", self._canv_lrelease)
        self.canvas.bind("<Button-3>", self._canv_rclick)
        self.canvas.bind("<Motion>", self._canv_move)
        self.canvas.grid(row=0, column=1, columnspan=3)
        
        # Set up info panel
        self.info_panel = LabelFrame(self)
        self.info_panel["text"] = "Information"
        self.info_panel["padx"] = 10
        self.info_panel["pady"] = 10
        self.info_panel.grid(row=0, column=0, rowspan=3)
        
        # Set up action weight display
        # Right
        label = Label(self.info_panel)
        label["text"] = "Right:"
        label.grid(row=0, column=0)
        
        self.q_right = StringVar()
        label = Label(self.info_panel)
        label["textvariable"] = self.q_right
        label.grid(row=0, column=1)
        
        # Up
        label = Label(self.info_panel)
        label["text"] = "Up:"
        label.grid(row=1, column=0)
        
        self.q_up = StringVar()
        label = Label(self.info_panel)
        label["textvariable"] = self.q_up
        label.grid(row=1, column=1)
        
        # Left
        label = Label(self.info_panel)
        label["text"] = "Left:"
        label.grid(row=2, column=0)
        
        self.q_left = StringVar()
        label = Label(self.info_panel)
        label["textvariable"] = self.q_left
        label.grid(row=2, column=1)
        
        # Down
        label = Label(self.info_panel)
        label["text"] = "Down:"
        label.grid(row=3, column=0)
        
        self.q_down = StringVar()
        label = Label(self.info_panel)
        label["textvariable"] = self.q_down
        label.grid(row=3, column=1)
        
        self.update_tileinfo()
        
        # Set up checkboxes
        self.rand_start = BooleanVar()
        cbtn = Checkbutton(self)
        cbtn["text"] = "Random start"
        cbtn["variable"] = self.rand_start
        cbtn["command"] = self.cmd_togglerand
        cbtn.grid(row=1, column=1)
        
        self.show_nums = BooleanVar()
        self.show_nums.set(False)
        cbtn = Checkbutton(self)
        cbtn["text"] = "Show numbers"
        cbtn["variable"] = self.show_nums
        cbtn["command"] = self.redraw
        cbtn.grid(row=2, column=1)
        
        self.show_weights = BooleanVar()
        self.show_weights.set(True)
        cbtn = Checkbutton(self)
        cbtn["text"] = "Show weights"
        cbtn["variable"] = self.show_weights
        cbtn["command"] = self.redraw
        cbtn.grid(row=3, column=1)
        
        # Set up buttons
        self.run_btn = Button(self)
        self.run_btn["command"] = self.cmd_runpause
        self.run_btn["width"] = 7
        self.run_btn.grid(row=1, column=2)
        
        self.reset_btn = Button(self)
        self.reset_btn["text"] = "Reset"
        self.reset_btn["command"] = self.cmd_reset
        self.reset_btn["width"] = 7
        self.reset_btn.grid(row=2, column=2)
        
        self.update_buttons()
        
        # Set up rate scale
        self.rate_scl = Scale(self)
        self.rate_scl["from"] = 0
        self.rate_scl["to"] = 3
        self.rate_scl["resolution"] = -1
        self.rate_scl["orient"] = HORIZONTAL
        self.rate_scl["length"] = 200
        self.rate_scl["showvalue"] = 0
        self.rate_scl["command"] = self.update_rate
        self.rate_scl.grid(row=2, column=3)
        
        self.rate_text = Label(self)
        self.rate_text.grid(row=1, column=3)
        self.update_rate()
        
        # Set up agent options
        self.agent_opts = LabelFrame(self)
        self.agent_opts["text"] = "Agent options"
        self.agent_opts["padx"] = 10
        self.agent_opts["pady"] = 10
        self.agent_opts.grid(row=0, column=5, rowspan=3)
        self.agent.init_options(self.agent_opts)
        
        self.resize(w, h)
        
    def resize(self, w, h, resize_gw=True):
        """
        Resize the grid and add new tiles
        """
        if resize_gw:
            self.gw.resize(w, h)
            self.rand_start.set(self.gw.agentstart == -1)
        
        newW = self.gw.w * self.tileW
        newH = self.gw.h * self.tileH
        
        # Resize canvas
        self.canvas["width"] = newW
        self.canvas["height"] = newH
        
        self.redraw()
        
    def redraw(self, event=None):
        """
        Redraw the canvas.
        """
        self.canvas.delete("all")
        cW = self.gw.w * self.tileW
        cH = self.gw.h * self.tileH
            
        # Tiles
        for t in range(self.gw.w * self.gw.h):
            x, y = self.gw.indextopos(t)
            x *= self.tileW
            y *= self.tileH
            
            filled = False
            # Draw wall
            if self.gw.tiles[t] == gridworld.TILE_WALL:
                filled = True
                self.canvas.create_rectangle(x + 1,
                                             y + 1,
                                             x + self.tileW,
                                             y + self.tileH,
                                             fill="black")
            # Draw goal
            elif self.gw.tiles[t] == gridworld.TILE_GOAL:
                filled = True
                self.canvas.create_rectangle(x + 1,
                                             y + 1,
                                             x + self.tileW,
                                             y + self.tileH,
                                             fill="green",
                                             outline="green")
            elif self.gw.agentstart == t:
                self.canvas.create_rectangle(x + 1,
                                             y + 1,
                                             x + self.tileW,
                                             y + self.tileH,
                                             fill="yellow",
                                             outline="yellow")
            
            # Draw agent
            if self.gw.agentindex == t:
                self.canvas.create_oval(x + 3,
                                        y + 3,
                                        x + self.tileW - 2,
                                        y + self.tileH - 2,
                                        fill="red")
            
            # Draw tile insides
            if not filled:
                midX = x + self.tileW * 0.5
                midY = y + self.tileH * 0.5
                
                if self.show_weights.get():
                    S = self.gw.tiles[t]
                    minQ = min(self.agent.Q[S])
                    
                    maxlen = minQ + max(self.agent.Q[S])
                    if maxlen > 0:
                        # Draw action weights
                        for A in range(agent.ACTION_COUNT):
                            ang = A * math.pi * 0.5
                            l = (minQ + self.agent.Q[S][A]) / maxlen
                            arrow = NONE if l < 1 else LAST
                            
                            l *= min(self.tileW, self.tileH) * 0.5
                            lX = l * math.cos(ang)
                            lY = -l * math.sin(ang)
                            
                            self.canvas.create_line(midX,
                                                    midY,
                                                    midX + lX,
                                                    midY + lY,
                                                    arrow=arrow,
                                                    arrowshape=(6,8,3))
                
                # Draw number
                if self.show_nums.get():
                    self.canvas.create_text(midX,
                                            midY,
                                            text = "{}".format(self.gw.tiles[t]))
        
        # Horizontal lines
        for x in range(self.gw.w):
            tileX = x * self.tileW
            self.canvas.create_line(tileX, 0, tileX, cH, fill="grey50")
        
        # Vertical lines
        for y in range(self.gw.h):
            tileY = y * self.tileH
            self.canvas.create_line(0, tileY, cW, tileY, fill="grey50")
    
    def update_buttons(self):
        self.run_btn["text"] = "Pause" if self.agentalarm else "Run"
        self.reset_btn["state"] = NORMAL if self.running else DISABLED
            
    def update_rate(self, event=None):
        self.agentrate = int(10 ** self.rate_scl.get())
        self.rate_text["text"] = "Rate: {:d} ms/step".format(self.agentrate)
        
    def update_tileinfo(self):
        right = 0.0
        up = 0.0
        left = 0.0
        down = 0.0
        
        if self.cur_index >= 0:
            tile = self.gw.tiles[self.cur_index]
            if tile >= 0 and tile < agent.STATE_COUNT:
                right, up, left, down = self.agent.Q[tile]
        
        fmt = "{:.3f}"
        self.q_right.set(fmt.format(right))
        self.q_up.set(fmt.format(up))
        self.q_left.set(fmt.format(left))
        self.q_down.set(fmt.format(down))
        
    def cmd_togglerand(self, event=None):
        if self.rand_start.get():
            self.gw.agentstart = -1
        else:
            self.gw.agentstart = self.gw.agentindex
            
        self.redraw()
    
    def cmd_runpause(self, event=None):
        # If there's an alarm running, pause
        if self.agentalarm:
            self.pause()
        else:
            self.resume()
            
    def cmd_reset(self, event=None):
        if not self.running: return
        
        # Reset the agent
        self.agent.reset()
        self.gw.initworld()
        
        # Stop the agent from running
        self.pause()
        self.running = False
        
        self.redraw()
        self.update_buttons()
    
    def cmd_resize(self, event=None):
        resize = ResizeDlg(self, self.gw.w, self.gw.h)
        
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
        
        f = filedialog.asksaveasfilename(**opts)
        if not f: return
        
        self.gw.save(f)
        
    def cmd_open(self, event=None):
        opts = {}
        opts["defaultextension"] = ".gwd"
        opts["filetypes"] = [("GridWorlds", ".gwd")]
        opts["parent"] = self
        opts["initialdir"] = "./worlds"
        opts["title"] = "Load world"
        
        f = filedialog.askopenfilename(**opts)
        if not f: return
        
        self.gw.load(f)
        self.rand_start.set(self.gw.agentstart == -1)
        self.resize(self.gw.w, self.gw.h, False)
            
        self.redraw()
        
    def step_agent(self):
        """
        Make the agent take one step.
        """
        # Start a new episode
        if self.gw.tiles[self.gw.agentindex] == agent.TILE_GOAL:
            self.gw.initworld()
            self.agent.init_episode()
            self.new_episode = False
        
        self.agent.do_step(self.gw.get_state(), self.gw.sample)
        self.redraw()
        
        self.update_tileinfo()
        
        self.agentalarm = self.after(self.agentrate, self.step_agent)
        
    def resume(self):
        """
        Resume the simulation.
        """
        # Set a new alarm
        self.agentalarm = self.after(self.agentrate, self.step_agent)
        self.running = True
        
        self.update_buttons()
        
    def pause(self):
        """
        Pause the simulation.
        """
        if not self.agentalarm:
            return
        
        self.after_cancel(self.agentalarm)
        self.agentalarm = None
        
        self.update_buttons()
                
    def _screentotiles(self, x, y):
        return (x // self.tileW,
                y // self.tileH)
                          
    def _canv_lclick(self, event=None):
        """
        Called when the canvas is left-clicked.
        """
        x, y = self._screentotiles(event.x, event.y)
        if not self.gw.validpos(x, y): return
        
        ind = self.gw.postoindex(x, y)
        
        # Start dragging agent
        if self.gw.agentindex == ind:
            self.dragagent = True
        
        # Start making walls
        self.makewall = self.gw.tiles[ind] != gridworld.TILE_WALL
        
        self._canv_lmove(event)
            
    def _canv_lmove(self, event=None):
        """
        Called when the canvas is left-clicked and the mouse moves.
        """
        x, y = self._screentotiles(event.x, event.y)
        if not self.gw.validpos(x, y): return
        
        ind = self.gw.postoindex(x, y)
        
        # Drag agent
        if self.dragagent:
            # Don't drag into wall
            if self.gw.tiles[ind] != gridworld.TILE_WALL:
                self.gw.agentindex = ind
                if not self.running and not self.rand_start.get():
                    self.gw.agentstart = ind
        
        # Draw walls
        else:
            # Can't draw over goal
            if self.gw.tiles[ind] == gridworld.TILE_GOAL or \
                self.gw.agentindex == ind or self.gw.agentstart == ind:
                return
            
            # Make position a wall/empty
            self.gw.tiles[ind] = gridworld.TILE_WALL if self.makewall else 0
            
            # Update neighbouring tiles
            for t in self.gw.tileneighbours(ind):
                self.gw.updt_tile(t)
        
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
        ind = self.gw.postoindex(*pos)
        
        # Can't put goal in a wall
        if self.gw.tiles[ind] == gridworld.TILE_WALL:
            return
        
        # Make position a goal/not a goal
        if self.gw.tiles[ind] == gridworld.TILE_GOAL:
            self.gw.tiles[ind] = 0
            self.gw.updt_tile(ind)
        else:
            self.gw.tiles[ind] = gridworld.TILE_GOAL
        
        # Redraw
        self.redraw()
        
    def _canv_move(self, event=None):
        """
        Called when the mouse moves on the canvas.
        """
        self.cur_index = -1
        
        if event:
            x, y = self._screentotiles(event.x, event.y)
            if self.gw.validpos(x, y):
                self.cur_index = min(self.gw.postoindex(x, y),
                                     len(self.gw.tiles))
            
    def _close(self, event=None):
        self.destroy()
        
app = GUI()
app.mainloop()
