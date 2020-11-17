"""
This module contains our Django views for the "tutor" application.
"""
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from core.models import Lesson, LessonSet
from accounts.models import UserInformation
from data_analysis.py_helper_functions.datalog_helper import log_data, get_log_data, finished_lesson_count
from tutor.py_helper_functions.tutor_helper import user_auth, lesson_set_auth, check_feedback, not_complete
from tutor.py_helper_functions.mutation import reverse_mutate, can_mutate, get_inv_key


def catalog(request):
    """function catalog This function handles the view for the catalog page of the application.
    Args:
        request (HTTPRequest): A http request object created automatically by Django.
    Returns:
        HttpResponse: A generated http response object to the request depending on whether or not
                      the user is authenticated.
    """
    # get all lesson sets, display
    if request.method == 'POST':
        if user_auth(request):
            # search for lesson set
            if lesson_set_auth(request):
                return redirect("/tutor/tutor")
            else:
                return redirect("accounts:profile")
        else:
            return redirect("/accounts/settings")
    else:
        return render(request, "tutor/catalog.html", {'LessonSet': LessonSet.objects.all()})


@login_required(login_url='/accounts/login/')
def tutor(request):
    """function tutor This function handles the view for the tutor page of the application.
    Args:
        request (HTTPRequest): A http request object created automatically by Django.
    Returns:
        HttpResponse: A generated http response object to the request depending on whether or not
                      the user is authenticated.
    """

    print(request)

    # Case 1: We have received a POST request submitting code (needs a lot of work)
    if request.method == 'POST':
        # Case 1a: if the user exists
        if user_auth(request):
            # submitted_json = json.loads(request.body.decode('utf-8'))
            # if success, return next lesson
            # if fail, do something
            # Case 1aa: if the user has not completed set

            current_user = UserInformation.objects.get(user=User.objects.get(email=request.user.email))
            print(current_user.current_lesson_name)
            current_lesson = Lesson.objects.get(lesson_name=current_user.current_lesson_name)
            print('current_lesson: ', current_lesson)
            submitted_answer = reverse_mutate(json.loads(request.body.decode('utf-8'))['answer'].replace(" ", ""), get_inv_key())
            print('submitted answer: ' + submitted_answer)
            #Need to include submitted_answer in log data because it has the original variables

            log_data(request, submitted_answer)

            status = json.loads(request.body.decode('utf-8'))['status']
            print("status: ", status)

            if status == "success":
                current_user.completed_lesson_index = current_lesson.lesson_index

                if Lesson.objects.filter(lesson_name=current_lesson.correct).exists():
                    current_user.current_lesson_index = Lesson.objects.get(
                        lesson_name=current_lesson.correct).lesson_index
                else:
                    print("Lesson does not exist")

                print("completed index: ", current_user.completed_lesson_index)
                print("current index: ", current_user.current_lesson_index)

                if Lesson.objects.filter(lesson_index=current_user.current_lesson_index).exists():
                    curr_lesson = Lesson.objects.get(lesson_index=current_user.current_lesson_index)
                    print('curr_lesson: ', current_lesson)
                    current_user.current_lesson_name = curr_lesson.lesson_name
                    current_user.save()
                    if current_user.completed_lesson_index == current_user.current_lesson_index:
                        current_user.completed_sets = current_user.current_lesson_set
                        current_user.current_lesson_set = None
                        current_user.save()
                        print("in done: ", current_user.current_lesson_set)

            # print(feedback['type'])
            # goto = alternate_lesson_check(current_lesson, feedback['type'])
            # feedback.update({'newLessonIndex': str(Lesson.objects.get(lesson_name=goto.lesson_name).lesson_index)})
            # feedback.update({'newLessonCode': Lesson.objects.get(lesson_name=goto.lesson_name).code.lesson_code})
            # feedback.update({'newLessonEx': Lesson.objects.get(lesson_name=goto.lesson_name).reason.reasoning_type})

            return JsonResponse(check_feedback(current_lesson, submitted_answer, status))

    # Case 2: We have received a GET request requesting code
    elif request.method == 'GET':
        # Ensure user exists
        # Case 2a: if the user exists
        print(not_complete(request))
        if user_auth(request) and not_complete(request):
            # Case 2aa: if the user has a current set
            current_user = UserInformation.objects.get(user=User.objects.get(email=request.user.email))
            current_set = current_user.current_lesson_set.lessons.all()
            set_len = current_set.filter(is_alternate=False).count()
            print(set_len)
            num_done = finished_lesson_count(current_user)
            # Case 2aaa: if the current set has a lesson of index that the user is on, set to current lesson
            if Lesson.objects.filter(lesson_index=current_user.current_lesson_index).exists():
                current_lesson = Lesson.objects.get(lesson_index=current_user.current_lesson_index)

                # check if mutatable then mutate:
                code_after_mutate = can_mutate(request)

                if current_lesson.reason.reasoning_type == 'MC' or current_lesson.reason.reasoning_type == 'Both':
                    return render(request, "tutor/tutor.html",
                                  {'lesson': current_lesson,
                                   'lesson_code': code_after_mutate,
                                   'concept': current_lesson.lesson_concept.all(),
                                   'referenceSet': current_lesson.reference_set.all(),
                                   'reason': current_lesson.reason.reasoning_question,
                                   'mc_set': current_lesson.reason.mc_set.all(),
                                   'currLessonNum': current_user.current_lesson_index,
                                   'completedLessonNum': current_user.completed_lesson_index,
                                   'setLength': set_len,
                                   'finished_count': num_done,
                                   'currSet': current_set,
                                   'mood': current_user.mood,
                                   'review': 'none',
                                   'screen_record': current_lesson.screen_record,
                                   'audio_record': current_lesson.audio_record,
                                   'audio_transcribe': current_lesson.audio_transcribe,
                                   'user_email': request.user.email})
                # Case 2aaab: if question is of type Text
                elif current_lesson.reason.reasoning_type == 'Text':
                    return render(request, "tutor/tutor.html",
                                  {'lesson': current_lesson,
                                   'lesson_code': code_after_mutate,
                                   'concept': current_lesson.lesson_concept.all(),
                                   'referenceSet': current_lesson.reference_set.all(),
                                   'reason': current_lesson.reason.reasoning_question,
                                   'currLessonNum': current_user.current_lesson_index,
                                   'completedLessonNum': current_user.completed_lesson_index,
                                   'setLength': set_len,
                                   'finished_count': num_done,
                                   'currSet': current_set,
                                   'mood': current_user.mood,
                                   'review': 'none',
                                   'screen_record': current_lesson.screen_record,
                                   'audio_record': current_lesson.audio_record,
                                   'audio_transcribe': current_lesson.audio_transcribe,
                                   'user_email': request.user.email})
                # Case 2aaac: if question is of type none

                return render(request, "tutor/tutor.html",
                              {'lesson': current_lesson,
                               'lesson_code': code_after_mutate,
                               'concept': current_lesson.lesson_concept.all(),
                               'referenceSet': current_lesson.reference_set.all(),
                               'currLessonNum': current_user.current_lesson_index,
                               'completedLessonNum': current_user.completed_lesson_index,
                               'setLength': set_len,
                               'finished_count': num_done,
                               'currSet': current_set,
                               'mood': current_user.mood,
                               'review': 'none',
                               'screen_record': current_lesson.screen_record,
                               'audio_record': current_lesson.audio_record,
                               'audio_transcribe': current_lesson.audio_transcribe,
                               'user_email': request.user.email})
    return redirect("accounts:profile")


