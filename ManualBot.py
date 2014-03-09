#!/usr/bin/env python

import sys, os

sys.stderr = open(os.devnull, 'w') #The judge didn't like having any output, even on stderr

import kivy
kivy.require('1.8.0')

#prevent a lot of the output
from kivy.config import Config
Config.set('kivy', 'log_enable', 0)
Config.set('kivy', 'log_level', 'critical')

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.uix.bubble import Bubble
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

#This way we don't need an external .kv file
Builder.load_string('''
<SpleefGame>:
    canvas.before:
        Color: 
            rgba: .5,.5,.5,1
        Rectangle:
            size: self.size
            pos: self.pos
    grid: grid
    FloatLayout:
        size: root.size
        SpleefGrid:
            id: grid
            size_hint_y: None
            y: 50
            height: root.height - self.y
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1,None
            height: 50
            Label:
                size_hint_x: .10
                text: "Legend:"
            Label:
                color: 0,0,0,1
                size_hint_x: .15
                text: "Normal Block"
                canvas.before:
                    Color:
                        rgb: 1,1,1
                    Rectangle:
                        size: self.width - 10, self.height - 10
                        pos: self.x + 5, self.y + 5
            Label:
                size_hint_x: .15
                text: "Broken Block"
                canvas.before:
                    Color:
                        rgb: 0,0,0
                    Rectangle:
                        size: self.width - 10, self.height - 10
                        pos: self.x + 5, self.y + 5
            Label:
                color: 0,0,0,1
                size_hint_x: .15
                text: "Can Break"
                canvas.before:
                    Color:
                        rgb: 1,.8,.8
                    Rectangle:
                        size: self.width - 10, self.height - 10
                        pos: self.x + 5, self.y + 5
            Label:
                color: 0,0,0,1
                size_hint_x: .15
                text: "Can Move"
                canvas.before:
                    Color:
                        rgb: .8,.8,1
                    Rectangle:
                        size: self.width - 10, self.height - 10
                        pos: self.x + 5, self.y + 5
            Label:
                size_hint_x: .10
                text: "Time: " + str(root.time)
            Button:
                size_hint: .20,None
                height: 50
                text: "Done Turn"
                on_press: grid.get_input()

<SpleefGrid>:
    spacing: 1.5
    cols: 12
    rows: 12
    canvas.before:
        Color:
            rgba: .1, .3, .1, .51
        Rectangle:
            size: self.size
            pos: self.pos
    padding: 0,0,0,0

<SpleefCell>:
    size: self.size
    pos: 0,0
    canvas.before:
        Color:
            rgb: (0,0,0) if self.broken else ((.8,1,.8) if self.selected else ((.8,.8,1) if self.canmove else ((1,.8,.8) if self.canbreak else (1,1,1))))
        Rectangle:
            size: self.size

<Bot>:
    pos: self.size
    size: self.size
    canvas.after:
        Color:
            rgb: self.r,self.g,self.b
        Ellipse:
            id: circle
            size: self.width*.9 if self.width < self.height else self.height*.9, self.width*.9 if self.width < self.height else self.height*.9
            pos: (self.width - (self.width*.9 if self.width < self.height else self.height*.9)) / 2, (self.height - (self.width*.9 if self.width < self.height else self.height*.9)) / 2

<Options>:
    size_hint: 1, None
    size: 125,50
    movebutton: movebutton
    breakbutton: breakbutton
    BubbleButton:
        id: movebutton
        text: 'Move'
        on_press: root.move()
    BubbleButton:
        id: breakbutton
        text: 'Break'
        on_press: root.break_block()
''')

class Options(Bubble):
    cell = ObjectProperty(None)
    movebutton = ObjectProperty(None)
    breakbutton = ObjectProperty(None)

    def move(self): #Moves to the specified location
        print "m " + str(self.cell.col) + " " + str(self.cell.row)
        self.parent.remove_widget(opts)
        self.cell.selected = False
        #If only moved a manhattan distance of 1 then let them break blocks still
        if abs(self.cell.col - self.cell.parent.bots[0].col) + abs(self.cell.row - self.cell.parent.bots[0].row) < 2:
            self.cell.parent.bots[0].moved = True
            self.cell.parent.bots[0].move(self.cell.col, self.cell.row)
        else: #They moved a manhattan distance of 2; end turn
            self.cell.parent.get_input()

    def break_block(self): #Breaks the selected block and ends the turn
        print "b " + str(self.cell.col) + " " + str(self.cell.row)
        self.parent.remove_widget(opts)
        self.cell.selected = False
        self.cell.parent.get_input()

opts = Options()

class Bot(Widget):
    row = NumericProperty(-10)
    col = NumericProperty(-10)
    sg = ObjectProperty(None)
    r = NumericProperty(0)
    g = NumericProperty(0)
    b = NumericProperty(0)
    moved = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(Bot, self).__init__( **kwargs)
        self.move(self.col, self.row)
        if self.id == "bot0": #Update cells each time your bot changes position
            for i in self.sg.grid:
                for j in i:
                    self.bind(row=j.update, col=j.update)

    def move(self, x, y, newturn=False): #Move bot to a new location
        self.sg.grid[self.row][self.col].remove_widget(self)
        self.col = x
        self.row = y
        self.sg.grid[self.row][self.col].add_widget(self)
        if self.id == "bot0" and self.moved and newturn: #If you had previously moved and broken a block restore overlay
            self.moved = False
            for i in self.sg.grid:
                for j in i:
                    j.update(self)

    def remove(self): #This bot died
        self.sg.grid[self.row][self.col].remove_widget(self)

