#Lucas 14 Dec 2022

import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog as fd
import pynput.keyboard as keyboard #Listener, Button, Controller
import pynput.mouse as mouse #Listener, Button, Controller
import time as t
import os
import random as rand

'''
TODO LIST
- make all entry/spinbox/combobox update to not allow bad input
- use self.intbounds in Macro
- separate logic + gui ?
- fix gui css
- use tk filedialog to add alerts
- improve marker canvas (make text labels show up anywhere, make dimensions bigger to fit everything?)
- USE A LISTENER FOR EXECUTION HOTKEYS!!
'''

'''
MARKER
generic object for marking a location on the screen for coordinate-based commands
'''
class Marker:
    def __init__(self, x, y, name):
        #marker coordinates
        self.x = int(x)
        self.y = int(y)
        #name will increment (Marker 1, Marker 2, Marker 3, ...)
        #but that will be controlled by Macro
        self.name = name
        self.color = self.get_rand_color() #fill color for canvas

    def save(self, x, y, name):
        self.x = int(x)
        self.y = int(y)
        self.name = str(name)

    def get_rand_color(self): #return a random color string in the form #RRGGBB
        num = rand.randint(0, 16777215)
        num = hex(num)
        while len(num[2:]) < 6:
            num = num + "0"
        return "#" + num[2:]

'''
COMMAND
generic class for command objects
'''
class Command:
    def __init__(self, name, vals, dict, typestr):
        self.name = str(name) #identification var
        self.vals = vals #values to use to run (dynamic size, based on command)
        self.intbounds = [1, 100] #bounds for commands that use int values (i.e. hold for n seconds)
        self.dict = dict #"n" = no dictionary, "k" = keydict, "m" = markerdict
        self.type = typestr
        self.valid = False

    def save(self, vals):
        self.vals = vals

    def checkintbounds(self, val): #makes sure that int vals are between bounds
        if val < self.intbounds[0]:
            val = self.intbounds[0]
        if val > self.intbounds[1]:
            val = self.intbounds[1]

    def getexectime(self):
        return 0 #this will be inherited by commands that take time to run
    
    def label(self): #for listbox
        return self.name + ", " + str(self.vals)
'''
CLICK
name = "Click"
vals[0] = string to click
vals[1] = (int) how many times to click
'''
class Click(Command):
    def __init__(self):
        Command.__init__(self, "Click", [None, None], "k", "Button")
        #we need both controllers bc the user can click keys or mouse buttons
        self.key = keyboard.Controller()
        self.mouse = mouse.Controller()

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        v1 = str(self.vals[1]) if not(self.vals[1] == None) else "__"
        return "click [" + v0 + "] " + v1 + " times"

    def save(self, vals): #returns true if successful, false otherwise
        key = vals[0]
        repeat = vals[1]

        self.checkintbounds(repeat) #check bounds
        self.valid = True #once valid inputs have been given, it can run

        self.vals = [key, repeat]
        return True #the entry widgets are pretty much impossible to mess up

    def run(self, keydict):
        for i in range(0, self.vals[1]): #repeat n times
            if self.vals[0] == "lmb" or self.vals[0] == "rmb" or self.vals[0] == "mmb": #mouse buttons
                self.mouse.click(keydict[self.vals[0]])
            else: #keyboard buttons
                self.key.tap(keydict[self.vals[0]])

'''
HOLD
name = "Hold"
vals[0] = string  to hold
vals[1] = how long (sec) to hold it
'''
class Hold(Command):
    def __init__(self):
        Command.__init__(self, "Hold", [None, None], "k", "Button")
        self.key = keyboard.Controller()
        self.mouse = mouse.Controller()

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        v1 = str(self.vals[1]) if not(self.vals[1] == None) else "__"
        return "hold [" + v0 + "] for " + v1 + " seconds"

    def save(self, vals): #returns true if successful, false otherwise
        key = vals[0]
        time = vals[1]

        self.checkintbounds(time) #check bounds
        self.valid = True

        self.vals = [key, time]
        return True
    
    def getexectime(self):
        return self.vals[1] #execution time is the time to hold down the button

    def run(self, keydict): #hold = press, sleep, release
        if self.vals[0] == "lmb" or self.vals[0] == "rmb" or self.vals[0] == "mmb": #mouse buttons
            self.mouse.press(keydict[self.vals[0]])
            t.sleep(self.vals[1])
            self.mouse.release(keydict[self.vals[0]])
        else: #keyboard buttons
            self.key.press(keydict[self.vals[0]])
            t.sleep(self.vals[1])
            self.key.release(keydict[self.vals[0]])
'''
PRESS 
name = "Press"
vals[0] = string  to press
'''
class Press(Command):
    def __init__(self):
        Command.__init__(self, "Press", [None], "k", "Button")
        self.key = keyboard.Controller()
        self.mouse = mouse.Controller()

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        return "press [" + v0 + "]"

    def save(self, vals):
        key = vals[0]

        self.vals = [key]
        self.valid = True

        return True

    def run(self, keydict):
        if self.vals[0] == "lmb" or self.vals[0] == "rmb" or self.vals[0] == "mmb": #mouse button
            self.mouse.press(keydict[self.vals[0]])
        else: #keyboard button
            self.key.press(keydict[self.vals[0]])
'''
RELEASE 
name = "Release"
vals[0] = string  to release
'''
class Release(Command):
    def __init__(self):
        Command.__init__(self, "Release", [None], "k", "Button")
        self.key = keyboard.Controller()
        self.mouse = mouse.Controller()

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        return "release [" + v0 + "]"

    def save(self, vals):
        key = vals[0]

        self.vals = [key]
        self.valid = True

        return True

    def run(self, keydict):
        if self.vals[0] == "lmb" or self.vals[0] == "rmb" or self.vals[0] == "mmb": #mouse button
            self.mouse.release(keydict[self.vals[0]])
        else: #keyboard
            self.key.release(keydict[self.vals[0]])
'''
TYPE
name = "Type"
vals[0] = string (1+ character) to type
'''
class Type(Command):
    def __init__(self):
        Command.__init__(self, "Type", [None], "n", "Button")
        self.controller = keyboard.Controller() #you cant type mouse buttons, so we just need keyboard

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        return "type " + v0

    def save(self, vals):
        string = vals[0]

        self.vals = [string]
        self.valid = True
        return True

    def run(self):
        self.controller.type(self.vals[0])
'''
MOVE MOUSE
name = "Move Mouse"
vals[0] = name of marker to move to
'''
class MoveMouse(Command):
    def __init__(self):
        Command.__init__(self, "Move Mouse", [None], "m", "Mouse")
        self.controller = mouse.Controller()

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        return "move mouse to " + v0

    def save(self, vals):
        m = vals[0]

        self.valid = True
        self.vals = [m]
        return True

    def run(self, mdict):
        m = mdict[self.vals[0]] #get the marker
        x = m.x
        y = m.y

        self.controller.position = (x, y) #manually set position of mouse

'''
DRAG MOUSE
name = "Drag Mouse"
val[0] = name of marker to drag mouse to
'''
class DragMouse(Command):
    def __init__(self):
        Command.__init__(self, "Drag Mouse", [None], "m", "Mouse")
        self.controller = mouse.Controller()
        self.time = 1 #how many seconds to drag before completion
        self.frames = 40 #how many frames in the drag animation (im treating this as an animation)

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        return "drag mouse to " + v0

    def save(self, vals):
        m = vals[0]

        self.valid = True
        self.vals = [m]
        return True

    def getexectime(self):
        return self.time #drag always takes 1 second

    def run(self, mdict):
        interval = self.time/self.frames

        #get old and new pos
        oldx = self.controller.position[0]
        oldy = self.controller.position[1]

        m = mdict[self.vals[0]] #get new pos from marker
        newx = m.x
        newy = m.y

        #keep track of current mouse pos
        x = oldx
        y = oldy

        '''
        finish the drag in 1 second (40 frames * 0.025 second interval)
        so we need to calculate how many pixels to move per 0.025 second for 40 frames
        '''
        dx = (oldx - newx) / self.frames
        dy = (oldy - newy) / self.frames

        #start the drag by holding down lmb
        self.controller.press(mouse.Button.left) #left moues button to drag

        for i in range(0, self.frames):
            x -= dx #im not gonna lie, idk why im subtracting, it just kinda works yk
            y -= dy
            self.controller.position = (x, y) #move the mouse
            t.sleep(interval)
        
        #snap to actual position
        self.controller.position = (newx, newy)

        #finally, release the drag
        self.controller.release(mouse.Button.left)
        
