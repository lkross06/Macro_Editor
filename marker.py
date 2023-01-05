#Lucas Ross 5 Jan 2023

import random as rand

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