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
        [Cell(1, 1), Cell(2, 2)],#2
        [Cell(2, 0), Cell(3, 1)],#3
        [Cell(0, 1), Cell(1, 2)],#4
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

"""
@raises(ValueError)
def get_file_format_test():
    assert get_file_format("gene1.fas"), "fasta"
    assert get_file_format("gene2.gbk"), "genebank"
    get_file_format("file.ab1")

@raises(IOError)
def test_file_existance():
    assert_true(load_from_file("../../hometask-files/2-bio_toolkits/gene1.fasta"))
    load_from_file("gene1.fas")

def get_info_test():
    assert_equals(get_info("AAAAAA"), (0.0, "AAAAAA", "KK"))
    assert_equals(get_info("GCC"), (100.0, "GCC", "A"))
    assert_equals(get_info("GCT"), (200.0/3, "GCU", "A"))

@raises(ValueError)
def load_from_file_test():
    filename = "../../hometask-files/2-bio_toolkits/gene1.fasta"
    sequences = load_from_file(filename)
    result_sequences = print_information(0, filename, sequences)
    assert_equals(len(result_sequences), 1)
    align(result_sequences)

def load_from_file_2_test():
    '''test should not raise any errors'''
    filenames = ["../../hometask-files/2-bio_toolkits/gene1.fasta", "../../hometask-files/2-bio_toolkits/gene2.fasta"]
    results = []
    for filename in filenames:
        results += print_information(0, filename, load_from_file(filename))
    assert align(results)
"""
