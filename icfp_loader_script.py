#!/usr/bin/env python
import json, os, sys, logging
from json import *
from icfp_random import Random
from itertools import islice
from icfp_triplet import Triplet
import icfp_solver

import numpy as np


class MoveType(object):
    W = '0'
    E = '2'
    SW = '4'
    SE = '5'
    RC = '1'
    RCC = 'x'
    IGN = '*'
    @staticmethod
    def fromChar(c):
        dict = {
            MoveType.W : ['p', '\'', '!', '.', '0', '3', 'P'],
            MoveType.E : ['b', 'c', 'e', 'f', 'y', '2', 'B', 'C', 'E', 'F', 'Y'],
            MoveType.SW: ['a', 'g', 'h', 'i', 'j', '4', 'A', 'G', 'H', 'I', 'J'],
            MoveType.SE: ['l', 'm', 'n', 'o', ' ', '5', 'L', 'M', 'N', 'O'],
            MoveType.RC: ['d', 'q', 'r', 'v', 'z', '1', 'D', 'Q', 'R', 'V', 'Z'],
            MoveType.RCC:['k', 's', 't', 'u', 'w', 'x', 'K', 'S', 'T', 'U', 'W', 'X']
        }
        for (k, v) in dict.items():
            if c in v:
                return k
        print c
        raise ValueError(c)
        return
    @staticmethod
    def toChars(move):
        return {
            MoveType.W :"p\'!.03",
            MoveType.E : "bcefy2",
            MoveType.SW: "aghij4",
            MoveType.SE: "lmno 5",
            MoveType.RC: "dqrvz1",
            MoveType.RCC: "kstuwx",
            MoveType.IGN: ""
        }[move]


