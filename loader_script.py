#!/usr/bin/env python
import json
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
        print "field created"
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
        self.pivot = Cell(data["pivot"])
        self.members = [Cell(member) for member in data["members"]]
class Game(object):
    def __init__(self, data):
        print "in game construction"
        print data
        self.startField = Field(data["width"], data["height"], )
        self.filledCells = [Cell(cell_info)for cell_info in data["filled"]]
        self.sourceLength = data["sourceLength"]
        self.sourceSeeds = data["sourceSeeds"]
        self.units = [Unit(unit_info) for unit_info in data["units"]]
        self.startField = self.startField.fillCells(self.filledCells)
        print self.startField.fillCells([Cell({"x":1, "y":1})]).checkCells([Cell({"x":1, "y":1})])

with open('test_data/problem_0.json') as data_file:
    data = json.load(data_file, encoding = "utf-8")
    print data["id"]
    Game(data)
