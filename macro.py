#Lucas Ross 14 Dec 2022

import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog as fd
import pynput.keyboard as keyboard #Listener, Button, Controller
import pynput.mouse as mouse #Listener, Button, Controller
import time as t
import os
from command import * #import from command.py
from marker import * #import from marker.py

'''
TODO LIST
- fix gui css
- use tk filedialog to add alerts
- add commands that are like functions (allow user to customize their own commands, like scratch)
- idk why but pressing caps lock triggers a zsh: trace trap
- trace
'''

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
        self.r = 4 #4px radius of circles in marker canvas

        #handles quitting threads
        self.quit = False

        self.uniqueid = 0 #each command will have a unique numerical id (does not correlate to position)

        self.title = "Macro Editor" #name of application
        self.wait = 0.5 #seconds in-between each command
        self.hotkey = None #run program when this hotkey is pressed
        self.mh = "space" #add a marker when this hotkey is pressed and the marker tab is active
        self.mhgood = True #checks to see if a marker can be added on the first press of self.mh (prevent hold)
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
        self.keydict["space"] = keyboard.Key.space
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
        self.root.bind('<Motion>', self.update_mouse) #on mouse movement, pynput retrieves mouse position again

        #add keyboard listener
        keylistener = keyboard.Listener(on_press=self.handle_key_press, on_release=self.handle_key_release)
        keylistener.start()

        #start the main loop (has to be in the main thread)
        self.root.mainloop()

        #stop thread after loop closes
        keylistener.stop()

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

        #prevents markers on edge from being cut off
        w += self.r * 2
        h += self.r * 2

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
        if type(key) == keyboard.KeyCode: #its either key.Key._ or keyboard.KeyCode._, and the former is handled alr
            key = self.unshift(key.char)

        vals = list(self.keydict.values())
        keys = list(self.keydict.keys())

        for i in range(0, len(keys)): #see if any of the key values in self.keydict match the pressed key
            if key == vals[i] and not(keys[i] in self.keys): #make sure the key isnt duplicated
                key = keys[i] #use for checking hotkeys later (hotkeys follow keys of keydict system)
                self.keys.append(keys[i])

        #check if mh was pressed and its on the marker tab and its the first time mh has been pressed (not held)
        if key == self.mh and self.get_active_tab() == "Marker" and self.mhgood:
            self.add_marker()
            self.mhgood = False

        #now check if hotkey was pressed
        if self.hotkey != None and key == self.hotkey:
            self.run()
    
        self.update_key() #update the GUI

    def handle_key_release(self, key):
        if type(key) == keyboard.KeyCode: #see handle_key_press
            key = self.unshift(key.char)
        
        vals = list(self.keydict.values())
        keys = list(self.keydict.keys())
        
        for i in range(0, len(keys)):
            if key == vals[i]: #check special keys
                if keys[i] in self.keys:
                    self.keys.remove(keys[i])

        #if mh was released and its in marker tab, then enable marker add
        if key == self.mh and self.get_active_tab() == "Marker":
            self.mhgood = True

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

    def update_mouse(self, e): #update mouse position when mouse moves
        con = mouse.Controller()
        pos = (int(con.position[0]), int(con.position[1]))
        self.mousevar.set("Mouse Position: " + str(pos))
        
    def update_key(self):
        strkeys = ""

        #format the things to be pressed
        for i in range(0, len(self.keys)):
            strkeys += self.keys[i]
            if i < len(self.keys) - 1: #dont add this on the last one or it looks weird
                strkeys += "+"

        self.keyvar.set("Keys Pressed: " + strkeys)

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
                self.list.itemconfig(i,{'fg':'white'}) # TODO: whats the default? cause this doesnt work on light mode
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
            r = self.r - 1 #subtract 1 to account for 1px border (width = 1 by default)

            #add r to all coordinates to shift it right+down (counteract the border upsizing)
            self.mcanvas.create_oval(cx - r + r, cy - r + r, cx + r + r, cy + r + r, outline = "#000000", fill = i.color) #center point at (cx, cy)

            #now add the text

            #offset values for text (by default, it will be above the marker by n px in the x/y direction)
            n = 8 #px away from center
            ox = cx #offset x
            oy = cy - n #offset y

            a = "" #anchor -> by default it will be centered around (ox, oy), but we can change it

            tx = 20 #threshold for x values (when to apply changes)
            ty = 20 #threshold for y values (when to apply changes)

            #possible anchor positions: n, ne, e, se, s, sw, w, nw, center
            #since "n" and "s" go first, we handle y coords then x coords

            if cy <= ty: #too high
                oy += (n * 2) #since default value is -n
                a += "n"
            elif cy >= ch - ty: #too far down
                #offset y doesnt need to change, by default oy = cy - n
                a += "s"

            if cx <= tx: #too far left
                ox += n
                a += "w"
            elif cx >= cw - tx: #too far right
                ox -= n
                a += "e"

            if a == "": #if no alterations were added to anchor, make it go to center
                a ="center"

            #by default, the text is centered around x,y
            self.mcanvas.create_text(ox, oy, \
                text= i.name + " (" + str(sx) + ", " + str(sy) + ")", \
                fill = "#000000", \
                anchor = a)

    #compares a dynamic variable to its starting value. if they differ, enable the save button to be pressed
    def enablesave(self, var, val, save): #var = variable to check, val = default value, save = button to change
        if var.get() == val:
            save["state"] = "disabled"
        else:
            save["state"] = "normal"

    def get_id(self):
        rtn = self.uniqueid
        self.uniqueid += 1 #get the new unique id
        return rtn

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
        print(runlist)

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
        cmd = Click(self.get_id())
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
        cmd = Hold(self.get_id())
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
        cmd = Press(self.get_id())
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
        cmd = Release(self.get_id())
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
        cmd = Type(self.get_id())
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
        cmd = MoveMouse(self.get_id())
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
        cmd = DragMouse(self.get_id())
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

        c2 = Label(frame, text=" in ")
        c2.grid(row=0, column=2)

        val1 = tk.DoubleVar()
        val1.set(self.commands[self.curr].vals[1])
        self.vals.append(val1)

        c3 = Spinbox(frame, from_=1, to=100, textvariable=self.vals[1], increment=0.1, format="%.1f", width=5)
        c3.grid(row=0, column=3)

        #whenever the variable changes from default val (i.e. the spinbox is updated), enable the save button
        val1.trace("w", lambda x,y,z : self.enablesave(c3, self.commands[self.curr].vals[1], self.editsave))

        c4 = Label(frame, text=" seconds")
        c4.grid(row=0, column=4)

        self.load_editsave(frame) #now put the save and delete button at the bottom

    def scroll(self): #create scroll object
        cmd = Scroll(self.get_id())
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
        cmd = Sleep(self.get_id())
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
        cmd = Repeat(self.get_id())
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

                        #now we gotta cast all the bruhs
                        try:
                            if name == "Click": #same as self.click() but it saves the new data to the obj before adding it
                                cmd = Click(self.get_id())
                                cmd.save([i[1], int(i[2])])
                            if name == "Hold":
                                cmd = Hold(self.get_id())
                                cmd.save([i[1], float(i[2])])
                            if name == "Press":
                                cmd = Press(self.get_id())
                                cmd.save([i[1]])
                            if name == "Release":
                                cmd = Release(self.get_id())
                                cmd.save([i[1]])
                            if name == "Type":
                                cmd = Type(self.get_id())
                                cmd.save([i[1]])
                            if name == "Move Mouse":
                                cmd = MoveMouse(self.get_id())
                                cmd.save([int(i[1])])
                            if name == "Drag Mouse":
                                cmd = DragMouse(self.get_id())
                                cmd.save([int(i[1]), int(i[2])])
                            if name == "Scroll Mouse":
                                cmd = Scroll(self.get_id())
                                cmd.save([int(i[1]), i[2]])
                            if name == "Sleep":
                                cmd = Sleep(self.get_id())
                                cmd.save([float(i[1])])
                            if name == "Repeat":
                                cmd = Repeat(self.get_id())
                                cmd.save([int(i[1]), int(i[2])])
                                
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

Macro() #run the GUI