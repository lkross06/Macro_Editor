#Lucas 14 Dec 2022

import tkinter as tk
from tkinter.ttk import *
import pandas as pd
from tkinter import filedialog as fd
import pynput.keyboard as keyboard #Listener, Button, Controller
import pynput.mouse as mouse #Listener, Button, Controller
import time as t
import os

'''
generic class for command objects
'''
class Command:
    def __init__(self, name, vals, usekeydict, typestr):
        self.name = str(name) #identification var
        self.vals = vals #values to use to run (dynamic size, based on command)
        self.intbounds = [1, 100] #bounds for commands that use int values (i.e. hold for n seconds)
        self.usekeydict = usekeydict
        self.type = typestr

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
        Command.__init__(self, "Click", ["a", 1], True, "Button") #default values: click a, 1 time
        #we need both controllers bc the user can click keys or mouse buttons
        self.key = keyboard.Controller()
        self.mouse = mouse.Controller()

    def label(self):
        return "click [" + self.vals[0] + "] " + str(self.vals[1]) + " times"

    def save(self, vals): #returns true if successful, false otherwise
        #vals input is an array of Tk Vars (because they update dynamically), so we gotta .get() to get their values
        key = vals[0].get()
        repeat = vals[1].get()

        self.checkintbounds(repeat) #check bounds

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
        Command.__init__(self, "Hold", ["a", 1], True, "Button") #default values: hold a for 1 second
        self.key = keyboard.Controller()
        self.mouse = mouse.Controller()

    def label(self):
        return "hold [" + self.vals[0] + "] for " + str(self.vals[1]) + " seconds"

    def save(self, vals): #returns true if successful, false otherwise
        key = vals[0].get()
        time = vals[1].get()

        self.checkintbounds(time) #check bounds

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
        Command.__init__(self, "Press", ["a"], True, "Button") #default value: press a
        self.key = keyboard.Controller()
        self.mouse = mouse.Controller()

    def label(self):
        return "press [" + self.vals[0] + "]"

    def save(self, vals):
        key = vals[0].get()

        self.vals = [key]
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
        Command.__init__(self, "Release", ["a"], True, "Button") #default value: release a
        self.key = keyboard.Controller()
        self.mouse = mouse.Controller()

    def label(self):
        return "release [" + self.vals[0] + "]"

    def save(self, vals):
        key = vals[0].get()

        self.vals = [key]
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
        Command.__init__(self, "Type", ["abc"], False, "Button") #default value: type "abc"
        self.controller = keyboard.Controller() #you cant type mouse buttons, so we just need keyboard

    def label(self):
        return "type " + self.vals[0]

    def save(self, vals):
        string = vals[0].get()

        self.vals = [string]
        return True

    def run(self):
        self.controller.type(self.vals[0])
'''
MOVE MOUSE
name = "Move Mouse"
vals[0] = x coord to move to (0 <= x <= width)
vals[1] = y coord to move to (0 <= y <= height)
'''
class MoveMouse(Command):
    def __init__(self):
        Command.__init__(self, "Move Mouse", [0, 0], False, "Mouse") #default values: move mouse to (0,0) (top left)
        self.controller = mouse.Controller()

    def label(self):
        return "move mouse to (" + str(self.vals[0]) + ", " + str(self.vals[1]) + ")"

    def save(self, vals):
        x = vals[0].get()
        y = vals[1].get()

        self.vals = [x, y]
        return True

    def run(self):
        x = self.vals[0]
        y = self.vals[1]

        self.controller.position = (x, y) #manually set position of mouse

