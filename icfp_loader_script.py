#!/usr/bin/env python
import json, os, sys, logging
from json import *
from icfp_random import Random
from itertools import islice
from icfp_triplet import Triplet

import numpy as np

class MoveType(object):
    W = 0
    E = 2
    SW = 4
    SE = 5
    RC = 1
    RCC = 'x'


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
    def checkPosition(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height
    def checkCells(self, cells):
        """
        returns True if all cells are empty (not filled), false otherwise
        """
        return np.all([self.field[cell.y, cell.x] and self.checkPosition(cell.x, cell.y) for cell in cells])

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
            lambda cell: Cell(*(_rotate(cell.toTriplet().untie(pin), rotation % 6).tie(pin).toColRow())) + offset,
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
        ##following line is an example of cells emptyness check:
        #print self.startField.fillCells([Cell({"x":1, "y":1})]).checkCells([Cell({"x":1, "y":1})])

    def process(self):
        return [Solution(self.id, seed, self) for seed in self.sourceSeeds]

    def makeMove(self, currentField, unit, currentOffset, currentRotation, moveType):
        """
        performs move for current unit and checks it position in currentField
        """
        newOffset = currentOffset
        newRotation = currentRotation
        if moveType == MoveType.W:
            newOffset = currentOffset + Triplet().west().toColRow()
        if moveType == MoveType.E:
            newOffset = currentOffset + Triplet().east().toColRow()
        if moveType == MoveType.SE:
            newOffset = currentOffset + Triplet().southEast().toColRow()
        if moveType == MoveType.SW:
            newOffset = currentOffset + Triplet().southWest().toColRow()
        if moveType == MoveType.RC:
            newRotation = (currentRotation + 1) % 6
        if moveType == MoveType.RCC:
            newRotation = (currentRotation - 1) % 6
        #next - check if unit can be placed at new position
        cells = unit.moveAndRotate(newOffset, newRotation)
        moveResult = currentField.checkCells(cells)
        return (moveResult, newOffset, newRotation)

    def makeCommands(self, seed, default_commands):
        """
        main method - should return sequence of commands
        """
        self.rndGenerator = Random(seed)
        unitIndex = self.rndGenerator.next() % len(self.units)
        currentUnit = self.units[unitIndex]
        currentOffset = self.unitStartOffsets[unitIndex]
        currentRotation = 0
        currentField = self.startField
        currentUnit.moveAndRotate(currentOffset, currentRotation)
        print (currentOffset.__str__(), currentRotation)
        (moveResult, newOffset, newRotation) = self.makeMove(currentField, currentUnit, currentOffset, currentRotation, MoveType.W)
        print (moveResult, newOffset.__str__(), newRotation)
        return default_commands


class Solution(object):
    def __init__(self, gameId, seed, game, commands = "cthulhu", tag = ""):
        self.problemId = gameId
        self.seed = seed
        self.tag = tag
        self.solution = game.makeCommands(seed, commands)

def to_json(solutionsList):
    return SolutionEncoder().encode(solutionsList)

def main(inputFileNames, timeLimit, memoryLimit, phrase):
    result = 0
    if not inputFileNames:
        print >> sys.stderr, "input file was not provided"
        result = 1
    if not timeLimit:
        timeLimit = 0
    if not memoryLimit:
        memoryLimit = 0
    if result:
        return result
    try:
        solutions = []
        for inputFileName in inputFileNames:
            with open(inputFileName) as data_file:
                data = json.load(data_file, encoding = "utf-8")
            game = Game(data)
            solutions.extend(game.process())
        print to_json(solutions)
    except Exception as e:
        print "Got error: ", e
        result = 1
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
    parser.add_option("-p", "--phrase_of_power", dest="phrase", help = "phrase of power string", metavar = "STRING")
    (options, args) = parser.parse_args()
    result = main(options.inputFileName, options.timeLimit, options.memoryLimit, options.phrase)
    if result:
        parser.print_help()
