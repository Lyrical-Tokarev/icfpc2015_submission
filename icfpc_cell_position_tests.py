from nose.tools import with_setup, raises, assert_true, assert_equals

from icfp_loader_script import *
from icfp_triplet import *

def check_cell_equality_test():
    a = Cell(1, 2)
    b = Cell(1, 2)
    assert_true(a == b)

def triplet_test():
    t1 = Triplet.fromColRow(1, 0)
    assert_true(t1.southWest() == Triplet.fromColRow(0, 1))
    assert_true(t1.southEast() == Triplet.fromColRow(1, 1))
    t2 = Triplet.fromColRow(1, 1)
    assert_true(t2.southWest() == Triplet.fromColRow(1, 2))
    assert_true(t2.southEast() == Triplet.fromColRow(2, 2))

def field_unit_move_test():
    basic_members = [{"x": 0, "y": 0}, {"x": 1, "y": 1}]
    pivots = [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 1}, {"x": 1, "y": -1}]
    moves = [Cell(1, 0), Cell(1, 1), Cell(2, 0), Cell(0, 1), Cell(0, 2)]
    expected_results = [
        [Cell(1, 0), Cell(2, 1)],#1
        [Cell(1, 1), Cell(3, 2)],#2
        [Cell(2, 0), Cell(3, 1)],#3
        [Cell(0, 1), Cell(2, 2)],#4
        [Cell(0, 2), Cell(1, 3)]
    ]
    for k in range(len(moves)):
        move = moves[k]
        expected_result = expected_results[k]
        print "current move: {0}".format(move)
        for pivot in pivots:
            unit = Unit(pivot, basic_members)
            actual_result = unit.moveAndRotate(move, 0)
            for i in range(len(actual_result)):
                print "actual: {0}, expected: {1}".format(actual_result[i], expected_result[i])
                assert_true(actual_result[i] == expected_result[i])

def kill_filled_lines_test():
    field = Field(4, 7).fillCells([Cell(x, 2) for x in range(4)]).fillCells([Cell(x, 5) for x in range(4)])
    assert_true(field.cleanLines() == Field(4,7))
    field = Field(4, 7).fillCells([Cell(x, 2) for x in range(4)]).fillCells([Cell(x, 5) for x in range(4)]).fillCells([
        Cell(3, 6), Cell(0, 1)])
    assert_true(field.cleanLines() == Field(4, 7).fillCells([Cell(3, 6), Cell(0, 3)]))
