#!/usr/bin/env python
import json, os, sys, logging
from json import *

import numpy as np

class Cell(object):
    def __init__(self, data):
        self.x = data["x"]
        self.y = data["y"]
"""
1st coord in field is based on height value.
field[i, j] id True when empty, False overwise
"""
class Field(object):
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.field = np.ones((height, width), dtype=bool)
        logging.debug("field created")
    """
    method should return new Field object with cells selected
    """
    def fillCells(self, cells):
        new_field = Field(self.width, self.height)
        np.copyto(new_field.field, self.field)
        for cell in cells:
            new_field.field[cell.y, cell.x] = False
        return new_field
    """
    method returns true if all cells are empty, false otherwise
    """
    def checkCells(self, cells):
        return np.all([self.field[cell.y, cell.x] for cell in cells])
    def __eq__(self, other):
        return isinstance(other, Field) and isinstance(self, Field) and np.array_equal(self.field, other.field)



class Unit(object):
    def __init__(self, data):
        self.pivot = Cell(data["pivot"]) #TODO: process situation with no pivot
        self.members = [Cell(member) for member in data["members"]]
class SolutionEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Solution):
            return o.__dict__
        return JSONEncoder().default(o)
class Game(object):
    def __init__(self, data):
        logging.debug("in game construction")
        logging.debug(data)
        self.startField = Field(data["width"], data["height"], )
        self.filledCells = [Cell(cell_info)for cell_info in data["filled"]]
        self.sourceLength = data["sourceLength"]
        self.sourceSeeds = data["sourceSeeds"]
        self.id = data["id"]
        self.units = [Unit(unit_info) for unit_info in data["units"]]
        self.startField = self.startField.fillCells(self.filledCells)
        ##following line is an example of cells emptyness check:
        #print self.startField.fillCells([Cell({"x":1, "y":1})]).checkCells([Cell({"x":1, "y":1})])
    def process(self):
        return SolutionEncoder().encode([Solution(self.id, seed) for seed in self.sourceSeeds])

class Solution(object):
    def __init__(self, gameId, seed, commands = "cthulhu", tag = ""):
        self.problemId = gameId
        self.seed = seed
        self.tag = tag
        self.solution = commands

def main(inputFileName, timeLimit, memoryLimit, phrase):
    result = 0
    if not inputFileName:
        print >> sys.stderr, "input file was not provided"
        result = 1
    if not timeLimit:
        timeLimit = 0
    if not memoryLimit:
        memoryLimit = 0
    if result:
        return result
    try:
        with open(inputFileName) as data_file:
            data = json.load(data_file, encoding = "utf-8")
        game = Game(data)
        print game.process()
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
    parser.add_option("-f", "--file", dest = "inputFileName", help = "input FILE with games - in json", metavar = "FILE")
    parser.add_option("-t", "--time", dest = "timeLimit", help = "time limit", metavar = "NUMBER")
    parser.add_option("-m", "--memory", dest = "memoryLimit", help = "memory limit", metavar = "NUMBER")
    parser.add_option("-p", "--phrase_of_power", dest="phrase", help = "phrase of power string", metavar = "STRING")
    (options, args) = parser.parse_args()
    result = main(options.inputFileName, options.timeLimit, options.memoryLimit, options.phrase)
    if result:
        parser.print_help()
