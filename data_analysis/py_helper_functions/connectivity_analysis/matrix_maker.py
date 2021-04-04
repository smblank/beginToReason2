import math
import csv
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
    matrix, answer_to_index, answer_count = _create_matrix(query)
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
    matrix, relation_matrix, index_to_answer, answer_count = \
        _hierarchical_clustering(matrix, _relations_matrix(matrix),
                                 _reverse_dict(answer_to_index, answer_count), math.pi / 6, answer_count)
    _write_to_csv(matrix, _relations_matrix(matrix), index_to_answer, "matrix_results_rads_pi", answer_count)


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
    return matrix, answer_to_index, answers_found


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
        for other_row_index in range(row_index, side_length):
            # relation_strength = (math.pi / 2 - _find_angle(row, matrix[other_row_index])) / (math.pi / 2)
            relation_strength = _find_angle(row, matrix[other_row_index])
            relation_matrix[row_index][other_row_index] = relation_matrix[other_row_index][row_index] = \
                relation_strength
            # Symmetric because it's relational

    return relation_matrix


# Using dot product (law of cosines)
def _find_angle(row1, row2):
    magnitude_product = _magnitude(row1) * _magnitude(row2)
    if magnitude_product == 0:
        return float("NaN")
    cos_theta = _dot_product(row1, row2) / magnitude_product
    if cos_theta > 1:
        print("UH-OH! gonna round " + str(cos_theta) + " to 1... hope nobody notices")
        return 0
    return math.acos(cos_theta)


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


def _write_to_csv(prediction_matrix, relation_matrix, answers_list, file_name, dimension):
    prediction_matrix = _add_headers(prediction_matrix, answers_list, "FROM\\TO")
    relation_matrix = _add_headers(relation_matrix, answers_list, "")
    csv_file = open(file_name + ".csv", 'w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(["Predictions"])
    writer.writerows(prediction_matrix)
    writer.writerows([[], ["Relations"]])
    writer.writerows(relation_matrix)
    csv_file.close()


def _reverse_dict(dictionary, list_length):
    index_to_ans = [""] * list_length
    for pair in dictionary.items():
        if not index_to_ans[pair[1]]:
            index_to_ans[pair[1]] = pair[0]
    return index_to_ans


def _add_headers(matrix, headers, top_left):
    # Add on left
    for index, row in enumerate(matrix):
        matrix[index] = [headers[index]] + row

    # Add on top
    matrix = [[top_left] + headers] + matrix

    return matrix


def _hierarchical_clustering(connection_matrix, distance_matrix, index_to_answer, max_distance, dimension):
    # Find closest pair
    record_angle = 400
    record_row = -1
    record_col = -1
    for row_index, row in enumerate(distance_matrix):
        for col_index in range(row_index + 1, dimension):
            if row[col_index] < record_angle:
                record_angle = row[col_index]
                record_col = col_index
                record_row = row_index

    # Base case
    if record_angle > max_distance:
        return connection_matrix, distance_matrix, index_to_answer, dimension

    # Update index_to_answer list
    index_to_answer[record_row] += " & " + index_to_answer[record_col]
    index_to_answer.pop(record_col)

    # Add rows together
    for index, val in enumerate(connection_matrix[record_col]):
        connection_matrix[record_row][index] += val

    # Add cols together, delete old col
    for index in range(dimension):
        row = connection_matrix[index]
        row[record_row] += row[record_col]
        row.pop(record_col)

    # Delete old row
    connection_matrix.pop(record_col)

    # Recalculate distances
    distance_matrix = _relations_matrix(connection_matrix)

    # Recursive
    return _hierarchical_clustering(connection_matrix, distance_matrix, index_to_answer, max_distance, dimension - 1)