'''
DRAG MOUSE
name = "Drag Mouse"
val[0] = where to drag mouse x coord to (0 to height)
val[1] = where to drag mouse y coord to (0 to height)
'''
class DragMouse(Command):
    def __init__(self):
        Command.__init__(self, "Drag Mouse", [0, 0], True, "Mouse") #default values: move mouse to (0,0) (top left)
        self.controller = mouse.Controller()
        self.time = 1 #how many seconds to drag before completion
        self.frames = 40 #how many frames in the drag animation (im treating this as an animation)

    def label(self):
        return "drag mouse to (" + str(self.vals[0]) + ", " + str(self.vals[1]) + ")"

    def save(self, vals):
        x = vals[0].get()
        y = vals[1].get()

        self.vals = [x, y]
        return True

    def getexectime(self):
        return self.time #drag always takes 1 second

    def run(self, keydict):
        interval = self.time/self.frames

        #get old and new pos
        oldx = self.controller.position[0]
        oldy = self.controller.position[1]
        newx = self.vals[0]
        newy = self.vals[1]

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
        self.controller.press(keydict["lmb"]) #left moues button to drag

        for i in range(0, self.frames):
            x -= dx #im not gonna lie, idk why im subtracting, it just kinda works yk
            y -= dy
            self.controller.position = (x, y) #move the mouse
            t.sleep(interval)
        
        #snap to actual position
        self.controller.position = (newx, newy)

        #finally, release the drag
        self.controller.release(keydict["lmb"])
        
'''
SCROLL MOUSE (equivalent to 2-finger movement on touchpad)
vals[0] = amount of steps (int)
vals[1] = direction (up, right, down, left)
'''
class Scroll(Command):
    def __init__(self):
        Command.__init__(self, "Scroll Mouse", [1, "down"], False, "Mouse") #default values: scroll mouse 1 step down
        self.controller = mouse.Controller()

    def label(self):
        step = self.vals[0]
        direction = self.vals[1]

        return "scroll mouse " + str(step) + " steps " + direction

    def save(self, vals):
        steps = vals[0].get()
        direction = vals[1].get()

        self.checkintbounds(steps)

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
        Command.__init__(self, "Sleep", [1], False, "Other") #default value: sleep for 1 second

    def label(self):
        return "sleep for " + str(self.vals[0]) + " seconds"

    def save(self, vals):
        sec = vals[0].get()

        self.checkintbounds(sec) #check int bounds

        self.vals = [int(sec)]
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
class Repeat(Command): #TODO: indent the lines below on listbox?
    def __init__(self):
        Command.__init__(self, "Repeat", [1, 1], False, "Other") #default value: sleep for 1 second

    def label(self):
        return "repeat next " + str(self.vals[1]) + " lines " + str(self.vals[0]) + " times"

    def save(self, vals):
        rep = vals[0].get()
        lines = vals[1].get()

        self.checkintbounds(rep) #check int bounds
        self.checkintbounds(lines)

        self.vals = [int(rep), int(lines)]
        return True
    
    def getexectime(self):
        return 0 #doesnt really matter, not part of runlist

    def run(self, lines):
        for i in range(0, self.vals[0]):
            for j in lines:
                j.run()
        
