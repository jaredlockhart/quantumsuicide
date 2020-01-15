##       quantum.suicide.0.1
##
##  Graphics routine for a simulated particle accelerator
##  Jared L Kerim, design, implementation, Copyright 2007, JPL
##  Gerrit Van Woudenberg, production, creative credit
##
##  ***********************************************************
##
##
##  ***********************************************************

##---------------------
## INCLUDES
##---------------------

from pygame import *
from random import random, randint
from time import sleep, time
from math import sin, pi

##---------------------
## CONSTANTS
##---------------------

white = [255, 255, 255]
black = [0, 0, 0]
clear = [255, 0, 255]
active = False
pause = 0.02
shutdown = False
startup = False
command = False
commandchanged = False

##---------------------
## INITIALIZATION
##---------------------


display.init()
font.init()

terminal = font.Font('terminal.ttf', 15)
clockfont = font.Font('terminal.ttf', 20)
countfont = font.Font('terminal.ttf', 15)



screen = Surface([1024, 768])


##-----------------------
## COMMAND FILE LOADING  
##-----------------------

def reverse(items):
    tmp = items[:]
    tmp.reverse()
    return tmp

def loadcmds():
    cmdfile = open('commands.txt', 'r')
    commands = {}
    incmd = False
    cmd = ''
    reply = ''
    for line in cmdfile.readlines():
        if incmd:
            if ';' in line:
                reply += line.strip()[:-1]
                commands[cmd] = reply
                cmd = ''
                reply = ''
                incmd = False
            else:
                reply += line
        else:
            if ':' in line:
                
                incmd = True
                cmd = line.strip()[:-1]
    cmdfile.close()
    return commands

def writecmds(commands):
    cmdfile = open('commands.txt', 'w')
    for cmd, reply in commands.items():
        cmdfile.write(cmd + ':\n')
        cmdfile.write(reply + ';\n\n')
    cmdfile.close()


def loadparticles():
    tmp = open('particles.txt', 'r')
    text = tmp.read()
    tmp.close()
    particles = []
    for line in text.split('\n'):
        if line == '':
            continue
        particles.append([j for j in line.split('\t') if not j == ''])
    return particles
                        
def loadexperiment():
    tmp = open('experiment.txt', 'r')
    text = tmp.read()
    tmp.close()
    experiment = []
    instance = []
    for line in text.split('\n'):
        if line == '': continue
        if '[' in line:
            experiment.append(instance)
            time = float(line.strip()[1:-1])
            instance = [time]
        else:
            instance.append(line.strip())
    experiment.append(instance)
    return experiment[1:]

##---------------------
## MATH UTILITY FUNCTIONS
##---------------------

def bound(value, low, high):
    "Bound a value between low and high"
    if value < low:
        return low
    elif value > high:
        return high
    else:
        return value

def powerset(items):
    "Create the powerset of a set of items"
    result = []
    while len(items) > 0:
        curr = items[0]
        for i in items[1:]:
            if not i == curr:
                result.append((curr, i))
        items = [i for i in items if not i == curr]
    return result

##---------------------
## STATIC GRAPHICS PRIMITIVES
##---------------------

# Graph Background
        
def graphborder(width, height, title):
    "Create the backdrop for a single sensor readout with title and border"
    surf = Surface([width, height])
    surf.fill(black)
    text = terminal.render(title, 0, white)
    surfrect = surf.get_rect()
    textrect = text.get_rect()
    textx = surfrect.centerx - textrect.centerx
    texty = 5
    surf.blit(text, [textx, texty])
    draw.rect(surf, white, [0, 0, width-2, height-2], 2)
    return surf

# Bargraph Primitives
        
def gradient(width, height, delta=10):
    "Create a vertical graded bar of lines"
    surf = Surface((width, height))
    halfx = width / 2
    halfy = height / 2
    for i in range(0, height, height/delta):
            draw.line(surf, white, (width/2, i), (width, i))
    return surf

def drawbar(width, height):
    output = Surface([width, height])
    grad = gradient(width/2, height-1)
    output.blit(grad, [0, 0])
    barheight = -1 * randint(0, height-1)
    barrect = [width/2, height, width/2, barheight]
    draw.rect(output, white, barrect)
    return output

def drawbarlow(width, height):
    output = Surface([width, height])
    grad = gradient(width/2, height-1)
    output.blit(grad, [0, 0])
    barheight = -1 * randint(0, int(0.3 * (height-1)))
    barrect = [width/2, height, width/2, barheight]
    draw.rect(output, white, barrect)
    return output



