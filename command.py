#Lucas Ross 5 Jan 2023

import pynput.keyboard as keyboard #Listener, Button, Controller
import pynput.mouse as mouse #Listener, Button, Controller
import time as t

'''
COMMAND
generic class for command objects
'''
class Command:
    def __init__(self, id, name, vals, dict, typestr):
        self.name = str(name) #identification var
        self.id = id #unique id for each command
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
    def __init__(self, id):
        Command.__init__(self, id, "Click", [None, None], "k", "Button")
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
    def __init__(self, id):
        Command.__init__(self, id, "Hold", [None, None], "k", "Button")
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
    def __init__(self, id):
        Command.__init__(self, id, "Press", [None], "k", "Button")
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
    def __init__(self, id):
        Command.__init__(self, id, "Release", [None], "k", "Button")
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
    def __init__(self, id):
        Command.__init__(self, id, "Type", [None], "n", "Button")
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
    def __init__(self, id):
        Command.__init__(self, id, "Move Mouse", [None], "m", "Mouse")
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
    def __init__(self, id):
        Command.__init__(self, id, "Drag Mouse", [None], "m", "Mouse")
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
    def __init__(self, id):
        Command.__init__(self, id, "Scroll Mouse", [None, None], "n", "Mouse")
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
    def __init__(self, id):
        Command.__init__(self, id, "Sleep", [None], "n", "Other")

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
    def __init__(self, id):
        Command.__init__(self, id, "Repeat", [None, None], "n", "Other")

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