'''
tkinter application to simulate user inputs with pynput (keyboard/mouse)
'''
class Macro:
    def __init__(self):
        self.commands = [] #list of commands to execute
        self.curr = None #keep track of the index of our current stock
        self.clipboard = [] #keeps track of all objects on clipboard
        self.intbounds = (0, 100) #TODO: use this

        self.title = "Macro Editor" #name of application
        self.wait = 0.5 #seconds in-between each command
        self.vals = [] #this will transfer gui info to commands

        self.root = tk.Tk() # Create a window
        self.root.title(self.title)
        self.root.geometry("800x800+200+50")
        self.root.resizable(width=False, height=False)

        #set up grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        #make the notebook for different tabs
        self.notebook = Notebook(self.root, height=700)
        self.notebook.grid(sticky="NESW")

        #make the frames for the tab container
        self.program_tab()
        self.history_tab()

        #make the menu widgets
        self.menu()

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
        self.list.bind("<<ListboxSelect>>", self.listbox_select)
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

        #dynamic text label
        self.mousevar = tk.StringVar()
        self.mousevar.set("Mouse Position: (0,0)")

        mouselabel = Label(metricframe, textvariable=self.mousevar, width=25)
        mouselabel.grid(row=0, column=0)

        #dynamic text label 2
        self.exectime = tk.StringVar()
        self.exectime.set("Execution Time: 0s")

        exectimelabel = Label(metricframe, textvariable=self.exectime, width=25)
        exectimelabel.grid(row=1, column=0)

        #for managing metrics related to program itself (title of program, execution time interval)
        manageframe = LabelFrame(tab, text="Manage", width=50)
        manageframe.grid(row=1, column=1, sticky='NESW', padx=5, pady=5)
        manageframe.grid_propagate(False)

        # 5 x 2 grid
        manageframe.rowconfigure(0, weight=1)
        manageframe.rowconfigure(1, weight=1)
        manageframe.rowconfigure(2, weight=1)
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

        #save button
        self.managesave = Button(manageframe, text="Save", command=self.update_program)
        self.managesave.grid(row=2, column=0, columnspan=2)

        #by default its disabled
        self.managesave["state"] = "disabled"

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        self.titlevar.trace("w", lambda x,y,z : self.enablesave(title2, self.title, self.managesave))
        self.waitvar.trace("w", lambda x,y,z : self.enablesave(wait2, self.wait, self.managesave))

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

    def history_tab(self): #create history page for notebook
        tab = Frame(self.notebook)
        tab.grid()
        self.notebook.add(tab, text="History")

        #set up grid
        tab.rowconfigure(0, weight=1)

        #text box
        self.historylog = tk.Text(tab)
        self.historylog.grid(row=0, sticky="NESW")

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
    
    def load_curr(self, i): #update the GUI to correctly handle the current seletion (at index i)
        self.curr = i

        #delete current manage tab children
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

    def load_editdefault(self): #default frame for when no command is selected
        none = Label(self.edit, text="No Command Selected")
        none.grid(row=0, column=0) #3x3 grid, so this label is in the middle
    
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

            if cmd.name == "Repeat":
                repeat = cmd.vals[0]
                lines = cmd.vals[1]
                for n in range(0, repeat - 1): #runlist will append everything again after, so -1 repeat
                    for j in range(i + 1, i + lines + 1):
                        if j < len(self.commands): #only add if its in the list
                            runlist.append(self.commands[j])
            else: #omit the repeat commands from running
                runlist.append(cmd) #if its not a repeat command, just add it
        
        return runlist


    def update_program(self, log = True): #update program metrics from Tk Vars
        self.root.title(self.titlevar.get())
        self.wait = self.waitvar.get()

        #disable the save button again
        self.managesave["state"] = "disabled"

        #update history log
        if log: #by default it will log, but if its part of another sequence (i.e. import txt) it wont
            self.update_history("program", None) #no val for this entry

    def update_mouse(self, x, y): #update mouse position from listener
        mousepos = (int(x), int(y))
        self.mousevar.set("Mouse Position: " + str(mousepos))

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
            "add":"added _ command",
            "edit":"edited _ command",
            "program":"updated program details"
        }
        label = labels[idx].replace("_", str(val))
        self.historylog.insert(tk.END, label + "\n")

    #compares a dynamic variable to its starting value. if they differ, enable the save button to be pressed
    def enablesave(self, var, val, save): #var = variable to check, val = default value, save = button to change
        if var.get() == val:
            save["state"] = "disabled"
        else:
            save["state"] = "normal"

    def delete(self, log = True): #deletes a selection of commands in the listbox
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

    def copy(self, log = True): #copy commands indices to the clipboard
        self.clipboard = [] #reset clipboard
        for i in self.list.curselection():
            self.clipboard.append(self.commands[i]) #add everything to keyboard
        
        #add to history log if anything was copied and if its not part of a cut (thats handled separately)
        clipboard_length = len(self.list.curselection())
        if clipboard_length > 0 and log:
            self.update_history("copy", clipboard_length)

    def paste(self, log = True): #paste all indices from clipboard after current selection
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
    
    def cut(self, log = True): #copies selection and deletes it
        #store length for history log
        cut_len = len(self.list.curselection())

        #tell the functions that they are part of a cut command
        self.copy(False) #no matter what, it shouldnt log anything
        self.delete(False)

        #now add to history log
        if log:
            self.update_history("cut", cut_len)

    
    def clear(self, log = True): #reset all dynamic vals
        self.curr = None
        self.program_len = self.list.size() #store for history log
        self.list.delete(0, self.list.size())
        self.commands = []
        self.vals = []
        
        self.waitvar.set(0.5)
        self.titlevar.set("Macro Editor")

        #now update the program to display it
        self.load_curr(self.curr)
        self.update_exectime()
        self.update_program(log) #if this function shouldnt log, update_program shouldnt log either

        #update history log
        if log:
            self.update_history("clear", None) #no val for this entry
    
    def save(self, log = True): #save the edits to the current command
        cmd = self.commands[self.curr]

        #save changes
        cmd.save(self.vals)

        #disable save button (we know which one it is bc we're in the edit menu)
        self.editsave["state"] = "disabled"
        
        #update label
        self.list.delete(self.curr)
        self.list.insert(self.curr, cmd.label())

        #update execution time
        self.update_exectime()

        #update history log
        if log:
            self.update_history("edit", str(cmd.name).lower())
    
    def run(self, log = True): #run the program!!
        runlist = self.load_runlist() #get the runlists

        for i in range(0, len(runlist)):
            cmd = runlist[i]

            if cmd.usekeydict: #pass in keydict if the command needs it 
                cmd.run(self.keydict)
            else:
                cmd.run()

            if i < len(self.commands) - 1: #sleep for self.wait time if its not the last command
                t.sleep(self.wait)
        
        #update history log
        if log:
            self.update_history("run", len(self.commands))
    
    def listbox_toggle(self, event): #toggle when the mouse is over the listbox (and items can be selected)
        self.inlistbox = not(self.inlistbox)
    
    def listbox_add(self, x, log = True): #add command to the listbox
        self.list.insert(len(self.commands), x.label())
        self.commands.append(x)

        #now update execution time
        self.update_exectime()

        #update history log
        if log:
            self.update_history("add", str(x.name).lower())

    def listbox_select(self, event): #handles a new stock being selected in listbox
        curr = self.list.curselection() #returns a tuple
        if self.inlistbox: #only allow changes if in the listbox
            if len(curr) == 1: #single selection
                index = curr[0] #since the listbox only allows single selection, the tuple only has 1 item
            else: #either multiple selection or no selection (you cant edit then)
                index = None
            self.load_curr(index)

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

        val1 = tk.IntVar()
        val1.set(self.commands[self.curr].vals[1])
        self.vals.append(val1)

        c3 = Spinbox(frame, from_=1, to=100, textvariable=self.vals[1], width=5)
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

        c1 = Entry(frame, textvariable=self.vals[0], width=5)
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

        c0 = Label(frame, text="move mouse to (")
        c0.grid(row=0, column=0)

        val0 = tk.IntVar()
        val0.set(self.commands[self.curr].vals[0])
        self.vals.append(val0)
        
        #x bounds: 0 to width of screen
        c1 = Spinbox(frame, textvariable=self.vals[0], from_=0, to=self.root.winfo_screenwidth(), width=5) 
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))

        c2 = Label(frame, text=", ")
        c2.grid(row=0, column=2)

        val1 = tk.IntVar()
        val1.set(self.commands[self.curr].vals[1])
        self.vals.append(val1)

        #y bounds: 0 to height of screen
        c3 = Spinbox(frame, textvariable=self.vals[1], from_=0, to=self.root.winfo_screenheight(), width=5) 
        c3.grid(row=0, column=3)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val1.trace("w", lambda x,y,z : self.enablesave(c3, self.commands[self.curr].vals[1], self.editsave))

        #y bounds: 0 to height of screen
        c4 = Label(frame, text=")")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the save and delete button at the bottom

    def dragmouse(self): #create dragmouse object
        cmd = DragMouse()
        self.listbox_add(cmd)
    
    def load_dragmouse(self): #load dragmouse frame onto edit frame
        frame = self.edit

        c0 = Label(frame, text="drag mouse to (")
        c0.grid(row=0, column=0)

        val0 = tk.IntVar()
        val0.set(self.commands[self.curr].vals[0])
        self.vals.append(val0)
        
        #x bounds: 0 to width of screen
        c1 = Spinbox(frame, textvariable=self.vals[0], from_=0, to=self.root.winfo_screenwidth(), width=5) 
        c1.grid(row=0, column=1)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val0.trace("w", lambda x,y,z : self.enablesave(c1, self.commands[self.curr].vals[0], self.editsave))

        c2 = Label(frame, text=", ")
        c2.grid(row=0, column=2)

        val1 = tk.IntVar()
        val1.set(self.commands[self.curr].vals[1])
        self.vals.append(val1)

        #y bounds: 0 to height of screen
        c3 = Spinbox(frame, textvariable=self.vals[1], from_=0, to=self.root.winfo_screenheight(), width=5) 
        c3.grid(row=0, column=3)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val1.trace("w", lambda x,y,z : self.enablesave(c3, self.commands[self.curr].vals[1], self.editsave))

        #y bounds: 0 to height of screen
        c4 = Label(frame, text=")")
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

        val0 = tk.IntVar()
        val0.set(self.commands[self.curr].vals[0])
        self.vals.append(val0)

        c1 = Spinbox(frame, textvariable=self.vals[0], from_=1, to=100, width=5)
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

            text.pop(0) #for filler line

            self.titlevar.set(title)
            self.waitvar.set(wait)
            self.update_program(False)

            for i in text: #now we transcribe commands
                i = i.split(",")

                name = i[0]
                v0 = i[1]
                v1 = None
                if len(i) > 2:
                    v1 = i[2]
                
                try:
                    if name == "Click": #same as self.click() but it saves the new data to the obj before adding it
                        cmd = Click()

                        #cast to tk.StringVar/tk.IntVar objects so that it can be processed better by save()
                        var0 = tk.StringVar(value=str(v0))
                        var1 = tk.IntVar(value=int(v1))
                        cmd.save([var0, var1])

                        self.listbox_add(cmd, False)
                    if name == "Hold":
                        cmd = Hold()

                        var0 = tk.StringVar(value=str(v0))
                        var1 = tk.IntVar(value=int(v1))
                        cmd.save([var0, var1])

                        self.listbox_add(cmd, False)
                    if name == "Press":
                        cmd = Press()
                        
                        var0 = tk.StringVar(value=str(v0))
                        cmd.save([var0])

                        self.listbox_add(cmd, False)
                    if name == "Release":
                        cmd = Release()
                        
                        var0 = tk.StringVar(value=str(v0))
                        cmd.save([var0])

                        self.listbox_add(cmd, False)
                    if name == "Type":
                        cmd = Type()
                        
                        var0 = tk.StringVar(value=str(v0))
                        cmd.save([var0])

                        self.listbox_add(cmd, False)
                    if name == "Move Mouse":
                        cmd = MoveMouse()
                        
                        var0 = tk.IntVar(value=int(v0))
                        var1 = tk.IntVar(value=int(v1))
                        cmd.save([var0, var1])

                        self.listbox_add(cmd, False)
                    if name == "Drag Mouse":
                        cmd = MoveMouse()
                        
                        var0 = tk.IntVar(value=int(v0))
                        var1 = tk.IntVar(value=int(v1))
                        cmd.save([var0, var1])

                        self.listbox_add(cmd, False)
                    if name == "Scroll Mouse":
                        cmd = Scroll()

                        var0 = tk.IntVar(value=int(v0))
                        var1 = tk.StringVar(value=str(v1))
                        cmd.save([var0, var1])

                        self.listbox_add(cmd, False)
                    if name == "Sleep":
                        cmd = Sleep()
                        
                        var0 = tk.IntVar(value=int(v0))
                        cmd.save([var0])

                        self.listbox_add(cmd, False)
                    if name == "Repeat":
                        cmd = Repeat()

                        var0 = tk.IntVar(value=int(v0))
                        var1 = tk.IntVar(value=int(v1))
                        cmd.save([var0, var1])

                        self.listbox_add(cmd, False)
                
                except TypeError: #just dont add it if theres a casting error
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
        text.append("")

        #now put the commands
        for i in self.commands:
            s = str(i.name) + "," + str(i.vals[0])
            if len(i.vals) > 1:
                s += "," + str(i.vals[1])
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