def drawbargraph(width, height, title, low=False):
    output = graphborder(width, height, title)
    if low:
        bar = drawbarlow(26, height-40)
    else:
        bar = drawbar(26, height-40)
    xpos = width/2 - 15
    ypos = 30
    output.blit(bar, [xpos, ypos])
    return output



# Linegraph Primitives

def matrix(x, y, dx, dy):
    "Create a 2D matrix grid"
    surf = Surface((x+1, y+1))
    surf.fill(black)
    for currx in range(0, x+1, dx):
        if currx == x/2:
            draw.line(surf, white, (currx, 0), (currx, y), 2)
        else:
            draw.line(surf, white, (currx, 0), (currx, y))
    for curry in range(0, y+1, dy):
        if curry == y/2:
            draw.line(surf, white, (0, curry), (x, curry), 2)
        else:
            draw.line(surf, white, (0, curry), (x, curry))
    return surf

def linegraph(width, height, points=20):
    output = matrix(width, height, width/10, height/10)
    points = [(randint(0, width-1), randint(0, height-1)) for i in range(points)]
    for start, stop in powerset(points):
        draw.circle(output, white, start, 2)
        draw.line(output, white, start, stop)
    return output

def linegraphlow(width, height, points=20):
    output = matrix(width, height, width/10, height/10)
    points = [(width/3 + randint(0, int(0.3 * width-1)), height/3 + randint(0, int(0.3 * height-1))) for i in range(points)]
    for start, stop in powerset(points):
        draw.circle(output, white, start, 2)
        draw.line(output, white, start, stop)
    return output


def drawlinegraph(width, height, title, low=False):
    output = graphborder(width, height, title)
    if low:
        tmp = linegraphlow(width-10, height-40)
    else:
        tmp = linegraph(width-10, height-40)
    output.blit(tmp, [5, 30])
    return output

# Singraph Primitives

def sinegraph(width, height, offset, amp):
    "Create a sine graph offset by a float: 0.0 to 1.0"
    surf = Surface((width, height))
    surf.set_colorkey([255, 0, 255])
    surf.fill([255, 0, 255])
    i = 0
    while i < width:
        percent = i/float(width) + offset
        val = -pi + (percent * 2 * pi)
        y = (height/2) + int(sin(val) * amp) 
        draw.circle(surf, white, (i, y), 1)
        i += 3
    return surf


def drawsinegraph(width, height, title, low=False):
    output = graphborder(width, height, title)
    mat = matrix(width-10, height-40, (width-10)/10, (height-40)/10)
    output.blit(mat, [5, 30])
    if low:
        tmp = sinegraph(width-10, height-40, random(), randint(0, height/6))
    else:
        tmp = sinegraph(width-10, height-40, random(), randint(0, height/3))        
    output.blit(tmp, [5, 30])
    return output



##---------------------
## ANIMATED GRAPH PRIMITIVES
##---------------------
            
class graph:
    "An animated vertical bar graph"
    def __init__(self, xpos, ypos, width, height, render, title):
        global screen
        self.rect = Rect([xpos, ypos, width, height])
        self.images = [render(width, height, title) for i in range(30)]
        self.imageslow = [render(width, height, title, True) for i in range(30)]
    def update(self):
        global screen, active
        if active:
            screen.blit(self.images[randint(0, 29)], self.rect.topleft)
        else:
            screen.blit(self.imageslow[randint(0, 29)], self.rect.topleft)



