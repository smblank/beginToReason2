"""
Main file for displaying graphs.
"""
import json
from data_analysis.py_helper_functions.graph_viewer.node import Node
from plantuml import deflate_and_encode
from data_analysis.models import DataLog
from core.models import Lesson

# Takes a lesson index and returns the START node of its graph representation
def lesson_to_graph(lesson_id):
    query = DataLog.objects.filter(
        lesson_key_id=lesson_id).order_by('user_key', 'time_stamp')
    nodes_in_chain = []
    start_node = Node(Node.START_NAME, False)
    end_node = Node(Node.GAVE_UP_NAME, False)
    prev_node = start_node
    nodes_in_chain.append(prev_node)
    prev_student = query[0].user_key
    for log in query:
        # Take only the (first) code between Confirm and ;
        log.code = log.code.split("Confirm")[1].split("\r")[
            0].strip().strip(";")
        prev_node.add_appearance(log.user_key)
        # Is this kid same as the last one?
        if log.user_key != prev_student:
            # Nope!
            if not prev_node.is_correct:
                # Last kid gave up
                prev_node.add_next(end_node, prev_student)
                end_node.add_appearance(prev_student)
            else:
                # Last kid got it right
                chain_length = len(nodes_in_chain)
                for node in nodes_in_chain:
                    chain_length -= 1
                    node.add_distance(chain_length)
                    node.add_successful_appearance()
            prev_student = log.user_key
            nodes_in_chain.clear()
            prev_node = start_node
            nodes_in_chain.append(prev_node)
            start_node.add_appearance(log.user_key)
        # Runs every time
        if log.status == 'failure':
            answer_correct = False
        else:
            # I think that the 'status' of a log is whether they got it wrong or right, with 'success' for a right
            # answer and 'failure' for a wrong one. This checks whether that's the case.
            if log.status != 'success':
                print("I don't know how status works, please send help!!!")
                print(log.status + " confused me")
            answer_correct = True
        current_node = start_node.find_node(log.code)
        if not current_node:
            current_node = Node(log.code, answer_correct)
        if current_node.is_correct != answer_correct:
            print("\n\n\nI (think I) found conflicting data!!!\n(It's probably a lesson with 2 confirms)\n\n\n")
        prev_node.add_next(current_node, log.user_key)
        nodes_in_chain.append(current_node)
        prev_node = current_node
    # Post iteration
    prev_node.add_appearance(prev_student)
    if not prev_node.is_correct:
        # Last kid gave up
        prev_node.add_next(end_node)
        end_node.add_appearance(prev_student)
    else:
        # Last kid got it right
        chain_length = len(nodes_in_chain)
        for node in nodes_in_chain:
            chain_length -= 1
            node.add_distance(chain_length)
            node.add_successful_appearance()
    return start_node


# Takes a lesson index and returns a JSON representation fit for D3
def lesson_to_json(lesson_id):
    root = lesson_to_graph(lesson_id)
    nodes = []
    edges = []
    for node in root.return_family():
        nodes.append(node.to_dict())
        for edge in node.edge_dict():
            edges.append(edge)
    return json.dumps({"nodes": nodes, "links": edges})


# Helper function
def find_optimal_min(node_list):
    appearances = []
    for node in node_list:
        appearances.append(node.appearances)
    appearances.sort()
    # 15 or less nodes will be allowed in graph
    max_nodes = 15
    if len(appearances) > max_nodes:
        return appearances[len(appearances) - max_nodes - 1] + 1
    # Just in case it's a teeny tiny lesson with a small amount of nodes
    return 0


def lesson_stats(lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    return json.dumps({"name": lesson.lesson_name, "title": lesson.lesson_title, "instruction": lesson.instruction, "code": lesson.code.lesson_code})