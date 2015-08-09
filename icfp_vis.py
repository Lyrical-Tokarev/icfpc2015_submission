
__author__ = 'Lacemaker'
import sys
import os
import fnmatch
import math
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

        self.currentFile = "test_data/problem_6.json"
        self.loadFileData(self.currentFile)


    def initUI(self):

        self.setGeometry(300,300,250,150)
        self.setWindowTitle('Event handler')
        self.resize(800, 600)

        grview = QGraphicsView(self)
        self.scene = QGraphicsScene()
        grview.setScene(self.scene)
        grview.resize(640, 480)

        sidebar = QWidget(self)
        sidebarLayout = QVBoxLayout()
        sidebar.move(640, 0)
        sidebar.setFixedWidth(160)

        self.srcTextEdit = QTextEdit(self)
        self.srcTextEdit.setFixedHeight(100)
        self.solTextEdit = QTextEdit(self)
        self.solTextEdit.setFixedHeight(100)

        panel = QWidget(self)
        panel.setGeometry(QRect(640, 100, 160, 40))
        panelButtons = QHBoxLayout(self)

        btnLoad = QPushButton ("Load")
        def onLoadClick():
            jsonStr = str(self.srcTextEdit.toPlainText())
            self.loadGame(jsonStr)
            return
        btnLoad.clicked.connect(onLoadClick)

        btnPrev = QPushButton ("<<")
        def onPrevClick():
            dir = os.path.dirname(self.currentFile)
            file = os.path.basename(self.currentFile)
            files = filter(lambda f: fnmatch.fnmatch(f, '*.json'), os.listdir(dir))
            jsonFile = files[files.index(file) - 1]
            self.loadFileData(os.path.join(dir, jsonFile))
        btnPrev.clicked.connect(onPrevClick)
        btnNext = QPushButton (">>")
        def onNextClick():
            dir = os.path.dirname(self.currentFile)
            file = os.path.basename(self.currentFile)
            files = filter(lambda f: fnmatch.fnmatch(f, '*.json'), os.listdir(dir))
            jsonFile = files[files.index(file) + 1]
            self.loadFileData(os.path.join(dir, jsonFile))
        btnNext.clicked.connect(onNextClick)

        panelButtons.addWidget(btnPrev)
        panelButtons.addWidget(btnLoad)
        panelButtons.addWidget(btnNext)
        panel.setLayout(panelButtons)

        btnPlay = QPushButton("Play")
        def onPlayClick():
            solStr = str(self.solTextEdit.toPlainText())
            self.play(solStr)
            return
        btnPlay.clicked.connect(onPlayClick)

        sidebarLayout.addWidget(self.srcTextEdit)
        sidebarLayout.addWidget(panel)
        sidebarLayout.addWidget(self.solTextEdit)
        sidebarLayout.addWidget(btnPlay)
        sidebar.setLayout(sidebarLayout)

        self.show()
        return

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Space:
            self.nextUnit()
        elif e.key() == QtCore.Qt.Key_S:
            self.makeMove(MoveType.RC)
        elif e.key() == QtCore.Qt.Key_W:
            self.makeMove(MoveType.RCC)
        elif e.key() == QtCore.Qt.Key_Q:
            self.makeMove(MoveType.W)
        elif e.key() == QtCore.Qt.Key_E:
            self.makeMove(MoveType.E)
        elif e.key() == QtCore.Qt.Key_A:
            self.makeMove(MoveType.SW)
        elif e.key() == QtCore.Qt.Key_D:
            self.makeMove(MoveType.SE)
        return

    def makeMove(self, moveType):
        (_a, o, r) = self.game.makeMove(self.gameField , self.currentUnit, self.currentUnitOffsets, self.currentUnitRotation, moveType)
        result = True
        if _a:
            self.currentUnitOffsets = o
            self.currentUnitRotation = r
        else:
            # lock unit
            cells = self.currentUnit.moveAndRotate(self.currentUnitOffsets, self.currentUnitRotation)
            self.gameField = self.gameField.fillCells(cells)
            [self.game.filledCells.append(c) for c in cells]

            # clear lines
            lines = self.gameField.countLines()
            if lines > 0:
                self.gameField = self.gameField.cleanLines()

            # calculate score
            points = len(self.currentUnit.members) + 100 * (1 + lines) * lines / 2
            if self.lastCleanedLines > 1:
                line_bonus =  math.floor((self.lastCleanedLines - 1) * points / 10)
            else:
                line_bonus = 0
            move_score = points + line_bonus
            self.lastCleanedLines = lines
            self.score += move_score
            print("Score: ", move_score, self.score)

            # spawn next unit
            self.nextUnit()
            cells = self.currentUnit.moveAndRotate(self.currentUnitOffsets, self.currentUnitRotation)
            result = self.gameField.checkCells(cells)

        self.redraw()
        return result

    def loadGame(self, jsonText):
        jsonData = json.loads(jsonText, encoding = "utf-8")
        game = Game(jsonData)

       # init state
        self.game = game
        self.gameField = game.startField
        self.rndGenerator = Random(game.sourceSeeds[0])

        self.unitIndex = self.rndGenerator.next() % len(self.game.units)
        self.currentUnit = self.game.units[self.unitIndex]
        self.currentUnitOffsets = self.game.unitStartOffsets[self.unitIndex]
        self.currentUnitRotation = 0
        self.lastCleanedLines = 0
        self.score = 0

        self.drawField()
        drawUnit(self.scene, self.currentUnit, self.currentUnitOffsets)
        return

    def loadFileData(self, file):
        self.currentFile = file
        with open(self.currentFile) as data_file:
            data = data_file.read()
            self.srcTextEdit.setText(data)
            self.loadGame(data)


    def nextUnit(self):
        self.unitIndex = self.rndGenerator.next() % len(self.game.units)
        self.currentUnit = self.game.units[self.unitIndex]
        self.currentUnitOffsets = self.game.unitStartOffsets[self.unitIndex]
        self.currentUnitRotation = 0
        self.drawField()
        drawUnit(self.scene, self.currentUnit, self.currentUnitOffsets)
        return

    def drawField(self):
        w = self.game.startField.width
        h = self.game.startField.height
        self.scene.clear()
        for x in xrange(0, w):
            for y in xrange(0, h):
                drawHex(self.scene, x, y, not self.gameField.field[y, x])

        return

    def redraw(self):
        self.drawField()
        drawUnit(self.scene, self.currentUnit, self.currentUnitOffsets, self.currentUnitRotation)
        return

    def play(self, solStr):
        for c in solStr:
            if (c not in ['\r', '\n', '\t']):
                move = MoveType.fromChar(c)
                res = self.makeMove(move)
                if not res:
                    break
            QtGui.QApplication.processEvents()
        return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VizFrame()
    w.show();
    sys.exit(app.exec_())


