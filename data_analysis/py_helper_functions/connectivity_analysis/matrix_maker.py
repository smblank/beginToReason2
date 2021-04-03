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
            _disassemble_chain(matrix, chain, attenuation_constant)
        chain.append(answer_to_index.get(log.code))
    # Post iteration, gotta do this for the last student
    _disassemble_chain(matrix, chain, attenuation_constant)
    _display_matrix(matrix, answer_to_index)


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


# Adds to the matrix the connections described by the chain. Empties chain when done
def _disassemble_chain(matrix, chain, attenuation_constant):
    for chain_index, matrix_index in enumerate(chain):
        _create_connections(matrix, chain, attenuation_constant, chain_index, matrix_index)
    chain = []


# Helper for disassemble_chain
def _create_connections(matrix, chain, attenuation_constant, chain_index, matrix_index):
    strength = 1
    for index in range(chain_index + 1, len(chain)):
        matrix[matrix_index][chain[index]] += strength
        matrix[chain[index]][matrix_index] += strength
        strength *= attenuation_constant  # Recursively weakens by the constant


# Displays the matrix with newlines and all that good stuff
def _display_matrix(matrix, answer_to_index):
    print(answer_to_index)
    for row in matrix:
        print(row)