'''
SCROLL MOUSE (equivalent to 2-finger movement on touchpad)
vals[0] = amount of steps (int)
vals[1] = direction (up, right, down, left)
'''
class Scroll(Command):
    def __init__(self):
        Command.__init__(self, "Scroll Mouse", [None, None], "n", "Mouse")
        self.controller = mouse.Controller()

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        v1 = str(self.vals[1]) if not(self.vals[1] == None) else "__"
        return "scroll mouse " + v0 + " steps " + v1

    def save(self, vals):
        steps = vals[0]
        direction = vals[1]

        self.checkintbounds(steps)
        self.valid = True

        self.vals = [int(steps), direction]
        return True

    def run(self):
        '''
        scroll(dx, dy)

        negative <--- dx ----> positive

                positive
                    ^
                    |
                    |
                    dy
                    |
                    |
                    v
                negative
        '''
        s = self.vals[0]
        d = self.vals[1]

        if d == "up":
            self.controller.scroll(0, s)
        elif d == "down":
            self.controller.scroll(0, -s)
        elif d == "right":
            self.controller.scroll(s, 0)
        elif d == "left":
            self.controller.scroll(-s, 0)

'''
SLEEP
vals[0] = sec to sleep
'''
class Sleep(Command):
    def __init__(self):
        Command.__init__(self, "Sleep", [None], "n", "Other")

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        return "sleep for " + v0 + " seconds"

    def save(self, vals):
        sec = vals[0]

        self.valid = True
        self.checkintbounds(sec) #check int bounds

        self.vals = [float(sec)]
        return True
    
    def getexectime(self):
        return self.vals[0] #execution time is whatever the amount the user inputs

    def run(self):
        t.sleep(self.vals[0]) #easy peasy

'''
REPEAT
vals[0] = how many times to repeat
vals[1] = how many lines after to repeat
'''
class Repeat(Command):
    def __init__(self):
        Command.__init__(self, "Repeat", [None, None], "n", "Other")

    def label(self):
        v0 = str(self.vals[0]) if not(self.vals[0] == None) else "__"
        v1 = str(self.vals[1]) if not(self.vals[1] == None) else "__"
        return "repeat next " + v1 + " lines " + v0 + " times"

    def save(self, vals):
        rep = vals[0]
        lines = vals[1]

        self.checkintbounds(rep) #check int bounds
        self.checkintbounds(lines)
        self.valid = True

        self.vals = [int(rep), int(lines)]
        return True
    
    def getexectime(self):
        return 0 #doesnt really matter, not part of runlist

    def run(self, lines):
        for i in range(0, self.vals[0]):
            for j in lines:
                j.run()

