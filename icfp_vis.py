
__author__ = 'Lacemaker'
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import *
from icfp_loader_script import *
import json


HEX_SIZE = 18
K = 0.8660254
COLOR_UNIT = QColor(255, 220, 0, 255)
COLOR_PIVOT = QColor(255, 100, 0, 255)
COLOR_FILLED = QColor(127, 127, 255, 255)
COLOR_UNFILLED = QColor(240, 240, 240, 255)


def toCoords(col, row):
    x = col * K * HEX_SIZE * 2 + K * HEX_SIZE * (row % 2)
    y = row * HEX_SIZE * 1.5
    return (x, y)

def drawHex(scene, col, row, filled = False, color = COLOR_FILLED):
    (x, y) = toCoords(col, row)
    hexSize = HEX_SIZE - 2
    p1 = QPointF(x, y - hexSize)
    p2 = QPointF(x + K * hexSize, y - 0.5 * hexSize)
    p3 = QPointF(x + K * hexSize, y + 0.5 * hexSize)
    p4 = QPointF(x, y + hexSize)
    p5 = QPointF(x - K * hexSize, y + 0.5 * hexSize)
    p6 = QPointF(x - K * hexSize, y - 0.5 * hexSize)

    poly = QPolygonF()
    poly.append(p1)
    poly.append(p2)
    poly.append(p3)
    poly.append(p4)
    poly.append(p5)
    poly.append(p6)

    if (not filled):
        color = COLOR_UNFILLED

    brush = QBrush(color, Qt.SolidPattern)
    scene.addPolygon(poly, QPen(color), brush)

    return

def drawGrid(scene, width, height):
    for i in xrange(0, width):
        for j in xrange(0, height):
            drawHex(scene, i, j)
    return

def drawPivot(scene, col, row, color = COLOR_PIVOT):
    (x, y) = toCoords(col, row)
    pivotSize = 6
    scene.addEllipse(QRectF(x - pivotSize / 2, y - pivotSize / 2 , pivotSize, pivotSize), QPen(), QBrush(color, Qt.SolidPattern))
    return

def drawUnit(scene, unit, offsets = Cell(0, 0), rotation = 0):
    for m in unit.moveAndRotate(offsets, rotation):
        drawHex(scene, m.x, m.y, True, COLOR_UNIT)
    drawPivot(scene, unit.pivot.x + offsets.x, unit.pivot.y + offsets.y)
    return

class VizFrame(QtGui.QWidget):
    def __init__(self):
        super(VizFrame, self).__init__()
        self.initUI()

        with open("test_data/problem_10.json") as data_file:
            data = data_file.read()
            self.srcTextEdit.setText(data)


    def initUI(self):

        self.setGeometry(300,300,250,150)
        self.setWindowTitle('Event handler')
        self.resize(800, 600)

        grview = QGraphicsView(self)
        self.scene = QGraphicsScene()
        grview.setScene(self.scene)
        grview.resize(640, 480)

        self.srcTextEdit = QTextEdit(self);
        self.srcTextEdit.setGeometry(640, 0 , 160, 100)


        btnLoad = QPushButton ("Load", self)
        btnLoad.setGeometry(640, 100, 160, 20)
        def onLoadClick():
            jsonStr = self.srcTextEdit.toPlainText()
            jsonData = json.loads(str(jsonStr), encoding = "utf-8")
            game = Game(jsonData)
            self.loadGame(game)
            return
        btnLoad.clicked.connect(onLoadClick)

        self.show()
        return

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            self.nextUnit()
        elif e.key() == QtCore.Qt.Key_S:
            (_a, self.currentUnitOffsets, self.currentUnitRotation) = self.game.makeMove(self.game.startField, self.currentUnit, self.currentUnitOffsets, self.currentUnitRotation, MoveType.RC)
            self.redraw()
        elif e.key() == QtCore.Qt.Key_W:
            (_a, self.currentUnitOffsets, self.currentUnitRotation) = self.game.makeMove(self.game.startField, self.currentUnit, self.currentUnitOffsets, self.currentUnitRotation, MoveType.RCC)
            self.redraw()
        elif e.key() == QtCore.Qt.Key_Q:
            (_a, self.currentUnitOffsets, self.currentUnitRotation) = self.game.makeMove(self.game.startField, self.currentUnit, self.currentUnitOffsets, self.currentUnitRotation, MoveType.W)
            self.redraw()
        elif e.key() == QtCore.Qt.Key_E:
            (_a, self.currentUnitOffsets, self.currentUnitRotation) = self.game.makeMove(self.game.startField, self.currentUnit, self.currentUnitOffsets, self.currentUnitRotation, MoveType.E)
            self.redraw()
        elif e.key() == QtCore.Qt.Key_A:
            (_a, self.currentUnitOffsets, self.currentUnitRotation) = self.game.makeMove(self.game.startField, self.currentUnit, self.currentUnitOffsets, self.currentUnitRotation, MoveType.SW)
            self.redraw()
        elif e.key() == QtCore.Qt.Key_D:
            (_a, self.currentUnitOffsets, self.currentUnitRotation) = self.game.makeMove(self.game.startField, self.currentUnit, self.currentUnitOffsets, self.currentUnitRotation, MoveType.SE)
            self.redraw()
        return



    def loadGame(self, game):
        self.game = game
        self.rndGenerator = Random(game.sourceSeeds[0])

        self.drawField()
        self.unitIndex = self.rndGenerator.next() % len(self.game.units)
        self.currentUnit = self.game.units[self.unitIndex]
        self.currentUnitOffsets = self.game.unitStartOffsets[self.unitIndex]
        self.currentUnitRotation = 0
        drawUnit(self.scene, self.currentUnit, self.currentUnitOffsets)
        return

    def nextUnit(self):
        self.unitIndex = self.rndGenerator.next() % len(self.game.units)
        self.currentUnit = self.game.units[self.unitIndex]
        self.currentUnitOffsets = self.game.unitStartOffsets[self.unitIndex]
        self.currentUnitRotation = 0
        print ("unitIndex", (self.unitIndex, self.game.sourceLength))
        self.drawField()
        drawUnit(self.scene, self.currentUnit, self.currentUnitOffsets)
        return

    def drawField(self):
        w = self.game.startField.width
        h = self.game.startField.height
        self.scene.clear()
        drawGrid(self.scene, w, h)
        for cell in self.game.filledCells:
            drawHex(self.scene, cell.x, cell.y, True)

    def redraw(self):
        self.drawField()
        drawUnit(self.scene, self.currentUnit, self.currentUnitOffsets, self.currentUnitRotation)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VizFrame()
    w.show();
    sys.exit(app.exec_())


