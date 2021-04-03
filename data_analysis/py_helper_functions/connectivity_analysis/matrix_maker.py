import math

from core.models import LessonSet
from data_analysis.models import DataLog
from data_analysis.py_helper_functions.datalog_helper import locate_confirms


# Uses an adapted version of Katz centrality to create link prediction matrix
# Attenuation constant is decay factor between links
def lesson_to_matrix(set_id, lesson_index, attenuation_constant):
    lesson_id = LessonSet.objects.get(id=set_id).lessons.all()[lesson_index].id
    query = DataLog.objects.filter(lesson_key_id=lesson_id).order_by('user_key', 'time_stamp')
    if not query:
        return
    matrix, answer_to_index = _create_matrix(query)
    prev_student = query[0].user_key
    chain = []
    for log in query:
        if prev_student != log.user_key:
            # New student!
            prev_student = log.user_key
            _disassemble_chain(matrix, chain, attenuation_constant)
            chain = []
        chain.append(answer_to_index.get(log.code))
    # Post iteration, gotta do this for the last student
    _disassemble_chain(matrix, chain, attenuation_constant)
    _display_matrix(matrix, answer_to_index)
    _relations_matrix(matrix)


# returns a matrix and hashmap between unique answers and indices in the matrix,
# also cleans up each entry's code to only keep the confirm statements
def _create_matrix(query):
    answers_found = 0
    answer_to_index = {}
    for log in query:
        log.code = locate_confirms(log.code)
        answers_found += _dict_add(answer_to_index, log.code, answers_found)
    matrix = []
    for index in range(answers_found):
        matrix.append(_make_row(answers_found))
    return matrix, answer_to_index


# To add to the dict in a way that handles whitespace inconsistency. Returns what to increment answers_found by
def _dict_add(dictionary, key, answers_found):
    if key in dictionary:
        # Already in here!
        return 0

    stripped_key = key.replace(" ", "")
    if stripped_key in dictionary:
        # Update for this version of whitespace
        dictionary[key] = dictionary.get(stripped_key)
        return 0

    # Never seen this variation before then
    dictionary[key] = dictionary[stripped_key] = answers_found
    return 1


# Makes a row filled with zeroes of given length
def _make_row(length):
    row = []
    for index in range(length):
        row.append(0)
    return row


# Adds to the matrix the connections described by the chain
def _disassemble_chain(matrix, chain, attenuation_constant):
    for chain_index, matrix_index in enumerate(chain):
        _create_connections(matrix, chain, attenuation_constant, chain_index, matrix_index)


# Helper for disassemble_chain
def _create_connections(matrix, chain, attenuation_constant, chain_index, matrix_index):
    strength = 1
    for index in range(chain_index + 1, len(chain)):
        matrix[matrix_index][chain[index]] += strength  # add to connection from matrix_index to chain[index]
        strength *= attenuation_constant  # Recursively weakens by the constant


def _relations_matrix(matrix):
    # Make matrix
    side_length = len(matrix)
    relation_matrix = []
    for index in range(side_length):
        relation_matrix.append(_make_row(side_length))

    for row_index, row in enumerate(matrix):
        for other_row_index in range(row_index + 1, side_length):
            angle = _find_angle(row, matrix[other_row_index])
            relation_matrix[row_index][other_row_index] = angle
            relation_matrix[other_row_index][row_index] = angle  # Symmetric because it's relational

    _display_matrix(relation_matrix, "Angles:")


# Displays the matrix with newlines and all that good stuff
def _display_matrix(matrix, answer_to_index):
    print(answer_to_index)
    for row in matrix:
        print(row)


# Using dot product (law of cosines)
def _find_angle(row1, row2):
    magnitude_product = _magnitude(row1) * _magnitude(row2)
    if magnitude_product == 0:
        return "NaN"
    print(_dot_product(row1, row2) / magnitude_product)
    return math.acos(_dot_product(row1, row2) / magnitude_product)


# Basic dot product
def _dot_product(row1, row2):
    ans = 0
    for index, value in enumerate(row1):
        ans += value * row2[index]
    return ans


# Magnitude of vector
def _magnitude(row):
    quadrature_sum = 0
    for value in row:
        quadrature_sum += math.pow(value, 2)
    return math.sqrt(quadrature_sum)
