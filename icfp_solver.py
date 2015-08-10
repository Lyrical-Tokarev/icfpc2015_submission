#! /usr/bin/env python
__author__ = 'Lacemaker'

from icfp_random import *
from icfp_loader_script import *
from icfp_estimation import *

def getRoute(startOffset, offset):
    route = []
    if (offset.x < startOffset.x):
        for i in range(offset.x, startOffset.x):
            route.append(MoveType.W)
    else:
        for i in range(startOffset.x, offset.x):
            route.append(MoveType.E)

    for i in range(0, offset.y):
        if i % 2 == 0:
            route.append(MoveType.SE)
        else:
            route.append(MoveType.SW)
    return route

def cellsWidth(cells):
    w = 0
    for c in cells:
        if (c.x > w): w = c.x
    return w + 1

class Solver():

    def __init__(self, game):
        self.game = game
        self.gameField = game.startField
        self.rndGenerator = Random(game.sourceSeeds[0])
        return

    def solve(self, seed):
        self.unitIndex = self.rndGenerator.next() % len(self.game.units)
        self.currentUnit = self.game.units[self.unitIndex]
        self.currentUnitOffsets = self.game.unitStartOffsets[self.unitIndex]
        self.currentUnitRotation = 0

        r = []

        for units in range(self.game.sourceLength):

            bestCost = 10000000
            bestOffset = self.currentUnitOffsets
            estimator = BadnessEstimator(self.game.startField.width, self.game.startField.height)
            for i in range(self.game.startField.width - cellsWidth(self.currentUnit.members) + 1):
                offset = Cell(i, 0)
                canMove = True
                prevCells = []
                while True:
                    offset = offset + Cell(0, 1)
                    cells = self.currentUnit.moveAndRotate(offset, 0)
                    if not self.gameField.checkCells(cells): break
                    prevCells = cells

                f = self.gameField.fillCells(prevCells)
                cost = -offset.y  # todo: put heuristics here estimator.scoreHeight(f) + estimator.scoreFilledRows(f)
                if cost < bestCost:
                    bestCost = cost
                    bestOffset = offset
            cells = self.currentUnit.moveAndRotate(bestOffset + Cell(0, -1), 0)
            #for cell in cells: print cell
            self.gameField = self.gameField.fillCells(cells)
            r.extend(getRoute(self.currentUnitOffsets, bestOffset))

            lines = self.gameField.countLines()
            if lines > 0:
                self.gameField = self.gameField.cleanLines()

            self.unitIndex = self.rndGenerator.next() % len(self.game.units)
            self.currentUnit = self.game.units[self.unitIndex]
            self.currentUnitOffsets = self.game.unitStartOffsets[self.unitIndex]
            self.currentUnitRotation = 0

            # check if we can spawn
            cells = self.currentUnit.moveAndRotate(self.currentUnitOffsets, self.currentUnitRotation)
            if not self.gameField.checkCells(cells):
                break

        return ''.join(r)