class shell:
    def __init__(self, x, y, width, height):
        self.rect = Rect([x, y, width, height])
        self.img = graphborder(width, height, '-=:SHELL:=-')
        self.blackrect = self.img.get_rect()
        self.blackrect.x += 5
        self.blackrect.width -= 10
        self.blackrect.y += 25
        self.blackrect.height -= 30
        self.lines = ['command>>']
        self.blink = True
        self.blinkcount = 0
        self.blinkmax = 10
        self.img.set_alpha(200)
        self.commands = loadcmds()
        self.time = 0.0
        self.pause = 0.0
        self.wait = False
        self.currmsg = []
        self.input = False
        self.counter = False
        self.countertime = 0.0
        self.countermax = 0.0
        self.counterrate = 0.0
        self.dotp = False
        self.cloops = 0
        self.cloopsmax = 3
        self.dotcount = 0
        self.dotmax = 3
        self.qs = None
        self.loop = []
    def update(self):
        global screen
        self.timed()
        self.render()
        screen.blit(self.img, self.rect.topleft)
    def render(self):
        textimgs = []
        draw.rect(self.img, black, self.blackrect)
        curry = 25
        for line in self.lines:
            img = terminal.render(str(line)[:50], 0, white)
            self.img.blit(img, [5, curry])
            if line == self.lines[0] and self.blink:
                imgrect = img.get_rect()
                cursor = Rect([0, 0, 0, 0])
                cursor.x = imgrect.width + 5
                cursor.y = 25
                cursor.width = 10
                cursor.height = imgrect.height
                draw.rect(self.img, white, cursor)
            curry += 18

            self.blinkcount += 1
            if self.blinkcount > self.blinkmax:
                self.blinkcount = 0
                self.blink = not self.blink
    def timed(self):
        global active, startup, shutdown, command, commandchanged
        if self.input:
            return None
        if self.dotp:
            if self.cloops < self.cloopsmax:
                if self.dotcount < self.dotmax:
                    self.lines[0] += '.'
                    self.dotcount += 1
                else:
                    self.lines[0] = self.lines[0][:-self.dotmax]
                    self.dotcount = 0
                    self.cloops += 1
            else:
                self.lines[0] += '.....EXECUTED'
                self.lines.insert(0, 'command>>')
                self.dotcount = 0
                self.cloops = 0
                self.dotp = False
        if self.counter:
            if self.countertime < self.countermax:
                self.countertime += self.counterrate
                self.lines[0] = str(self.countertime)
                return None
            else:
                self.lines[0] = str(self.countermax)
                self.counter = False
                self.countertime = 0.0
                self.countermax = 0.0
                self.counterrate = 0.0
        if self.wait:
            if len(self.loop) > 0:
                self.lines.insert(0, self.loop[0])
                self.loop = self.loop[1:] + [self.loop[0]]
                return None
            if len(self.currmsg) == 0:
                self.wait = False
                self.time = 0.0
                self.pause = 0.0
                self.lines.insert(0, 'command>>')
                return None
            elif self.pause > 0.0:
                if (time() - self.time) > self.pause:
                    self.time = 0.0
                    self.pause = 0.0
                    return None
            elif '[' in self.currmsg[0]:
                if 'start' in self.currmsg[0]:
                    active = True
                    self.currmsg = self.currmsg[1:]
                elif 'kill' in self.currmsg[0]:
                    shutdown = True
                    self.currmsg = self.currmsg[1:]
                elif 'raise' in self.currmsg[0]:
                    startup = True
                    self.currmsg = self.currmsg[1:]
                elif 'stop' in self.currmsg[0]:
                    active = False
                    self.currmsg = self.currmsg[1:]
                elif 'counter' in self.currmsg[0]:
                    self.counter = True
                    self.countertime = float(self.currmsg[1][1:-1])
                    self.countermax = float(self.currmsg[2][1:-1])
                    self.counterrate = float(self.currmsg[3][1:-1])
                    self.currmsg = self.currmsg[4:]
                    self.lines.insert(0, str(self.countertime))
                elif 'input' in self.currmsg[0]:
                    self.input = True
                    self.currmsg = self.currmsg[1:]
                elif 'qs' in self.currmsg[0]:
                    tmp = int(self.currmsg[0][3:-1])
                    self.qs.count = tmp
                    self.qs.nocount = tmp
                    self.qs.run = True
                    self.currmsg = self.currmsg[1:]
                elif 'shellup' in self.currmsg[0]:
                    command = True
                    self.currmsg = self.currmsg[1:]
                elif 'shelldown' in self.currmsg[0]:
                    command = False
                    commandchanged = True
                    self.currmsg = self.currmsg[1:]
                elif 'begin' in self.currmsg[0]:
                    tmp = 0
                    for i in self.currmsg[1:]:
                        tmp += 1
                        if 'end' in i:
                            break
                        else:
                            self.loop.append(i)
                    self.currmsg = self.currmsg[tmp+1:]
                    return None
                else:
                    self.time = time()
                    self.pause = float(self.currmsg[0][1:-1])
                    self.currmsg = self.currmsg[1:]
                return None
            else:
                self.lines.insert(0, self.currmsg[0])
                self.currmsg = self.currmsg[1:]
    def process(self):
        global active
        cmd = self.lines[0][9:]
        if cmd == 'cmds':
            for i in self.commands.items():
                self.lines.insert(0, str(i))
            self.lines.insert(0, 'command>>')                   
        elif cmd in self.commands:
            reply = self.commands[cmd]
            if '[' in reply:
                self.currmsg = [i.strip() for i in reply.split('\n') if not i == '']
                self.wait = True
                return None
            for i in reverse(self.commands[cmd].split('\n')):
                if i == '': continue
                else:
                    self.lines.insert(0, i)
            self.lines.insert(0, 'command>>')   
        else:
            self.lines.insert(0, 'ACCESSING')
            self.dotp = True               
    def backspace(self):
        self.lines[0] = self.lines[0][:-1]
    def enter(self):
        if self.input:
            self.input = False
        else:
            self.process()
    def space(self):
        self.lines[0] += ' '
    def keypress(self, char):
        self.lines[0] += char