class SpleefCell(RelativeLayout):
    row = NumericProperty(0)
    col = NumericProperty(0)
    broken = BooleanProperty(False)
    selected = BooleanProperty(False)
    canmove = BooleanProperty(False)
    canbreak = BooleanProperty(False)
    bothere = BooleanProperty(False)

    def on_touch_down(self, touch):
        #Make sure this cell was clicked
        pos = self.to_local(*touch.pos)
        if pos[0] >= 0 and pos[0] < self.width and pos[1] >= 0 and pos[1] < self.height:
            if opts.parent is not None: #If the bubble menu is already open close it
                opts.parent.remove_widget(opts)
                opts.cell.selected = False
            elif not self.bothere and not self.broken and (self.canbreak or self.canmove): #Don't open it on cells that you can't do any actions on
                opts.clear_widgets()
                #Only show options you can do
                if self.canmove: opts.add_widget(opts.movebutton)
                if self.canbreak: opts.add_widget(opts.breakbutton)
                self.parent.add_widget(opts)
                opts.pos = touch.pos
                opts.center_x = touch.x
                pos_start = 'bottom_'
                pos_end = 'mid'
                if opts.y + opts.height > self.parent.height + self.parent.y: #Bubble is too high
                    opts.y -= opts.height
                    pos_start = 'top_'
                if opts.x + opts.width > self.parent.width + self.parent.x: #Bubble is too far right
                    opts.x -= opts.width / 2
                    opts.center_y = touch.y
                    pos_start = 'right_'
                if opts.x < self.parent.x: #Bubble is too far left
                    opts.x += opts.width / 2
                    opts.center_y = touch.y
                    pos_start = 'left_'
                opts.arrow_pos = pos_start + pos_end
                opts.cell = self
                self.selected = True

    def update(self, bot, *args): #Show the proper overlay
        if abs(self.col - bot.col) + abs(self.row - bot.row) <= 2 and not bot.moved: self.canmove = True
        else: self.canmove = False
        if abs(self.col - bot.col) <= (1 if bot.moved else 2) and abs(self.row - bot.row) <= (1 if bot.moved else 2): self.canbreak = True
        else: self.canbreak = False
        if self.col == bot.col and self.row == bot.row: self.bothere = True
        else: self.bothere = False


class SpleefGrid(GridLayout):
    grid = ListProperty([])
    bots = ListProperty([None, None, None, None])
    maxtime = NumericProperty(0)

    def __init__(self, **kwargs):
        kwargs.setdefault('cols', 12)
        kwargs.setdefault('rows', 12)
        super(SpleefGrid, self).__init__( **kwargs)
        Clock.schedule_once(self.get_input, 2)
        self.bind(rows=self.rebuild, cols=self.rebuild)
        self.rebuild()

    def rebuild(self, *args): #Initialize the grid
        if self.cols > 0 and self.rows > 0:
            self.grid = []
            self.clear_widgets()
            for i in range(self.cols):
                row = []
                for j in range(self.rows):
                    sc = SpleefCell(col=j, row=i)
                    row.append(sc)
                    self.add_widget(sc)
                self.grid.append(row)

    def get_input(self, *args):
        print("d") #Either finished setting up or finished turn
        info = raw_input().split(" ")
        while info[0] != "d":
            if info[0] == "g": #Set the grid size
                self.cols = int(info[1])
                self.rows = int(info[2])
            if info[0] == "t": #Set the max time
                self.maxtime = int(info[1])
                Clock.schedule_interval(self.parent.parent.decrease_time, 1)
            if info[0] == "p": #Set bot location
                if len(self.bots) <= int(info[1]) or self.bots[int(info[1])] is None:
                    r = 0
                    g = 0
                    b = 0
                    if int(info[1]) == 0: r = 1
                    if int(info[1]) == 1: b = 1
                    if int(info[1]) == 2: g = 1
                    if int(info[1]) == 3: 
                        r = 1
                        g = 1
                    self.bots[int(info[1])] = Bot(id="bot"+info[1], sg=self, r=r, g=g, b=b)
                    self.bots[int(info[1])].move(int(info[2]), int(info[3]))
                else:
                    self.bots[int(info[1])].move(int(info[2]), int(info[3]), True)
            if info[0] == "r": #A bot has died
                self.bots[int(info[1])].remove()
            if info[0] == "b": #A block has been broken
                self.grid[int(info[2])][int(info[1])].broken = True
            info = raw_input().split(" ")
        self.parent.parent.time = self.maxtime/1000

class SpleefGame(Widget):
    time = NumericProperty(0)

    def decrease_time(self, *args):
        self.time -= 1

game = SpleefGame()

class SpleefApp(App):
    def build(self):
        self.title = "Spleef Game"
        return game

SpleefApp().run()