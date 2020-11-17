"""
This module contains our Django helper functions for the "data analysis" application.
"""
import json
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import UserInformation
from core.models import LessonSet, Lesson
from data_analysis.models import DataLog


def log_data(request, reverseMutatedCode):
    """function log_data This function handles the logic for logging data
    Args:
         request (HTTPRequest): A http request object created automatically by Django.
         reverseMutatedCode: this is a string that has been changed back to the oringinal code
    Returns:
    """
    user = User.objects.get(email=request.user.email)
    user_info = UserInformation.objects.get(user=user)
    lesson_set = user_info.current_lesson_set
    lesson = Lesson.objects.get(lesson_index=user_info.current_lesson_index)
    explanation = json.loads(request.body.decode('utf-8'))['explanation']
    past_answers = json.loads(request.body.decode('utf-8'))['allAnswers']
    status = json.loads(request.body.decode('utf-8'))['status']
    face = json.loads(request.body.decode('utf-8'))['face']
    user_info.mood = face
    user_info.save()

    print("data_logged")

    data_to_log = DataLog.objects.create(user_key=user,
                                         time_stamp=timezone.now(),
                                         lesson_set_key=lesson_set,
                                         lesson_key=lesson,
                                         status=status,
                                         code=reverseMutatedCode,
                                         explanation=explanation,
                                         past_answers = past_answers,
                                         face=face)
    data_to_log.save()

def get_log_data(user, lesson_index):
    user = User.objects.get(email=user)
    print(user)
    get_user_successes = DataLog.objects.filter(user_key=user)

    print(get_user_successes.filter(lesson_key=Lesson.objects.get(lesson_index=lesson_index)))
    get_lesson = get_user_successes.filter(lesson_key=Lesson.objects.get(lesson_index=lesson_index)).order_by('-id')[0]

    print(get_lesson)
    return repr(get_lesson.code).replace("'",''), get_lesson.face, get_lesson.past_answers, get_lesson.explanation

def finished_lesson_count(user):
    user = User.objects.get(email=user)

    get_user_successes = DataLog.objects.filter(user_key=user).filter(status='success')
    print(get_user_successes.count())

    return get_user_successes.count()