class particlelist:
    def __init__(self, width, height, particles):
        self.rect = Rect([0, 0, width, height])
        self.img = Surface([width, height])
        self.particles = particles
        self.highlight = 0
    def render(self):
        self.img.fill(black)
        curry = 0
        for p in self.particles:
            if curry/18 == self.highlight:
                text = terminal.render(p[0], 0, black, white)
            else:            
                text = terminal.render(p[0], 0, white)
            self.img.blit(text, [5, curry])
            curry += 18
    def up(self):
        if self.highlight >= 1:
            self.highlight -= 1
    def down(self):
        if self.highlight < (len(self.particles) - 1):
            self.highlight += 1

def pairbox(width, height, label, data):
    output = Surface((width, height))
    output.fill(black)
    draw.rect(output, white, [0, 0, width-4, height-4], 2)
    labelimg = terminal.render(label, 0, white)
    dataimg = clockfont.render(data, 0, white)
    output.blit(labelimg, [5, 5])
    datax = width - dataimg.get_rect().width - 15
    output.blit(dataimg, [datax, 18])
    return output

def clock(width, height, time):
    output = Surface((width, height))
    output.fill(black)
    draw.rect(output, white, [0, 0, width-4, height-4], 2)
    tmp = clockfont.render(str(time) + 'nsecs', 0, white)
    output.blit(tmp, [5, 5])
    return output

def experiment(width, height, number):
    output = Surface((width, height))
    output.fill(black)
    draw.rect(output, white, [0, 0, width-4, height-4], 2)
    tmp = clockfont.render('Experiment: ' + str(number), 0, white)
    output.blit(tmp, [5, 5])
    return output


class particledata:
    def __init__(self, width, height, particle):
        self.rect = Rect([0, 0, width, height])
        self.img = Surface([width, height])
        self.particle = particle
        self.render()
    def render(self):
        self.img.fill(black)
        curry = 0
        currd = 0
        for name in ('Name', 'Symbol', 'Electric Charge', 'Weak Charge', 'Weak Isospin', 'Hypercharge', 'Colour Charge', 'Generation', 'Mass'):
            tmp = pairbox(self.rect.width-10, 48, name, self.particle[currd])
            self.img.blit(tmp, [5, curry])
            curry += 50
            currd += 1



class detector:
    def __init__(self, x, y, width, height):
        self.rect = Rect([x, y, width, height])
        self.img = graphborder(width, height, "-=:Particle Detector:=-")
        self.img.set_alpha(200)
        self.particles = loadparticles()
        self.plists = []
        self.plist = None
        self.dwidth = ((width/2) - 10)
        self.dheight = (height-55)
        self.cwidth = ((width/2) - 10)
        self.cheight = 35
        self.details = None
        self.time = 0.0
        self.currlist = 0
        self.experiment = loadexperiment()
        self.run = False
        self.setup()
        self.expmode = False
        self.expcount = 0        
    def setup(self):
        for curr in self.experiment:
            timesig = curr[0]
            particles = curr[1:]
            newp = []
            for p in particles:
                for j in self.particles:
                    if j[0] == p:
                        newp.append(j)
            particles = newp
            plist = particlelist(self.dwidth, self.dheight-20, particles)
            self.plists.append(plist)
        self.plist = self.plists[0]
        self.matchdetails()
    def matchdetails(self):
        self.details = particledata(self.dwidth, self.dheight, self.plist.particles[self.plist.highlight])
    def update(self):
        global screen, active
        self.render()
        screen.blit(self.img, self.rect.topleft)
        self.run = active
        if self.run:
            self.time += random()
        self.matchtime()
    def matchtime(self):
        if self.expmode:
            self.time = self.expcount
        curr = 0
        for e in self.experiment:
            if self.time > e[0]:
                curr += 1
                continue
            else:
                break
        if curr >= len(self.plists):
            self.plist  = self.plists[-1]
            self.matchdetails()
        else:
            self.plist = self.plists[curr]
            self.matchdetails()
    def start():
        self.run = True
    def stop():
        self.run = False
    def render(self):
        self.plist.render()
        self.img.blit(self.plist.img, [5, 65])
        self.img.blit(self.details.img, [self.rect.width/2, 25])
        if self.expmode:
            self.img.blit(experiment(self.cwidth, self.cheight, self.expcount), [10, 25])
        else:
            self.img.blit(clock(self.cwidth, self.cheight, self.time), [10, 25])
    def down(self):
        self.plist.down()
        self.details = particledata(self.dwidth, self.dheight, self.plist.particles[self.plist.highlight])
    def up(self):
        self.plist.up()
        self.details = particledata(self.dwidth, self.dheight, self.plist.particles[self.plist.highlight])
    def right(self):
        self.time += 0.1
    def left(self):
        self.time -= 0.1
        if self.time < 0.0:
            self.time = 0.0

