
__author__ = 'Lacemaker'
import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import *
from icfp_loader_script import *
import json

def drawHex(scene, col, row, filled = False):
    size = 16
    K = 0.8660254
    x = col * K * size * 2 + K * size * (row % 2)
    y = row * size * 1.5
    p1 = QPointF(x, y - size)
    p2 = QPointF(x + K*size, y - 0.5*size)
    p3 = QPointF(x + K*size, y + 0.5*size)
    p4 = QPointF(x, y + size)
    p5 = QPointF(x - K*size, y + 0.5*size)
    p6 = QPointF(x - K*size, y - 0.5*size)

    poly = QPolygonF()
    poly.append(p1)
    poly.append(p2)
    poly.append(p3)
    poly.append(p4)
    poly.append(p5)
    poly.append(p6)

    if (filled):
        brush = QBrush(QColor(0, 0, 255, 127), Qt.SolidPattern)
    else:
        brush = QBrush()
    scene.addPolygon(poly, QPen(), brush)

    return

def drawGrid(scene, width, height):
    for i in xrange(0, width):
        for j in xrange(0, height):
            drawHex(scene, i, j)
    return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(800, 600)

    grview = QGraphicsView(w)
    scene = QGraphicsScene()

    grview.setScene(scene)
    grview.resize(640, 480)

    srcTextEdit = QTextEdit(w);
    srcTextEdit.setGeometry(640, 0 , 160, 100)


    btnLoad = QPushButton ("Load", w)
    btnLoad.setGeometry(640, 100, 160, 20)
    def onLoadClick():
        jsonStr = srcTextEdit.toPlainText()
        jsonData = json.loads(str(jsonStr), encoding = "utf-8")
        game = Game(jsonData)
        w = game.startField.width
        h = game.startField.height
        scene.clear()
        drawGrid(scene, w, h)
        for cell in game.filledCells:
            drawHex(scene, cell.x, cell.y, True)
        return
    btnLoad.clicked.connect(onLoadClick)

    w.show();
    sys.exit(app.exec_())

    data = json.load(data_file, encoding = "utf-8")
