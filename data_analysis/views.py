"""
This module contains our Django views for the "data_analysis" application.
"""
from django.shortcuts import render, redirect
from tutor.py_helper_functions.tutor_helper import user_auth_inst, lesson_set_auth
from data_analysis.py_helper_functions.lesson_stats import get_set_stats, get_set_name
from data_analysis.py_helper_functions.graph_viewer.lesson_reader import lesson_to_json, lesson_stats


# Create your views here.
def d3_graph(request, index):
    print(request)
    return render(request, "data_analysis/d3graph.html", {'graphData': lesson_to_json(index),
                                                          'lessonData': lesson_stats(index)})


def set_statistics(request, index):
    print(request)
    return render(request, "data_analysis/setStatistics.html", {'lessonSetData': get_set_stats(index),
                                                                'lessonSetName': get_set_name(index)})


def instructor(request):
    """function instructor This function handles the view for the instructor page of the application.

    Args:
        request (HTTPRequest): A http request object created automatically by Django.

    Returns:
        HttpResponse: A generated http response object to the request.
    """

    # get all lesson sets, display
    if request.method == 'POST':
        # Will this include where the data is updated? Such as selecting different visuals to interact with?
        if user_auth_inst(request):
            # Take instructor to data view
            if lesson_set_auth(request):
                return redirect("/tutor/tutor")
            else:
                return redirect("accounts:profile")
        else:
            return redirect("/accounts/settings")
    else:
        return render(request, "data_analysis/visual.html")