class qsuicide:
    def __init__(self, x, y, width, height):
        self.rect = Rect([x, y, width, height])
        self.img = graphborder(width, height, "-=:QUANTUM SUICIDE:=-")
        self.img.set_alpha(200)
        self.run = False
        self.success = False
        self.count = 0
        self.yescount = 0
        self.nocount = 0
        draw.rect(self.img, white, [160, 35, 220, 35], 2)
        draw.rect(self.img, white, [160, 92, 220, 100], 2)
        tmp = countfont.render("DECAY RESULTS", 0, white)
        self.img.blit(tmp, [210, 100])
    def update(self):
        global screen, active
        self.render()
        screen.blit(self.img, self.rect.topleft)
        if self.run:
            self.count += 1
            self.nocount += 1
        if self.success:
            self.count += 1
            self.yescount += 1
            self.run = False
            self.success = False
    def rendercounter(self):
        text = countfont.render("TEST NUMBER: " + str(self.count), 0, white)
        tmp = text.get_rect()
        tmp.topleft = (190, 42)
        draw.rect(self.img, black, tmp) 
        self.img.blit(text, [190, 42])
    def rendernocounter(self):
        text = countfont.render("NO:  " + str(self.nocount), 0, white)
        tmp = text.get_rect()
        tmp.topleft = (240, 140)
        draw.rect(self.img, black, tmp) 
        self.img.blit(text, [240, 140])
    def renderyescounter(self):
        text = countfont.render("YES:  " + str(self.yescount), 0, white)
        tmp = text.get_rect()
        tmp.topleft = (235, 160)
        draw.rect(self.img, black, tmp)         
        self.img.blit(text, [235, 160])
    def render(self):
        self.rendercounter()
        self.renderyescounter()
        self.rendernocounter()
        
        

##---------------------
## CONTAINMENT CLASS
##---------------------

        
##---------------------            
## SCRATCH PAD
##---------------------
		

graphs = []

##for x in range(0, 900, 50):
##    graphs.append(graph(x, 100, 45, 200, drawsinegraph, "plz"))
##
##for x in range(0, 800, 210):
##    graphs.append(graph(x, 310, 200, 200, drawsinegraph, "plz"))
##
##for x in range(0, 800, 210):
##    graphs.append(graph(x, 520, 200, 100, drawsinegraph, "plz"))


graphs.append(graph(10, 10, 40, 300, drawbargraph, "5µ"))
graphs.append(graph(60, 10, 40, 300, drawbargraph, "15µ"))
graphs.append(graph(110, 10, 40, 300, drawbargraph, "35µ"))
graphs.append(graph(160, 10, 40, 300, drawbargraph, "75µ"))
graphs.append(graph(210, 10, 40, 300, drawbargraph, "-5µ"))
graphs.append(graph(260, 10, 750, 200, drawsinegraph, "GAS IONIZATION µHZ"))
graphs.append(graph(260, 210, 250, 100, drawsinegraph, "UPPER HARMONIC-BAND PASS"))
graphs.append(graph(520, 210, 250, 100, drawsinegraph, "ENVELOPE FILTER"))
graphs.append(graph(780, 210, 230, 100, drawsinegraph, "LOWER HARMONIC-BAND PASS"))
graphs.append(graph(10, 320, 300, 200, drawlinegraph, "M.LENSE ATTENUATION"))
for x in range(320, 600, 60):
    graphs.append(graph(x, 320, 50, 200, drawbargraph, str(x) + "Hz"))