class Cell(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __iadd__(self, b):
        if isinstance(b, Cell):
            self.x += b.x
            self.y += b.y
        else:
            self.x += b[0]
            self.y += b[1]
        return self
    def __add__(self, b):
        """
        example:
        ```
        a = Cell(3, 4)
        print (a + Cell(5, -2)) # prints "8 2"
        print a # prints "3 4"
        a+= a # modifies a in place
        print a + (1,2) # doesn't modify a
        ```
        """
        new_cell = Cell(self.x, self.y)
        if isinstance(b, Cell):
            new_cell.x += b.x
            new_cell.y += b.y
        else:
            new_cell.x += b[0]
            new_cell.y += b[1]
            #this is buggy, i know
        return new_cell
    def __str__(self):
        return "Cell({0}, {1})".format(self.x, self.y)
    def toTriplet(self):
        return Triplet.fromColRow(self.x, self.y)
    def __eq__(self, cell):
        return cell.x == self.x and cell.y == self.y
    @staticmethod
    def fromTriplet(triplet):
        (x, y) = triplet.toColRow()
        return Cell(x, y)


"""
1st coord in field is based on height value.
field[i, j] id True when empty, False overwise
"""
class Field(object):
    def __init__(self, width, height, **args):
        self.height = height
        self.width = width
        self.field = np.ones((height, width), dtype=bool)
        logging.debug("field created")
    def fillCells(self, cells):
        """
        returns new Field object with `cells` marked as filled, leaving self unchanged
        """
        new_field = Field(self.width, self.height)
        np.copyto(new_field.field, self.field)
        for cell in cells:
            new_field.field[cell.y, cell.x] = False
        return new_field
    def cleanLines(self):
        if np.all(np.any(self.field, 1)):
            return self
        rows = np.where(np.any(self.field, 1) == False)[0]
        shifts = [np.count_nonzero(rows > i) for i in range(self.height)]
        new_field = Field(self.width, self.height)
        for i in range(self.height - 1, -1, -1):
            if i + shifts[i] < self.height:
                new_field.field[i + shifts[i], :] = self.field[i, :]
        return new_field
    def countLines(self):
        return self.height - np.count_nonzero(np.any(self.field, 1))
    def checkPosition(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height
    def checkCells(self, cells):
        """
        returns True if all cells are empty (not filled), false otherwise
        """
        return np.all([self.checkPosition(cell.x, cell.y) and self.field[cell.y, cell.x] for cell in cells])
    def computePivotStartOffset(self, unit):
        """
        returns tuple - offset to move unit's pivot at spawn
        """
        offset_y = 0 - min(map(lambda c: c.y, unit.members))
        left_x = min(map(lambda c: c.x, unit.members))
        right_x = max(map(lambda c: c.x, unit.members))
        offset_x = (self.width - right_x + left_x - 1) // 2 - left_x
        return Cell(offset_x, offset_y)
    def __eq__(self, other):
        return isinstance(other, Field) and np.array_equal(self.field, other.field)


class Unit(object):
    def __init__(self, pivot, members):
        self.pivot = Cell(**pivot)
        self.members = [Cell(**member) for member in members]
    def moveAndRotate(self, offset, rotation):
        """
        returns [Cells] which are currently filled by Unit object
        """
        _rotate = lambda triplet, n: reduce(lambda last, n: last.clockwise(), range(n), triplet)
        pin = self.pivot.toTriplet()
        return map(
            lambda cell: Cell(*(_rotate(cell.toTriplet().untie(pin), rotation % 6).tie(offset.toTriplet()).tie(pin).toColRow())),
            self.members
        )


class SolutionEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Solution):
            return o.__dict__
        return JSONEncoder().default(o)

class Game(object):
    def __init__(self, data):
        logging.debug("in game construction")
        logging.debug(data)
        self.startField = Field(**data)
        self.filledCells = [Cell(**cell_info) for cell_info in data["filled"]]
        self.sourceLength = data["sourceLength"]
        self.sourceSeeds = data["sourceSeeds"]
        self.id = data["id"]
        self.startField = self.startField.fillCells(self.filledCells)
        self.units = [Unit(**unit_info) for unit_info in data["units"]]
        self.unitStartOffsets = [self.startField.computePivotStartOffset(unit) for unit in self.units]
    def convert(self, str, seed):
        rnd = Random(seed + 1)
        return "".join([MoveType.toChars[s][rnd.next() % len(MoveType.toChars[s])] for s in str])
        ##following line is an example of cells emptyness check:
        #print self.startField.fillCells([Cell({"x":1, "y":1})]).checkCells([Cell({"x":1, "y":1})])
    def process(self, phrasesOfPower):
        return [Solution(self.id, seed, self, phrasesOfPower) for seed in self.sourceSeeds]
    def makeMove(self, currentField, unit, currentOffset, currentRotation, moveType):
        """
        performs move for current unit and checks it position in currentField
        """
        newOffset = currentOffset
        newRotation = currentRotation
        if moveType == MoveType.W:
            newOffset = Cell.fromTriplet(currentOffset.toTriplet().west())
        if moveType == MoveType.E:
            newOffset = Cell.fromTriplet(currentOffset.toTriplet().east())
        if moveType == MoveType.SE:
            newOffset = Cell.fromTriplet(currentOffset.toTriplet().southEast())
        if moveType == MoveType.SW:
            newOffset = Cell.fromTriplet(currentOffset.toTriplet().southWest())
        if moveType == MoveType.RC:
            newRotation = (currentRotation + 1) % 6
        if moveType == MoveType.RCC:
            newRotation = (currentRotation - 1) % 6
        #next - check if unit can be placed at new position
        cells = unit.moveAndRotate(newOffset, newRotation)
        moveResult = currentField.checkCells(cells)
        return (moveResult, newOffset, newRotation)
    def strToCommands(self, str):
        return filter(lambda x: x!= MoveType.IGN, [MoveType.fromChar(ch) for ch in str])
    def substituteMove(self, currentField, currentUnit, currentOffset, currentRotation, cmd):
        for cmd2 in [cmd, MoveType.SE, MoveType.SW, MoveType.RC, MoveType.RCC, MoveType.E, MoveType.W]:
            (moveResult, newOffset, newRotation) = self.makeMove(currentField, currentUnit, currentOffset, currentRotation, cmd)
            if moveResult:
                return (moveResult, newOffset, newRotation, cmd2)
        return (False, currentOffset, currentRotation, cmd)
    def makeCommands(self, seed, default_commands, einificate = True):
        """
        main method - should return sequence of commands
        """
        self.rndGenerator = Random(seed)
        unitIndex = self.rndGenerator.next() % len(self.units)
        currentUnit = self.units[unitIndex]
        currentOffset = self.unitStartOffsets[unitIndex]
        currentRotation = 0
        currentField = self.startField
        cmds = self.strToCommands(default_commands[0])
        valid_commands = []
        previousWasBad = False
        last_cmd = MoveType.IGN
        unitsCounter = 0
        while(True):
            if previousWasBad:
                break
            cmd_index = -1
            for cmd in cmds:
                cmd_index = (cmd_index + 1) % len(cmds)
                (moveResult, newOffset, newRotation, cmd2) = self.substituteMove(currentField, currentUnit, currentOffset, currentRotation, cmd)
                if moveResult:
                    if einificate and cmd2 == MoveType.SW and last_cmd != MoveType.W:
                        #print "eification"
                        offset = currentOffset
                        rotation = currentRotation
                        eiResult = True
                        for ei in self.strToCommands("Ei!"):
                            (mr, offset, rotation) = self.makeMove(currentField, currentUnit, offset, rotation, ei)
                            if not mr:
                                eiResult = False
                                break
                        if eiResult:
                            valid_commands.append("Ei!")
                            #print "eificated"
                        else:
                            if cmd2 == cmd:
                                valid_commands.append(default_commands[0][cmd_index])
                            else:
                                valid_commands.append(cmd2)
                    else:
                        if cmd2 == cmd:
                            valid_commands.append(default_commands[0][cmd_index])
                        else:
                            valid_commands.append(cmd2)
                    previousWasBad = False
                    currentOffset = newOffset
                    currentRotation = newRotation
                    last_cmd = cmd2
                else:
                    #todo: spawn new Unit here
                    if previousWasBad:
                        break
                    valid_commands.append(default_commands[0][cmd_index])
                    previousWasBad = True
                    if unitsCounter >= self.sourceLength:
                        break
                    currentField = currentField.fillCells(currentUnit.moveAndRotate(currentOffset, currentRotation)).cleanLines()
                    unitIndex = self.rndGenerator.next() % len(self.units)
                    currentUnit = self.units[unitIndex]
                    currentOffset = self.unitStartOffsets[unitIndex]
                    currentRotation = 0
                    unitsCounter += 1
        #return "".join([
        #    default_commands[0] for i in range(len(valid_commands) // len(default_commands[0]))]) + default_commands[0][:(len(valid_commands) % len(default_commands[0]))]
        return "".join(valid_commands)
        #currentUnit.moveAndRotate(currentOffset, currentRotation)
        #print (currentOffset.__str__(), currentRotation)
        #(moveResult, newOffset, newRotation) = self.makeMove(currentField, currentUnit, currentOffset, currentRotation, MoveType.W)
        #print (moveResult, newOffset.__str__(), newRotation)
        #return default_commands[0]


class Solution(object):
    def __init__(self, gameId, seed, game, phrasesOfPower, commands = ["iiiiiiiimmiiiiiimimmiiiimimimmimimimimmimimimeemimeeeemimim" +
    "imimiiiiiimmeemimimimimiimimimmeemimimimmeeeemimimimmiiiiii" +
    "pmiimimimeeemmimimmemimimimiiiiiimeeemimimimimeeemimimimmii" +
    "iimemimimmiiiipimeeemimimmiiiippmeeeeemimimimiiiimmimimeemi" +
    "mimeeeemimimiiiipmeeemmimmiimimmmimimeemimimimmeeemimiiiiip" +
    "miiiimmeeemimimiiiipmmiipmmimmiippimemimeeeemimmiipppmeeeee" +
    "mimimmiimipmeeeemimimiimmeeeeemimmeemimmeeeemimiiippmiippmi" +
    "iimmiimimmmmmeeeemimmiippimmimimeemimimimmeemimimimmeemimim" +
    "imiimimimeeemmimimmmiiiiipimeemimimimmiiiimimmiiiiiiiimiimi" +
    "mimimeeemmimimimmiiiiiimimmemimimimimmimimimeemimiiiiiiiimi" +
    "iiimimimiimimimmimmimimimimmeeeemimimimimmmimimimimeemimimi" +
    "mimmmemimimmiiiiiiimiimimimmiiiiiimeeeeemimimimimmimimimmmm" +
    "emimimmeeeemimimimmiimimimmiiiiiipmeeeeemimimimimmiiiiimmem" +
    "imimimimmmmimimmeeeemimimimimeeemimimimmiimimimeeemmimimmii" +
    "iiiiimimiiiiiimimmiiiiiiiimmimimimimiiiimimimeemimimimimmee" +
    "emimimimimiiiiiiimiiiimimmemimimimmeemimimimeeemmimimmiiiii" +
    "immiiiipmmiiimmmimimeemimimeeemmimmiiiippmiiiimiiippimiimim" +
    "eemimimeeeemimimiiiipmeemimimiimiimimmimeeemimimmippipmmiim" +
    "emimmipimeeeemimmeemimiippimeeeeemimimmmimmmeeeemimimiiipim" +
    "miipmemimmeeeemimimiipipimmipppimeeemimmpppmmpmeeeeemimmemmBigbootePlanet 10Ei!cthulhu",
    "BigbootePlanet 10Ei!cthulhu", "Planet 10Ei!cthulhu", "Ei!", "Ia! Ia! R'lyeh"], tag = "t3"):
        self.problemId = gameId
        self.seed = seed
        self.tag = tag #+ str(seed)
        self.solution = icfp_solver.Solver(game).solve(seed)#.replace("".join(game.strToCommands("Ei!")), "Ei!")
        #self.solution = game.convert(self.solution, seed)
        #return
        if gameId == 6:
            best_commands = game.makeCommands(seed, [self.solution])
            for i in range(len(commands)):
                self.solution = commands[i]
                self.solution = game.makeCommands(seed, [self.solution], False)
                if len(self.solution) > len(best_commands):
                    best_commands = self.solution
            self.solution = best_commands
        else:
            self.solution = game.makeCommands(seed, [self.solution])
        for phrase in phrasesOfPower:
            phrase_encoded = ''.join(game.strToCommands(phrase))
            self.solution = self.solution.replace(phrase_encoded, phrase)
        #.replace("".join(game.strToCommands("Ei!")), "Ei!")

def to_json(solutionsList):
    return SolutionEncoder().encode(solutionsList)

def main(inputFileNames, timeLimit, memoryLimit, phrases):
    result = 0
    if not inputFileNames:
        inputFileNames = ["test_data/problem_{0}.json".format(i) for i in range(25)  if i!=6]
        #print >> sys.stderr, "input file was not provided"
        #result = 1
    if not timeLimit:
        timeLimit = 0
    if not memoryLimit:
        memoryLimit = 0
    if result:
        return result
    #try:
    solutions = []
    for inputFileName in inputFileNames:
        with open(inputFileName) as data_file:
            data = json.load(data_file, encoding = "utf-8")
        game = Game(data)
        solutions.extend(game.process(phrases))
    print to_json(solutions)
    #except Exception as e:
    #    print "Got error: ", e
    #    result = 1
    return result

if __name__ == "__main__":
    logging.basicConfig(filename = "" + os.path.splitext(os.path.basename(__file__))[0] + ".log", level = logging.ERROR)
    logging.debug("============\nCalled simple script")
    from optparse import OptionParser
    parser = OptionParser()
    #input file options:
    parser.add_option("-f", "--file", dest = "inputFileName", help = "input FILE with games - in json", metavar = "FILE", action="append")
    parser.add_option("-t", "--time", dest = "timeLimit", help = "time limit", metavar = "NUMBER")
    parser.add_option("-m", "--memory", dest = "memoryLimit", help = "memory limit", metavar = "NUMBER")
    parser.add_option("-p", "--phrase_of_power", dest="phrases", help = "phrase of power string", metavar = "STRING", action="append")
    (options, args) = parser.parse_args()
    if options.phrases:
        phrasesOfPower = sorted(options.phrases, key=len, reverse = True)
        result = main(options.inputFileName, options.timeLimit, options.memoryLimit, phrasesOfPower)
    else:
        result = main(options.inputFileName, options.timeLimit, options.memoryLimit, [])
    if result:
        parser.print_help()