@login_required(login_url='/accounts/login/')
def completed(request, index):
    """function previous This function handles retrieving the prev lesson.
        Args:
            request (HTTPRequest): A http request object created automatically by Django.
            index (int): The index of the lesson to retrieve
        Returns:
            HttpResponse: A generated http response object to the request depending on whether or not
                          the user is authenticated.
        """
    if request.method == 'GET':
        if user_auth(request):
            current_user = UserInformation.objects.get(user=User.objects.get(email=request.user.email))
            if not not_complete(request):
                current_set = current_user.completed_sets.lessons.all()
            else:
                current_set = current_user.current_lesson_set.lessons.all()
            current_lesson = Lesson.objects.get(lesson_index=index)

            set_len = current_set.filter(is_alternate=False).count()
            print(set_len)
            num_done = finished_lesson_count(current_user)

            if index <= current_user.completed_lesson_index:
                lesson_info = get_log_data(current_user, index)
                print("lesson info: ", index)
                return render(request, "tutor/tutor.html",
                              {'lesson': current_lesson,
                               'lesson_code': lesson_info[0],
                               'concept': current_lesson.lesson_concept.all(),
                               'referenceSet': current_lesson.reference_set.all(),
                               'currLessonNum': current_user.current_lesson_index,
                               'setLength': set_len,
                               'finished_count': num_done,
                               'currSet': current_set,
                               'mood': lesson_info[1],
                               'past': lesson_info[2],
                               'completedLessonNum': current_user.completed_lesson_index,
                               'review': current_lesson.correct_feedback})
            return redirect("tutor:tutor")

    return redirect("accounts:profile")