graphs.append(graph(610, 320, 300, 100, drawsinegraph, "-5x10^3 µHZ - +5x10^3 µHZ"))
graphs.append(graph(610, 420, 300, 100, drawsinegraph, "-3x10^8 µHZ - +3x10^8 µHZ"))
graphs.append(graph(910, 320, 50, 200, drawbargraph, "+7Hz"))
graphs.append(graph(960, 320, 50, 200, drawbargraph, "-7Hz"))
graphs.append(graph(10, 530, 300, 230, drawlinegraph, "M.LENSE FIELD STRENGTH"))
for x in range(320, 1000, 230):
    graphs.append(graph(x, 530, 230, 100, drawsinegraph, "LENSE " + str(x/230) + " EMF 10^5 HZ"))
    graphs.append(graph(x, 630, 230, 130, drawlinegraph, "LENSE " + str(x/230) + " FIELD EMISSION"))

graphbak = graphs[:]


prompt = shell(25, 120, 400, 500)
browser = detector(440, 120, 550, 500)
experiment = qsuicide(440, 120, 550, 500)
prompt.qs = experiment

##---------------------
## MAIN FUNCTION
##---------------------    


def main():
    global bargraph, terminal, active, screen, pause, prompt, browser, experiment, graphs, shutdown, startup, command, commandshell, commandchanged, graphbak
    output = display.set_mode([1024, 768], HWSURFACE|HWPALETTE|FULLSCREEN|DOUBLEBUF)    

    experimentp = False
    backup = screen.copy()
    leftp = False
    rightp = False
    pausemax = 3
    pausecount = 0.0    
    while 1:
        for e in event.get():
            if e.type == QUIT:
                display.quit()
                return None
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    display.quit()
                    return None
                elif e.key == K_MINUS:
                    shutdown = True                
                elif e.key == K_TAB:
                    active = not active
                elif e.key == K_SPACE:
                    prompt.space()
                elif e.key == K_BACKSPACE:
                    prompt.backspace()
                elif e.key == K_LSHIFT:
                    command = not command
                    commandchanged = True
                elif e.key == K_LCTRL:
                    experimentp = not experimentp
                elif e.key == K_RCTRL:
                    experiment.success = True
                    prompt.loop = []
                elif e.key == K_RETURN:
                    prompt.enter()
                elif e.key == K_UP:
                    browser.up()
                elif e.key == K_DOWN:
                    browser.down()
                elif e.key == K_PAGEUP:
                    browser.time += 5.0
                elif e.key == K_PAGEDOWN:
                    browser.time -= 5.0
                    if browser.time < 0.0:
                        browser.time = 0.0
                elif e.key == K_LEFT:
                    leftp = True
                    browser.expcount -= 1
                    if browser.expcount < 0:
                        browser.expcount = 0
                elif e.key == K_RIGHT:
                    rightp = True
                    browser.expcount += 1
                elif e.key == K_END:
                    browser.time = 0.0
                elif e.key == K_EQUALS:
                    browser.expmode = not browser.expmode                    
                else:
                    char = key.name(e.key)
                    if char in '.abcdefghijklmnopqrstuvwxyz;:/?\|[{]}1234567890-=!@#$%^&*()_+~~':
                        prompt.keypress(char)
            elif e.type == KEYUP:
                if e.key == K_LEFT:
                    leftp = False
                elif e.key == K_RIGHT:
                    rightp = False
    
        if leftp:
            browser.left()
        elif rightp:
            browser.right()

        if commandchanged:
            screen = backup.copy()
            commandchanged = False

        if shutdown:
            screen.fill(black)
            if len(graphs) > 0:
                if pausecount < pausemax:
                    pausecount += 1
                else:
                    graphs = graphs[1:]
                    pausecount = 0
            else:
                shutdown = False

        if startup:
            print 'STARTING UP!!!'
            if len(graphs) < len(graphbak):
                if pausecount < pausemax:
                    pausecount += 1
                else:
                    graphs.append(graphbak[len(graphs)])
                    pausecount = 0
            else:
                startup = False
                    

        for g in graphs:
            g.update()



        if command:
            prompt.update()
            if experimentp:
                experiment.update()
            else:
                browser.update()
        else:
            prompt.timed()            

        output.blit(screen, [0, 0])        

        display.flip()

        if pause > 0:
            sleep(pause)

        
        

        
##---------------------
## RUNTIME
##---------------------            
        
if __name__ == '__main__':
    main()