'''
MACRO
tkinter application to simulate user inputs with pynput (keyboard/mouse)
'''
class Macro:
    def __init__(self):
        self.commands = [] #list of commands to execute
        self.curr = None #keep track of the index of our current stock
        self.mcurr = None #silly little pun because its marker curr
        self.clipboard = [] #keeps track of all objects on clipboard
        self.mclipboard = []
        self.intbounds = (0, 100)

        self.title = "Macro Editor" #name of application
        self.wait = 0.5 #seconds in-between each command
        self.hotkey = None #run program when this hotkey is pressed
        self.mh = "space" #add a marker when this hotkey is pressed and the marker tab is active
        self.vals = [] #this will transfer gui info to commands
        self.markers = [] #keep track of all available marker

        self.root = tk.Tk() # Create a window
        self.root.title(self.title)
        self.root.geometry("800x800+200+50")
        self.root.resizable(width=False, height=False)

        #dimensions of screen
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        #set up grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        #any key that can be pressed without holding shift / toggling caps lock
        no_shift = [39] + [x for x in range(44, 58)] + [59, 61, 91, 92, 93, 96] + [x for x in range(97, 123)] #see comment block in self.unshift()

        #converts the name of the character in the GUI to the character to press in the pynput functions
        self.keydict = {chr(x):chr(x) for x in no_shift} # character name : character

        #now add the others
        self.keydict["space"] = " "
        self.keydict["bs"] = keyboard.Key.backspace
        self.keydict["caps"] = keyboard.Key.caps_lock
        self.keydict["cmd"] = keyboard.Key.cmd
        self.keydict["ctrl"] = keyboard.Key.ctrl
        self.keydict["enter"] = keyboard.Key.enter
        self.keydict["esc"] = keyboard.Key.esc
        self.keydict["shift"] = keyboard.Key.shift
        self.keydict["tab"] = keyboard.Key.tab
        self.keydict["lmb"] = mouse.Button.left
        self.keydict["rmb"] = mouse.Button.right
        self.keydict["mmb"] = mouse.Button.middle

        self.keys = [] #current keys pressed

        #alphanumeric button handler
        self.root.bind("<KeyPress>", self.handle_key_press)
        self.root.bind("<KeyRelease>", self.handle_key_release)

        #other buttons (key.char == "", so we use key.keysym to get key symbol)

        #press
        self.root.bind("<KeyPress-space>", lambda key : self.handle_other_key_press("space"))
        self.root.bind("<KeyPress-Meta_R>", lambda key : self.handle_other_key_press("cmd"))
        self.root.bind("<KeyPress-Meta_L>", lambda key : self.handle_other_key_press("cmd"))
        self.root.bind("<KeyPress-Meta_R>", lambda key : self.handle_other_key_press("cmd"))
        self.root.bind("<KeyPress-Control_L>", lambda key : self.handle_other_key_press("ctrl"))
        self.root.bind("<KeyPress-Control_R>", lambda key : self.handle_other_key_press("ctrl"))
        self.root.bind("<KeyPress-Shift_L>", lambda key : self.handle_other_key_press("shift"))
        self.root.bind("<KeyPress-Shift_R>", lambda key : self.handle_other_key_press("shift"))
        self.root.bind("<KeyPress-Tab>", lambda key : self.handle_other_key_press("tab"))
        self.root.bind("<KeyPress-Caps_Lock>", lambda key : self.handle_other_key_press("caps"))
        self.root.bind("<KeyPress-Escape>", lambda key : self.handle_other_key_press("esc"))
        self.root.bind("<KeyPress-Return>", lambda key : self.handle_other_key_press("enter"))
        self.root.bind("<KeyPress-BackSpace>", lambda key : self.handle_other_key_press("bs"))

        #release
        self.root.bind("<KeyRelease-space>", lambda key : self.handle_other_key_release("space"))
        self.root.bind("<KeyRelease-Meta_L>", lambda key : self.handle_other_key_release("cmd"))
        self.root.bind("<KeyRelease-Meta_R>", lambda key : self.handle_other_key_release("cmd"))
        self.root.bind("<KeyRelease-Control_L>", lambda key : self.handle_other_key_release("ctrl"))
        self.root.bind("<KeyRelease-Control_R>", lambda key : self.handle_other_key_release("ctrl"))
        self.root.bind("<KeyRelease-Shift_L>", lambda key : self.handle_other_key_release("shift"))
        self.root.bind("<KeyRelease-Shift_R>", lambda key : self.handle_other_key_release("shift"))
        self.root.bind("<KeyRelease-Tab>", lambda key : self.handle_other_key_release("tab"))
        self.root.bind("<KeyRelease-Caps_Lock>", lambda key : self.handle_other_key_release("caps"))
        self.root.bind("<KeyRelease-Escape>", lambda key : self.handle_other_key_release("esc"))
        self.root.bind("<KeyRelease-Return>", lambda key : self.handle_other_key_release("enter"))
        self.root.bind("<KeyRelease-BackSpace>", lambda key : self.handle_other_key_release("bs"))

        #make the notebook for different tabs
        self.notebook = Notebook(self.root, height=700)
        self.notebook.grid(sticky="NESW")

        #make the frames for the tab container
        self.program_tab()
        self.marker_tab()
        self.history_tab()

        #make the menu widgets
        self.menu()

        # listener for mouse
        mouselistener = mouse.Listener(on_move=self.update_mouse)
        mouselistener.start()

        #start the main loop
        self.root.mainloop()

        #stop thread after loop closes
        mouselistener.stop()

    def program_tab(self): #the main page of the notebook widget
        tab = Frame(self.notebook)
        tab.grid()

        #set up grid
        tab.rowconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        tab.rowconfigure(2, weight=1)
        tab.rowconfigure(3, weight=2)
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=2)

        self.inlistbox = False #keep track of when the cursor is in the listbox and can select things

        #listbox
        self.list = tk.Listbox(tab, selectmode=tk.EXTENDED)
        self.list.grid(row=0, rowspan=4, column=0, sticky="NSEW", padx=5, pady=5)
        self.list.bind("<<ListboxSelect>>", self.listbox_programselect)
        self.list.bind("<Enter>", self.listbox_toggle)
        self.list.bind("<Leave>", self.listbox_toggle)

        #for metrics relating to inputs and commands
        metricframe = LabelFrame(tab, text="Metrics", width=50)
        metricframe.grid(row=0, column=1, sticky="NESW", padx=5, pady=5)
        metricframe.grid_propagate(False)

        #3x3 grid
        metricframe.rowconfigure(0, weight=1)
        metricframe.rowconfigure(1, weight=1)
        metricframe.rowconfigure(2, weight=1)
        metricframe.columnconfigure(0, weight=1)
        metricframe.columnconfigure(1, weight=1)
        metricframe.columnconfigure(2, weight=1)

        #dynamic text label 1
        self.keyvar = tk.StringVar()
        self.keyvar.set("Keys Pressed: ")

        keylabel = Label(metricframe, textvariable=self.keyvar, width=50)
        keylabel.grid(row=0, column=0)

        #dynamic text label 2
        self.mousevar = tk.StringVar()
        self.mousevar.set("Mouse Position: (0,0)")

        mouselabel = Label(metricframe, textvariable=self.mousevar, width=50)
        mouselabel.grid(row=1, column=0)

        #dynamic text label 3
        self.exectime = tk.StringVar()
        self.exectime.set("Execution Time: 0s")

        exectimelabel = Label(metricframe, textvariable=self.exectime, width=50)
        exectimelabel.grid(row=2, column=0)

        #for managing metrics related to program itself (title of program, execution time interval)
        manageframe = LabelFrame(tab, text="Manage", width=50)
        manageframe.grid(row=1, column=1, sticky='NESW', padx=5, pady=5)
        manageframe.grid_propagate(False)

        # 5 x 2 grid
        manageframe.rowconfigure(0, weight=1)
        manageframe.rowconfigure(1, weight=1)
        manageframe.rowconfigure(2, weight=1)
        manageframe.rowconfigure(3, weight=1)
        manageframe.columnconfigure(0, weight=1)
        manageframe.columnconfigure(1, weight=1)

        #program title
        self.titlevar = tk.StringVar()
        self.titlevar.set(self.title)

        title1 = Label(manageframe, text="Program Title: ")
        title1.grid(row=0, column=0, sticky="W")

        title2 = Entry(manageframe, textvariable=self.titlevar, width=10)
        title2.grid(row=0, column=1, sticky="W")

        #wait time
        self.waitvar = tk.DoubleVar()
        self.waitvar.set(self.wait)

        wait1 = Label(manageframe, text="Execution Interval: ")
        wait1.grid(row=1, column=0, sticky="W")

        wait2 = Spinbox(manageframe, from_=0, to=10, increment=0.1, textvariable=self.waitvar, width=10)
        wait2.grid(row=1, column=1, sticky="W")

        #hotkey
        self.hotkeyvar = tk.StringVar()
        self.hotkeyvar.set("None")

        hk1 = Label(manageframe, text="Execution Hotkey: ")
        hk1.grid(row=2, column=0, sticky="W")

        hk2 = Combobox(manageframe, textvariable=self.hotkeyvar, width=5)
        hk2vals = list(self.keydict.keys()) #all the label
        hk2["values"] = [None] + hk2vals #allow none to be an option
        hk2.state(["readonly"])
        hk2.grid(row=2, column=1, sticky="W")

        #save button
        self.managesave = Button(manageframe, text="Save", command=self.update_program)
        self.managesave.grid(row=3, column=0, columnspan=2)

        #by default its disabled
        self.managesave["state"] = "disabled"

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        self.titlevar.trace("w", lambda x,y,z : self.enablesave(title2, self.title, self.managesave))
        self.waitvar.trace("w", lambda x,y,z : self.enablesave(wait2, self.wait, self.managesave))
        self.hotkeyvar.trace("w", lambda x,y,z : self.enablesave(hk2, self.hotkey, self.managesave))

        #for editing the selected command
        self.edit = LabelFrame(tab, text="Edit", width=50) #starting width = 50
        self.edit.grid(row=2, column=1, sticky='NESW', padx=5, pady=5)
        self.edit.grid_propagate(False) #dont let children change widget size

        #set up 2x5 non-stretchy grid
        self.edit.rowconfigure(0)
        self.edit.rowconfigure(1)
        self.edit.columnconfigure(0)
        self.edit.columnconfigure(1)
        self.edit.columnconfigure(2)
        self.edit.columnconfigure(3)
        self.edit.columnconfigure(4)

        self.load_editdefault() #load the default edit frame (i.e. when no command is selected)

        self.notebook.add(tab, text="Program") #add to notebook

    def marker_tab(self):
        tab = Frame(self.notebook)
        tab.grid()
        self.notebook.add(tab, text="Marker")

        #set up grid
        tab.rowconfigure(0, weight=1)
        tab.rowconfigure(1, weight=2)
        tab.rowconfigure(2, weight=2)
        tab.columnconfigure(0, weight=3)
        tab.columnconfigure(1, weight=2)

        #get proportion of screen
        prop = self.width/self.height
        w = 500 #width is always 700px
        h = w / prop # get corresponding height

        #canvas to show markers on screen
        self.mcanvas = tk.Canvas(tab, width=w, height=h)

        self.mcanvas.grid(row=0, column=1)
        self.mcanvas.config(bg="white")

        #make the listbox
        self.mlist = tk.Listbox(tab, selectmode=tk.EXTENDED)
        self.mlist.grid(row=0, rowspan=3, column=0, sticky="NESW")
        self.mlist.bind("<<ListboxSelect>>", self.listbox_markerselect)
        #the toggle can be used for both listboxes because you have to be out of the listbox to switch tabs
        self.mlist.bind("<Enter>", self.listbox_toggle)
        self.mlist.bind("<Leave>", self.listbox_toggle)

        #manage frame
        manageframe = LabelFrame(tab, text="Manage", width=400)
        manageframe.grid(row=1, column=1, padx=5, pady=5, sticky="NWS")

        #set up grid
        manageframe.rowconfigure(0, weight=1)
        manageframe.rowconfigure(1, weight=1)
        manageframe.rowconfigure(2, weight=1)
        manageframe.columnconfigure(0, weight=1)
        manageframe.columnconfigure(1, weight=1)
        manageframe.columnconfigure(2, weight=2)
        manageframe.grid_propagate(False)

        mouselabel = Label(manageframe, textvariable=self.mousevar, width=50)
        mouselabel.grid(row=0, column=0, columnspan=3)

        i1 = Label(manageframe, text="press", width=5)
        i1.grid(row=1, column=0)

        self.mhvar = tk.StringVar()
        self.mhvar.set(self.mh)

        i2 = Combobox(manageframe, textvariable=self.mhvar, width=5)
        i2vals = list(self.keydict.keys()) #all the labels
        i2["values"] = i2vals
        i2.state(["readonly"])
        i2.grid(row=1, column=1)

        i3 = Label(manageframe, text="to set a marker at the mouse position")
        i3.grid(row=1, column=2)

        self.msave = Button(manageframe, command=self.update_markerhotkey, text="Save")
        self.msave.grid(row=2, column=1)
        self.msave["state"] = "disabled" #default to disabled

        #make it enable on change
        self.mhvar.trace("w", lambda x,y,z : self.enablesave(self.mhvar, self.mh, self.msave))

        #edit frame
        self.medit = LabelFrame(tab, text="Edit", width=400)
        self.medit.grid(row=2, column=1, padx=5, pady=5, sticky="NWS")
        self.medit.grid_propagate(False) #nonstretchy

        #set up grid
        self.medit.rowconfigure(0, weight=1)
        self.medit.rowconfigure(1, weight=1)
        self.medit.rowconfigure(2, weight=1)
        self.medit.columnconfigure(0, weight=1)
        self.medit.columnconfigure(1, weight=1)
        self.medit.columnconfigure(2, weight=1)
        self.medit.columnconfigure(3, weight=1)
        self.medit.grid_propagate(False)

        none = Label(self.medit, text="No Marker Selected")
        none.grid(row=0, column=0)

    def history_tab(self): #create history page for notebook
        tab = Frame(self.notebook)
        tab.grid()
        self.notebook.add(tab, text="History")

        #set up grid
        tab.rowconfigure(0, weight=1)

        #text box
        self.historylog = tk.Text(tab, width=105) #idk why but 105 is the best fit
        self.historylog.grid(row=0, sticky="NESW")
        self.historylog.configure(state='disabled') #disable as default

    def menu(self):
        #make a menu bar widget (container for the cascade menus at the top of the window)
        menubar = tk.Menu(self.root) #container is the root window

        #configure the root with the menu bar
        self.root.config(menu=menubar)

        #commands related to the python application itself and the program
        file_menu = tk.Menu(menubar, tearoff=0) #tearoff does not let you move the menu out of the window
        file_menu.add_command(label="Run", command=self.run)
        file_menu.add_separator()
        file_menu.add_command(label="Import TXT...", command=self.import_txt)
        file_menu.add_command(label="Export as TXT...", command=self.export_txt)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=quit)
        
        #commands related to editing commands
        edit_menu = tk.Menu(menubar, tearoff=0) #tearoff does not let you move the menu out of the window
        edit_menu.add_command(label="Cut", command=self.cut)
        edit_menu.add_command(label="Copy", command=self.copy)
        edit_menu.add_command(label="Paste", command=self.paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete", command=self.delete)
        edit_menu.add_command(label="Clear", command=self.clear)

        #commands to add command objects to program
        add_menu = tk.Menu(menubar, tearoff=0) #tearoff does not let you move the menu out of the window
        add_menu.add_command(label="Click", command=self.click)
        add_menu.add_command(label="Hold", command=self.hold)
        add_menu.add_command(label="Press", command=self.press)
        add_menu.add_command(label="Release", command=self.release)
        add_menu.add_command(label="Type", command=self.type)
        add_menu.add_separator()
        add_menu.add_command(label="Move Mouse", command=self.movemouse)
        add_menu.add_command(label="Drag Mouse", command=self.dragmouse)
        add_menu.add_command(label="Scroll Mouse", command=self.scroll)
        add_menu.add_separator()
        add_menu.add_command(label="Sleep", command=self.sleep)
        add_menu.add_command(label="Repeat", command=self.repeat)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        menubar.add_cascade(label="Add", menu=add_menu)

    def unshift(self, key): #takes a key (shift/caps lock pressed) and finds its corresponding unshifted key, returns the key if its already unshifted 
        '''
        all the ascii codes for keys that can be pressed without using shift/caps lock
        39      '
        44-47   , - . /
        48-57   0 to 9
        59      ;
        61      =
        91-93   [ ] \
        96      `
        97-122  a to z
        
        all the ascii codes for keys that can be pressed with using shift OR capslock
        65-90   A to Z

        all the ascii codes for keys that can be pressed with using shift ONLY
        33-38   ! " $ % &
        40-43   ( ) * +
        58      :
        60      <
        62-64   > ? @
        65-90   A to Z
        94-95   ^ _
        123-126 { | } ~
        '''
        
        #yes this was done by hand
        #shifted value : unshifted value
        dict = \
            {33:49} | \
            {34:39} | \
            {35:51} | \
            {36:52} | \
            {37:53} | \
            {38:55} | \
            {40:57} | \
            {41:48} | \
            {42:56} | \
            {43:61} | \
            {58:59} | \
            {60:44} | \
            {62:46} | \
            {63:47} | \
            {64:50} | \
            {94:54} | \
            {95:45} | \
            {123:91} | \
            {124:92} | \
            {125:93} | \
            {126:96}

        if len(key) > 0:
            key = ord(key)
            rtn = key

            if "shift" in self.keys: #shift/caps lock pressed
                if 65 <= key and key <= 90: #A-Z
                    rtn = key + 32
                else:
                    rtn = dict[key]
            elif "caps" in self.keys: #caps lock pressed
                if 65 <= key and key <= 90: #only a-z are affected
                    rtn = key + 32 #a-z <-- A-Z

            return chr(rtn)

    def handle_key_press(self, key):
        self.keys.append(self.unshift(key.char))
        self.update_key()

    def handle_key_release(self, key):
        self.keys.remove(self.unshift(key.char))
        self.update_key()

    def handle_other_key_press(self, key):
        self.keys.append(key)
        self.update_key()

    def handle_other_key_release(self, key):
        self.keys.remove(key)
        self.update_key()

    def load_curr_marker(self, i):
        self.mcurr = i #since curr should only be used once at a time, we can just reuse it

        #delete current edit tab children
        for i in self.medit.winfo_children():
            i.destroy()

        #load the edit frame
        if self.mcurr != None:
            self.load_marker()       
        else:
            self.load_editmarkerdefault()  
    
    def load_curr(self, i): #update the GUI to correctly handle the current seletion (at index i)
        self.curr = i

        #delete current edit tab children
        for i in self.edit.winfo_children():
            i.destroy()

        #reset vals
        self.vals = []

        if self.curr != None:
            #load the new one
            if self.commands[self.curr].name == "Click":
                self.load_click()
            if self.commands[self.curr].name == "Hold":
                self.load_hold()
            if self.commands[self.curr].name == "Press":
                self.load_press()
            if self.commands[self.curr].name == "Release":
                self.load_release()
            if self.commands[self.curr].name == "Type":
                self.load_type()
            if self.commands[self.curr].name == "Move Mouse":
                self.load_movemouse()
            if self.commands[self.curr].name == "Drag Mouse":
                self.load_dragmouse()
            if self.commands[self.curr].name == "Scroll Mouse":
                self.load_scroll()
            if self.commands[self.curr].name == "Sleep":
                self.load_sleep()
            if self.commands[self.curr].name == "Repeat":
                self.load_repeat()
        else:
            self.load_editdefault()

    def load_editsave(self, frame): #adds two buttons to the bottom of a command manage labelframe
        #now do the buttons
        delbutton = Button(frame, command=self.delete, text="Delete")
        delbutton.grid(row=1, column=0)

        self.editsave = Button(frame, command=self.save, text="Save")
        self.editsave.grid(row=1, column=1)
        self.editsave["state"] = "disabled"

    def load_editmarkersave(self): #adds the two bottom buttons
        frame = self.medit
        delbutton = Button(frame, command=self.delete, text="Delete")
        delbutton.grid(row=2, column=0)

        self.meditsave = Button(frame, command=self.save, text="Save")
        self.meditsave.grid(row=2, column=1)
        self.meditsave["state"] = "disabled"
        

    def load_editdefault(self): #default frame for when no command is selected
        none = Label(self.edit, text="No Command Selected")
        none.grid(row=0, column=0)
    
    def load_editmarkerdefault(self): #default frame for when no command is selected
        none = Label(self.medit, text="No Marker Selected")
        none.grid(row=0, column=0)
    
    def load_runlist(self):
        '''
        compile the execution list

        if d = repeat next 3 lines 2 times
        then this is how it would compile:

        self.commands
        0	a
        1	b
        2	c
        3	d(2)
        4		e
        5		f
        6		g
        7
        8

        runlist
        0	a
        1	b
        2	c
        3   e
        4	f
        5	g
        6	e
        7	f
        8	g
        '''
        runlist = []
        for i in range(0, len(self.commands)):
            cmd = self.commands[i]

            if cmd.name == "Repeat" and cmd.valid:
                repeat = cmd.vals[0]
                lines = cmd.vals[1]
                for n in range(0, repeat - 1): #runlist will append everything again after, so -1 repeat
                    for j in range(i + 1, i + lines + 1):
                        if j < len(self.commands): #only add if its in the list
                            if self.commands[j].valid: #only run if valid
                                runlist.append(self.commands[j])
            else: #omit the repeat commands from running
                if cmd.valid: #only run if valid
                    runlist.append(cmd) #if its not a repeat command, just add it
        
        return runlist

    def update_program(self, log = True): #update program metrics from Tk Vars
        self.root.title(self.titlevar.get())
        self.wait = self.waitvar.get()
        self.hotkey = self.hotkeyvar.get()

        if self.hotkey == "None": #if the user selects no hotkey, convert gui to logic (str --> None)
            self.hotkey = None

        #disable the save button again
        self.managesave["state"] = "disabled"

        #update history log
        if log: #by default it will log, but if its part of another sequence (i.e. import txt) it wont
            self.update_history("program", None) #no val for this entry
    
    def update_markerhotkey(self, log = True): #update marker setting hotkey
        self.mh = self.mhvar.get()

        #disable the save button again
        self.msave["state"] = "disabled"

        if log:
            self.update_history("edit", "marker hotkey")

    def update_mouse(self, x, y): #update mouse position from listener
        mousepos = (int(x), int(y))
        self.mousevar.set("Mouse Position: " + str(mousepos))
        
    def update_key(self):
        strkeys = ""

        #format the things to be pressed
        for i in range(0, len(self.keys)):
            strkeys += self.keys[i]
            if i < len(self.keys) - 1: #dont add this on the last one or it looks weird
                strkeys += "+"

        self.keyvar.set("Keys Pressed: " + strkeys)

        #now check if hotkey was pressed
        if self.hotkey != None:
            for i in self.keys:
                if i == self.hotkey: #if the hotkey is in the pressed keys
                    self.run()

        #if the marker tab is open, check if marker hotkey was pressed
        if self.get_active_tab() == "Marker":
            for i in self.keys:
                if i == self.mhvar.get():
                    self.add_marker()
    

    def update_exectime(self): #re-calculates execution time of program
        sec = 0
        runlist = self.load_runlist() # load the runlist so we have the raw command queue

        for i in range(0, len(runlist)):
            cmd = runlist[i]
            sec += cmd.getexectime() #get execution time of each command

            #if its not the last command, then add an extra self.wait to the end
            if i < len(runlist) - 1:
                sec += self.wait

        #now set the label to sec
        self.exectime.set("Execution Time: " + str(sec) + "s")

    def update_listbox(self): #updates gui of listbox
        indents = [0 for x in range(0, len(self.commands))] #contains indices to indent. if an index appears again, its indented again

        #check for indents
        for i in range(0, len(self.commands)):
            cmd = self.commands[i]
            if cmd.name == "Repeat" and cmd.valid: #only indent if its a valid repeat
                lines = cmd.vals[1]
                for j in range(i + 1, i + lines + 1): #get the lines affected by the repeat command
                    if j < len(self.commands): #only add if its in the list
                        indents[j] += 1 #add one more indent to index j

        #now add indents and edit colors
        for i in range(0, len(self.commands)):
            cmd = self.commands[i]
            
            label = cmd.label()
            for j in range(0, indents[i]):
                label = "\t" + label #add all the indents
            
            #now replace label
            self.list.delete(i)
            self.list.insert(i, label)

            if cmd.valid:
                #make white
                self.list.itemconfig(i,{'fg':'white'})
            else:
                #make gray
                self.list.itemconfig(i,{'fg':'gray'})

    
    def update_history(self, idx, val): #gets the idx from the dictionary and replaces _ with val
        labels = { #the _ will be replaced with values depending on label
            "copy":"copied _ commands",
            "paste":"pasted _ commands",
            "cut":"cut _ commands",
            "delete":"deleted _ commands",
            "clear":"cleared program",
            "run":"ran _ commands",
            "import":"imported program from _",
            "export":"exported program to _",
            "add":"added _",
            "edit":"edited _",
            "program":"updated program details"
        }
        label = labels[idx].replace("_", str(val)) #fill in the blanks

        #get the current time for the time stamp
        localtime = t.localtime()
        h = int(t.strftime("%H", localtime))
        m = int(t.strftime("%M", localtime))

        #format with AM/PM, and convert from military time --> regular time
        meridian = "am"
        if h > 12: #afternoon
            h -= 12
            meridian = "pm"
        elif h == 0: #midnight
            h = 12

        curr_time = str(h) + ":" + str(m) + meridian

        #enable it, edit it, then disable it (so user cant edit it)
        self.historylog.configure(state='normal')
        self.historylog.insert(tk.END, curr_time + "\t" + label + "\n")
        self.historylog.configure(state='disabled')

    def get_active_tab(self): #gets the name of the currently open tab
        return self.notebook.tab(self.notebook.select(), "text")

    def get_mdict(self):
        #create the marker dictionary
        mdict = {}
        for i in self.markers:
            mdict[i.name] = i
        
        return mdict

    def add_marker(self):
        #get current mouse pos
        con = mouse.Controller()
        pos = con.position

        m = Marker(pos[0], pos[1], "Marker " + str(len(self.markers) + 1)) #increments so that each name is unique

        #add to listbox
        self.listbox_add(m)
    
    def update_canvas(self): #updates the canvas GUI by redrawing everything
        #clear canvas
        self.mcanvas.delete("all")

        #add everything to canvas
        for i in self.markers:
            #translate x and y coordinates
            cw = int(self.mcanvas["width"]) #canvas width
            sw = self.width #screen width
            sx = i.x #screen x

            #ratio: sx/sw = cx/cw --> cx = (sx * cw)/sw
            cx = (sx * cw)/sw #canvas x

            ch = int(self.mcanvas["height"]) #canvas height
            sh = self.height #screen height
            sy = i.y #screen y
            
            #same ratio
            cy = (sy * ch)/sh #canvas y

            #draw circle of radius 1
            r = 3
            self.mcanvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline = "#000000", fill = i.color) #center point at (cx, cy)

            #now add the text
            #by default, the text is centered around x,y
            self.mcanvas.create_text(cx, cy - (r + 10), \
            text=i.name + " (" + str(sx) + ", " + str(sy) + ")", \
            fill = "#000000") #name + coords

    #compares a dynamic variable to its starting value. if they differ, enable the save button to be pressed
    def enablesave(self, var, val, save): #var = variable to check, val = default value, save = button to change
        if var.get() == val:
            save["state"] = "disabled"
        else:
            save["state"] = "normal"

    def delete(self, log = True): #deletes a selection of commands in the listbox
        if self.get_active_tab() == "Program":
            curr = self.list.curselection()
            del_len = len(curr)

            if del_len < 1: #the user is using the button in the edit menu OR nothing is selected for menu widget
                if self.curr != None:
                    curr = self.curr

                    self.commands.pop(curr)
                    self.list.delete(curr)

                    #add to history log if its not part of a cut (thats handled separately)
                    if log:
                        self.update_history("delete", 1)
            else: #the user is using the menu widget, so we can just delete the current selection
                for i in range(0, len(curr)): #iterates through n elements to delete (delete the labels)
                    self.commands.pop(curr[0]) #delete from the first element in selection
            
                self.list.delete(curr[0], curr[len(curr) - 1]) #delete from listbox

                #add to history log if its not part of a cut (thats handled separately)
                if log:
                    self.update_history("delete", del_len)
        
            #update the program (that nothing is selected)
            self.load_curr(None)

            #update execution time
            self.update_exectime()

            #update listbox gui
            self.update_listbox()

        if self.get_active_tab() == "Marker":
            curr = self.mlist.curselection()
            del_len = len(curr)

            if del_len < 1: #the user is using the button in the edit menu OR nothing is selected for menu widget
                if self.mcurr != None:
                    curr = self.mcurr

                    self.markers.pop(curr)
                    self.mlist.delete(curr)

                    #add to history log if its not part of a cut (thats handled separately)
                    if log:
                        self.update_history("delete", 1)
            else: #the user is using the menu widget, so we can just delete the current selection
                for i in range(0, len(curr)): #iterates through n elements to delete (delete the labels)
                    self.markers.pop(curr[0]) #delete from the first element in selection
            
                self.mlist.delete(curr[0], curr[len(curr) - 1]) #delete from listbox

                #add to history log if its not part of a cut (thats handled separately)
                if log:
                    self.update_history("delete", del_len)
        
            #update the program (that nothing is selected)
            self.load_curr_marker(None)

            #update canvas
            self.update_canvas()

    def copy(self, log = True): #copy commands indices to the clipboard
        if self.get_active_tab() == "Program":
            self.clipboard = [] #reset clipboard
            for i in self.list.curselection():
                self.clipboard.append(self.commands[i]) #add everything to clipboard
            
            #add to history log if anything was copied and if its not part of a cut (thats handled separately)
            clipboard_length = len(self.list.curselection())
            if clipboard_length > 0 and log:
                self.update_history("copy", clipboard_length)
        if self.get_active_tab() == "Marker":
            self.mclipboard = [] #reset clipboard
            for i in self.mlist.curselection():
                self.mclipboard.append(self.markers[i]) #add everything to clipboard
            
            #add to history log if anything was copied and if its not part of a cut (thats handled separately)
            clipboard_length = len(self.mlist.curselection())
            if clipboard_length > 0 and log:
                self.update_history("copy", clipboard_length)

    def paste(self, log = True): #paste all indices from clipboard after current selection
        if self.get_active_tab() == "Program":
            if len(self.clipboard) > 0:
                if self.curr != None: #insert into program
                    i = self.curr

                    #remove labels (after self.curr) from listbox
                    self.list.delete(i + 1, len(self.commands))

                    #pop command objs from commands
                    after = []
                    for j in range(i + 1, len(self.commands)):
                        #every time we pop, the indices shift, so we just keep popping the item after curr
                        after.append(self.commands.pop(i + 1))
                    
                    #add new stuffs
                    for cmd in self.clipboard: 
                        self.listbox_add(cmd)

                    #now add back everything else
                    for cmd in after:
                        self.listbox_add(cmd)
                        
                else: #if nothing is selected, just add to the end of the program
                    for i in self.clipboard:
                        self.listbox_add(i)
                
                #update execution time
                self.update_exectime()
                
                #add to history log
                if log:
                    self.update_history("paste", len(self.clipboard))
        if self.get_active_tab() == "Marker":
            if self.mcurr != None: #insert into program
                i = self.mcurr

                #remove labels (after self.mcurr) from listbox
                self.mlist.delete(i + 1, len(self.markers))

                #pop marker objs from markers
                after = []
                for j in range(i + 1, len(self.markers)):
                    #every time we pop, the indices shift, so we just keep popping the item after curr
                    after.append(self.markers.pop(i + 1))
                
                #add new stuffs
                for m in self.mclipboard: 
                    self.listbox_add(m)

                #now add back everything else
                for m in after:
                    self.listbox_add(m)
                    
            else: #if nothing is selected, just add to the end of the program
                for i in self.mclipboard:
                    self.listbox_add(i)
            
                #update canvas
                self.update_canvas()
                
                #add to history log
                if log:
                    self.update_history("paste", len(self.mclipboard))
        
    def cut(self, log = True): #copies selection and deletes it
        if self.get_active_tab() == "Program":
            #store length for history log
            cut_len = len(self.list.curselection())

            #tell the functions that they are part of a cut command
            self.copy(False) #no matter what, it shouldnt log anything
            self.delete(False)

            #now add to history log
            if log:
                self.update_history("cut", cut_len)
        if self.get_active_tab() == "Marker":
            #store length for history log
            cut_len = len(self.mlist.curselection())

            #tell the functions that they are part of a cut command
            self.copy(False) #no matter what, it shouldnt log anything
            self.delete(False)

            #now add to history log
            if log:
                self.update_history("cut", cut_len)
    
    def clear(self, log = True): #reset all dynamic vals
        if self.get_active_tab() == "Program":
            self.curr = None
            self.list.delete(0, self.list.size())
            self.commands = []
            self.vals = []
            #dont clear clipboard
            
            self.waitvar.set(0.1)
            self.titlevar.set("Macro Editor")

            #now update the program to display it
            self.load_curr(self.curr)
            self.update_exectime()
            self.update_program(log) #if this function shouldnt log, update_program shouldnt log either

            #update history log
            if log:
                self.update_history("clear", None) #no val for this entry
        if self.get_active_tab() == "Marker":
            self.mcurr = None
            self.markers = []
            self.mlist.delete(0, self.mlist.size()) #clear listbox
            #dont clear clipboard

            self.mhvar.set("space")

            #update things
            self.load_curr_marker(self.mcurr)
            self.update_markerhotkey(log)
            self.update_canvas()

            #update history log
            if log:
                self.update_history("clear", None) #no value for this entry
    
    def save(self, log = True): #save the edits to the current command
        window = self.get_active_tab() #get current tab (this function is different for different tabs)
        
        if window == "Program": #program tab
            cmd = self.commands[self.curr]

            saved = True

            #save changes
            try:
                if len(self.vals) > 1:
                    v0 = self.vals[0].get()
                    v1 = self.vals[1].get()
                    cmd.save([v0, v1])
                else:
                    v0 = self.vals[0].get()
                    cmd.save([v0])
            except tk.TclError:
                saved = False

            if saved:
                #disable save button (we know which one it is bc we're in the edit menu)
                self.editsave["state"] = "disabled"
                
                #update label
                self.list.delete(self.curr)
                self.list.insert(self.curr, cmd.label())

                #update execution time
                self.update_exectime()

                #update listbox
                self.update_listbox()

                #update history log
                if log:
                    self.update_history("edit", str(cmd.name).lower() + " command")
        if window == "Marker":
            m = self.markers[self.mcurr]

            #save changes
            x = self.mx.get()
            y = self.my.get()
            name = self.mname.get()

            m.save(x, y, name)

            #update the canvas
            self.update_canvas() 

            #update listbox label
            self.mlist.delete(self.mcurr)
            self.mlist.insert(self.mcurr, m.name)

    
    def run(self, log = True): #run the program!!
        runlist = self.load_runlist() #get the runlists

        mdict = self.get_mdict() #get the markers as a dictionary

        for i in range(0, len(runlist)):
            cmd = runlist[i]
            if cmd.valid: #only run if the command is valid
                if cmd.dict == "n": #input keydict if the command needs it 
                    cmd.run()
                elif cmd.dict == "k":
                    cmd.run(self.keydict)
                elif cmd.dict =="m":
                    cmd.run(mdict)

                if i < len(self.commands) - 1: #sleep for self.wait time if its not the last command
                    t.sleep(self.wait)
            
        #update history log
        if log:
            self.update_history("run", len(self.commands))
    
    def listbox_toggle(self, event): #toggle when the mouse is over the listbox (and items can be selected)
        self.inlistbox = not(self.inlistbox)
    
    def listbox_add(self, x, log = True, tab = "a"): #add command to the listbox

        #tab = "a": use active tab, tab = "p": set to program, tab = "m": set to marker
        if tab == "a":
            tab = self.get_active_tab()
        elif tab == "p":
            tab = "Program"
        elif tab == "m":
            tab = "Marker"

        if tab == "Program":
            self.list.insert(len(self.commands), x.label())
            self.commands.append(x)

            #now update execution time
            self.update_exectime()

            #update listbox gui
            self.update_listbox()

            #update history log
            if log:
                self.update_history("add", str(x.name).lower() + " command")

        if tab == "Marker":
            self.mlist.insert(len(self.markers), x.name)
            self.markers.append(x)

            #update canvas
            self.update_canvas()

            #update history log
            if log:
                self.update_history("add", x.name + " marker")

    def listbox_programselect(self, event): #handles a command being selected in listbox
        curr = self.list.curselection() #returns a tuple
        if self.inlistbox: #only allow changes if in the listbox
            if len(curr) == 1: #single selection
                index = curr[0] #since the listbox only allows single selection, the tuple only has 1 item
            else: #either multiple selection or no selection (you cant edit then)
                index = None
            self.load_curr(index)
        
    def listbox_markerselect(self, event): #handles a marker being selected in listbox
        curr = self.mlist.curselection() #returns a tuple
        if self.inlistbox: #only allow changes if in the listbox
            if len(curr) == 1: #single selection
                index = curr[0] #since the listbox only allows single selection, the tuple only has 1 item
            else: #either multiple selection or no selection (you cant edit then)
                index = None
            self.load_curr_marker(index)
    
    def load_marker(self):
        frame = self.medit

        marker = self.markers[self.mcurr]

        #name label
        n1 = Label(frame, text="Name:")
        n1.grid(row=0, column=0)

        #name
        self.mname = tk.StringVar()
        self.mname.set(marker.name)

        n2 = Entry(frame, width=10, textvariable=self.mname)
        n2.grid(row=0, column=1)

        #mouse coordniates
        m1 = Label(frame, text="Coordinates: (")
        m1.grid(row=1, column=0)

        #x coord
        self.mx = tk.IntVar()
        self.mx.set(marker.x)

        m2 = Spinbox(frame, from_=0, to=self.width, width=5, textvariable=self.mx)
        m2.grid(row=1, column=1)

        m3 = Label(frame, text=", ")
        m3.grid(row=1, column=2)

        #y coord
        self.my = tk.IntVar()
        self.my.set(marker.y)

        m4 = Spinbox(frame, from_=0, to=self.height, width=5, textvariable=self.my)
        m4.grid(row=1, column=3)

        m5 = Label(frame, text=")")
        m5.grid(row=1, column=4)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        self.mname.trace("w", lambda x,y,z : self.enablesave(n2, marker.name, self.meditsave))
        self.mx.trace("w", lambda x,y,z : self.enablesave(m2, marker.x, self.meditsave))
        self.my.trace("w", lambda x,y,z : self.enablesave(m4, marker.y, self.meditsave))

        self.load_editmarkersave()

    def click(self): #create new click command
        cmd = Click()
        self.listbox_add(cmd)
    
    def load_click(self): #load click frame onto edit frame
        frame = self.edit

        c0 = Label(frame, text="click")
        c0.grid(row=0, column=0)

        val0 = tk.StringVar()
        val0.set(self.commands[self.curr].vals[0]) # put default val
        self.vals.append(val0)

        c1 = Combobox(frame, textvariable=self.vals[0], width=5)
        c1vals = list(self.keydict.keys()) #all the labels
        c1["values"] = c1vals
        c1.state(["readonly"])
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))

        c2 = Label(frame, text="")
        c2.grid(row=0, column=2)

        val1 = tk.IntVar()
        val1.set(self.commands[self.curr].vals[1])
        self.vals.append(val1)

        c3 = Spinbox(frame, from_=1, to=100, textvariable=self.vals[1], width=5)
        c3.grid(row=0, column=3)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val1.trace("w", lambda x,y,z : self.enablesave(c3, self.commands[self.curr].vals[1], self.editsave))

        c4 = Label(frame, text=" times")
        c4.grid(row=0, column=4)
        

        self.load_editsave(frame) #now put the save and delete button at the bottom

    def hold(self): #create new hold object
        cmd = Hold()
        self.listbox_add(cmd)

    def load_hold(self): #load the hold frame onto the edit frame
        frame = self.edit

        c0 = Label(frame, text="hold ")
        c0.grid(row=0, column=0)

        val0 = tk.StringVar()
        val0.set(self.commands[self.curr].vals[0]) # put default val
        self.vals.append(val0)

        c1 = Combobox(frame, textvariable=self.vals[0], width=5)
        c1vals = list(self.keydict.keys()) #all the labels
        c1["values"] = c1vals
        c1.state(["readonly"])
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))

        c2 = Label(frame, text=" for ")
        c2.grid(row=0, column=2)

        val1 = tk.DoubleVar()
        val1.set(self.commands[self.curr].vals[1])
        self.vals.append(val1)

        #format and increment variables allow spinbox to go to 1 decimal place
        c3 = Spinbox(frame, textvariable=self.vals[1], from_=1, to=100, increment=0.1, format="%.1f", width=5)
        c3.grid(row=0, column=3)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val1.trace("w", lambda x,y,z : self.enablesave(c3, self.commands[self.curr].vals[1], self.editsave))

        c4 = Label(frame, text=" seconds")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the save and delete button at the bottom

    def press(self): #create new press object
        cmd = Press()
        self.listbox_add(cmd)

    def load_press(self): #load press frame onto edit frame
        frame = self.edit

        c0 = Label(frame, text="press ")
        c0.grid(row=0, column=0)

        val0 = tk.StringVar()
        val0.set(self.commands[self.curr].vals[0]) # put default val
        self.vals.append(val0)

        c1 = Combobox(frame, textvariable=self.vals[0], width=5)
        c1vals = list(self.keydict.keys()) #all the labels
        c1["values"] = c1vals
        c1.state(["readonly"])
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))

        c2 = Label(frame, text="")
        c2.grid(row=0, column=2)

        c3 = Label(frame, text="")
        c3.grid(row=0, column=3)

        c4 = Label(frame, text="")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the save and delete button at the bottom

    def release(self): #create new release object
        cmd = Release()
        self.listbox_add(cmd)

    def load_release(self): #load release frame onto edit frame
        frame = self.edit

        c0 = Label(frame, text="release ")
        c0.grid(row=0, column=0)

        val0 = tk.StringVar()
        val0.set(self.commands[self.curr].vals[0]) # put default val
        self.vals.append(val0)

        c1 = Combobox(frame, textvariable=self.vals[0], width=5)
        c1vals = list(self.keydict.keys()) #all the labels
        c1["values"] = c1vals
        c1.state(["readonly"])
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))

        c2 = Label(frame, text="")
        c2.grid(row=0, column=2)

        c3 = Label(frame, text="")
        c3.grid(row=0, column=3)

        c4 = Label(frame, text="")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the save and delete button at the bottom

    def type(self): #create type object
        cmd = Type()
        self.listbox_add(cmd)

    def load_type(self): #load type frame onto edit frame
        frame = self.edit

        c0 = Label(frame, text="type ")
        c0.grid(row=0, column=0)

        val0 = tk.StringVar()
        val0.set(self.commands[self.curr].vals[0]) # put default val
        self.vals.append(val0)

        c1 = Entry(frame, textvariable=self.vals[0], width=10)
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))

        c2 = Label(frame, text="")
        c2.grid(row=0, column=2)

        c3 = Label(frame, text="")
        c3.grid(row=0, column=3)

        c4 = Label(frame, text="")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the save and delete button at the bottom

    def movemouse(self): #create movemouse object
        cmd = MoveMouse()
        self.listbox_add(cmd)
    
    def load_movemouse(self): #load movemouse frame onto edit frame
        frame = self.edit

        c0 = Label(frame, text="move mouse to ")
        c0.grid(row=0, column=0)

        val0 = tk.StringVar()
        val0.set(self.commands[self.curr].vals[0])
        self.vals.append(val0)
        
        c1 = Combobox(frame, textvariable=self.vals[0], width=10)
        c1["values"] = list(self.get_mdict().keys())
        c1.state(["readonly"])
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))

        c2 = Label(frame, text="")
        c2.grid(row=0, column=2)

        c3 = Label(frame, text="") 
        c3.grid(row=0, column=3)

        c4 = Label(frame, text="")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the save and delete button at the bottom

    def dragmouse(self): #create dragmouse object
        cmd = DragMouse()
        self.listbox_add(cmd)
    
    def load_dragmouse(self): #load dragmouse frame onto edit frame
        frame = self.edit

        c0 = Label(frame, text="drag mouse to ")
        c0.grid(row=0, column=0)

        val0 = tk.StringVar()
        val0.set(self.commands[self.curr].vals[0])
        self.vals.append(val0)
        #width 10 bc the entry in marker tab edit frame is width 10
        c1 = Combobox(frame, textvariable=self.vals[0], width=10)
        c1["values"] = list(self.get_mdict().keys())
        c1.state(["readonly"])
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))

        c2 = Label(frame, text="")
        c2.grid(row=0, column=2)

        c3 = Label(frame, text="") 
        c3.grid(row=0, column=3)

        c4 = Label(frame, text="")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the save and delete button at the bottom

    def scroll(self): #create scroll object
        cmd = Scroll()
        self.listbox_add(cmd)

    def load_scroll(self): #load scroll frame onto edit frame
        frame = self.edit

        c0 = Label(frame, text="scroll mouse ")
        c0.grid(row=0, column=0)

        val0 = tk.IntVar()
        val0.set(self.commands[self.curr].vals[0])
        self.vals.append(val0)

        c1 = Spinbox(frame, textvariable=self.vals[0], from_=1, to=100, width=5)
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))
        
        c2 = Label(frame, text=" steps ")
        c2.grid(row=0, column=2)

        val1 = tk.StringVar()
        val1.set(self.commands[self.curr].vals[1])
        self.vals.append(val1)

        c3 = Combobox(frame, textvariable=self.vals[1], width=5)
        c3["values"] = ["up", "down", "right", "left"]
        c3.state(["readonly"])
        c3.grid(row=0, column=3)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val1.trace("w", lambda x,y,z : self.enablesave(c3, self.commands[self.curr].vals[1], self.editsave))

        c4 = Label(frame, text="")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the delete and save button at the bottom

    def sleep(self): #create sleep object
        cmd = Sleep()
        self.listbox_add(cmd)
    
    def load_sleep(self): #load sleep frame onto edit frame
        frame = self.edit

        #vals[0]
        c0 = Label(frame, text="sleep for ")
        c0.grid(row=0, column=0)

        val0 = tk.DoubleVar() #allow it to handle ints
        val0.set(self.commands[self.curr].vals[0])
        self.vals.append(val0)

        #format and increment variables allow spinbox to go to 1 decimal place
        c1 = Spinbox(frame, textvariable=self.vals[0], from_=1, to=100, increment=0.1, format="%.1f", width=5)
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))
        
        c2 = Label(frame, text=" seconds")
        c2.grid(row=0, column=2)

        c3 = Label(frame, text="")
        c3.grid(row=0, column=3)

        c4 = Label(frame, text="")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the delete and save button at the bottom

    def repeat(self): #create repeat object
        cmd = Repeat()
        self.listbox_add(cmd)
    
    def load_repeat(self): #load repeat frame onto edit frame
        frame = self.edit

        c0 = Label(frame, text="repeat next ")
        c0.grid(row=0, column=0)

        val0 = tk.IntVar()
        val0.set(self.commands[self.curr].vals[0])
        self.vals.append(val0)

        val1 = tk.IntVar()
        val1.set(self.commands[self.curr].vals[1])
        self.vals.append(val1)

        c1 = Spinbox(frame, textvariable=self.vals[1], from_=1, to=100, width=5)
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))
        
        c2 = Label(frame, text=" lines ")
        c2.grid(row=0, column=2)

        c3 = Spinbox(frame, textvariable=self.vals[0], from_=0, to=100, width=5)
        c3.grid(row=0, column=3)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val1.trace("w", lambda x,y,z : self.enablesave(c3, self.commands[self.curr].vals[1], self.editsave))

        c4 = Label(frame, text=" times")
        c4.grid(row=0, column=4)


        self.load_editsave(frame) #now put the delete and save button at the bottom

    def import_txt(self): #import a txt file as a program
        path = fd.askopenfilename() #os ui to ask for file, returns file path as string
        try:
            if len(path.removesuffix(".txt")) == len(path): #check if the path is NOT a .csv file
                raise FileNotFoundError()
            
            with open(path, "r") as file:
                text = file.readlines() #converts .txt file to list[str]

            for i in text: #remove the "\n"
                i.removesuffix("\n")
            
            #reset the current macro (so we can overwrite)
            self.clear(False)

            '''
            Title
            wait

            command 1
            command 2
            command 3
            etc.
            '''
            #keep removing first item of list[str] until we get to the actual commands
            title = text.pop(0)
            wait = text.pop(0)
            try:
                wait = float(wait)
            except ValueError:
                wait = 0.5 # just set to default if its invalid :/

            hk = text.pop(0) #get the execution hotkey
            if hk in list(self.keydict.keys()): #if its in the key dictionary, use it, otherwise its invalid (just set default)
                self.hotkeyvar.set(hk)
            else:
                self.hotkeyvar.set("None")

            mh = text.pop(0) #get the marker hotkey
            if mh in list(self.keydict.keys()): #if its in the key dictionary, use it, otherwise its invalid (just set default)
                self.hotkeyvar.set(mh)
            else:
                self.hotkeyvar.set("space")

            text.pop(0) #for filler line

            self.titlevar.set(title)
            self.waitvar.set(wait)
            self.update_program(False)
            self.update_markerhotkey(False)

            commands = True

            for i in text: #now we transcribe commands
                i = i.removesuffix("\n")

                if i == "": #its the end of the commands
                    commands = False #tell the program to switch to recording markers
                else:
                    i = i.split(",")

                    if commands:
                        name = i[0]
                        v0 = i[1]
                        v1 = None
                        if len(i) > 2:
                            v1 = i[2]

                        #now we gotta cast all the bruhs
                        try:
                            if name == "Click": #same as self.click() but it saves the new data to the obj before adding it
                                cmd = Click()
                                cmd.save([v0, int(v1)])
                            if name == "Hold":
                                cmd = Hold()
                                cmd.save([v0, float(v1)])
                            if name == "Press":
                                cmd = Press()
                                cmd.save([v0])
                            if name == "Release":
                                cmd = Release()
                                cmd.save([v0])
                            if name == "Type":
                                cmd = Type()
                                cmd.save([v0])
                            if name == "Move Mouse":
                                cmd = MoveMouse()
                                cmd.save([int(v0), int(v1)])
                            if name == "Drag Mouse":
                                cmd = DragMouse()
                                cmd.save([int(v0), int(v1)])
                            if name == "Scroll Mouse":
                                cmd = Scroll()
                                cmd.save([int(v0), v1])
                            if name == "Sleep":
                                cmd = Click()
                                cmd.save([float(v0)])
                            if name == "Repeat":
                                cmd = Repeat()
                                cmd.save([int(v0), int(v1)])
                                
                            self.listbox_add(cmd, False, "p") #add to listbox
                        
                        except (TypeError, tk.TclError): #just dont add it if theres a casting error
                            continue
                    
                    else: #interpret commands
                        try:
                            name = i[0]
                            x = int(i[1])
                            y = int(i[2])

                            m = Marker(x, y, name)
                            self.listbox_add(m, False, "m") #make it add a marker, not a command
                        except (TypeError, tk.TclError): #keep going if theres an error (disregard it)
                            continue

            self.update_history("import", title.removesuffix("\n") + ".txt")

        except FileNotFoundError: #if the file is not found, just stop
            pass

    def export_txt(self): #writes program to txt file at designated directory
        '''
        Title
        wait

        command 1
        command 2
        command 3
        etc.
        '''

        #file name = title of macro
        filename = self.title.replace(" ", "_").replace("/", "_").replace(".", "_") + ".txt"
        #make the string
        text = [] #each line is one item in array, will be separated by "\n"

        text.append(filename.removesuffix(".txt")) #remove .txt for the text
        text.append(str(self.wait))
        text.append(str(self.hotkey))
        text.append(str(self.mh))
        text.append("")

        #now put the commands
        for i in self.commands:
            if i.valid: #only write the valid commands to the file
                s = str(i.name) + "," + str(i.vals[0])
                if len(i.vals) > 1:
                    s += "," + str(i.vals[1])
                text.append(s)

        #buffer line
        text.append("")

        #now put markers
        for i in self.markers:
            s = str(i.name) + "," + str(i.x) + "," + str(i.y)
            text.append(s)

        #ask for file directory
        path = fd.askdirectory()
        filepath = os.path.join(path, filename)

        #now open the file and write to it
        file = open(filepath, "w")
        for i in text:
            file.write(i + "\n")

        #update history log
        self.update_history("export", filename)

Macro() #start the GUI