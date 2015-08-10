#!/usr/bin/env python

__author__ = 'Lacemaker'

import icfp_random
from icfp_loader_script import *
from icfp_estimation import *

def getRoute(startOffset, offset, rotation):
    from icfp_loader_script import MoveType
    route = []
    if rotation >= 0:
        route.extend([MoveType.RC for i in range(rotation)])
    else:
        route.extend([MoveType.RC for i in range(-rotation)])
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
    values = map(lambda c: c.x, cells)
    return max(values) - min(values) + 1

def computeCenterOfMass(cells):
    return map(lambda c: int(round(1.0*sum(c)/len(c))), zip(*map(lambda c: (c.x, c.y), cells)))

class Solver(object):

    def __init__(self, game):
        self.game = game
    def solve(self, seed):
        self.gameField = self.game.startField
        self.rndGenerator = icfp_random.Random(seed)
        from icfp_loader_script import Cell
        self.unitIndex = self.rndGenerator.next() % len(self.game.units)
        self.currentUnit = self.game.units[self.unitIndex]
        self.currentUnitOffsets = self.game.unitStartOffsets[self.unitIndex]
        self.currentUnitRotation = 0
        r = []
        for units in range(self.game.sourceLength):
            bestCost = 10000000
            bestOffset = self.currentUnitOffsets
            bestRotation = 0
            estimator = BadnessEstimator(self.game.startField.width, self.game.startField.height)
            for rotation in [0, -1, 1]:
                cells = self.currentUnit.moveAndRotate(bestOffset, rotation)
                if not self.gameField.checkCells(cells):
                    continue
                for i in range(self.game.startField.width - cellsWidth(self.currentUnit.moveAndRotate(bestOffset, rotation)) + 1):
                    offset = Cell(i, 0)
                    canMove = True
                    prevCells = []
                    while True:
                        offset = offset + Cell(0, 1)
                        cells = self.currentUnit.moveAndRotate(offset, 0)
                        if not self.gameField.checkCells(cells): break
                        prevCells = cells
                    f = self.gameField.fillCells(prevCells)
                    centerOfMass = computeCenterOfMass(prevCells)
                    cost = -centerOfMass[1] if len(prevCells) > 0 else -offset.y  #todo: put heuristics here estimator.scoreHeight(f) + estimator.scoreFilledRows(f)
                    if cost < bestCost:
                        bestCost = cost
                        bestOffset = offset
                        bestRotation = rotation
            cells = self.currentUnit.moveAndRotate(bestOffset + Cell(0, -1), bestRotation)
            #for cell in cells: print cell
            self.gameField = self.gameField.fillCells(cells)
            r.extend(getRoute(self.currentUnitOffsets, bestOffset, bestRotation))
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
        return "".join(r)

if __name__ == "__main__":
    from icfp_loader_script import *
    print Cell(1,2)
    print "in solver"
