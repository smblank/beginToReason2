import json
from data_analysis.models import DataLog
from core.models import Lesson, LessonSet


# Returns JSON array of lessons in the set
def get_set_stats(lesson_set_id):
    lesson_set_list = []
    for index, lesson in enumerate(LessonSet.objects.get(id=lesson_set_id).lessons.all()):
        if not lesson.is_alternate:
            # Throwing out alternate lessons
            lesson_set_list.append(_get_lesson_stats(lesson, index))
    return json.dumps({"lessons": lesson_set_list, "statBounds": _find_stat_ranges(lesson_set_list)})


# Returns the set's info (name, id)
def get_set_info(lesson_set_id):
    return {"name": LessonSet.objects.get(id=lesson_set_id).set_name, "id": lesson_set_id}


"""
Helper Methods
"""


# Returns a dict of a single lesson for lesson statistics
def _get_lesson_stats(lesson, index):
    lesson_dict = {"name": lesson.lesson_name, "title": lesson.lesson_title}
    lesson_dict.update(_get_user_stats(lesson, index))
    return lesson_dict


# Returns a dictionary of the user-specific stats (e.g. avg. num of attempts)
def _get_user_stats(lesson, index):
    query = DataLog.objects.filter(
        lesson_key_id=lesson.id).order_by('user_key', 'time_stamp')
    if not query:
        # Means that no students have taken the lesson yet
        return {"userCount": 0, "completionRate": 0, "firstTryRate": 0, "averageAttempts": 0, "lessonIndex": index}
    user_count = 1
    completions = 0
    attempts = 0
    first_try = int(query[0].status == 'correct')
    prev_student = query[0].user_key
    for log in query:
        if log.user_key != prev_student:
            # New student!
            user_count += 1
            prev_student = log.user_key
            first_try += int(log.status == 'success')
        completions += int(log.status == 'success')
        attempts += 1
    return {"userCount": user_count, "completionRate": completions / user_count, "firstTryRate": first_try / user_count,
            "averageAttempts": attempts / user_count, "lessonIndex": index}


# Gets the ranges that outliers lie out of
def _find_stat_ranges(lesson_set_list):
    completion_rate = []
    first_try = []
    average_attempts = []
    length = 0
    for lesson in lesson_set_list:
        if not lesson.get("userCount"):
            continue
        length += 1
        completion_rate.append(lesson.get("completionRate"))
        first_try.append(lesson.get("firstTryRate"))
        average_attempts.append(lesson.get("averageAttempts"))
    return {"completionRate": _get_normal_range(completion_rate, length),
            "firstTryRate": _get_normal_range(first_try, length),
            "averageAttempts": _get_normal_range(average_attempts, length)}


# Currently returning just the quartiles because 1.5*IQR was too lenient
def _get_normal_range(data_list, list_length):
    data_list.sort()
    half_length = int(list_length / 2)

    if half_length % 2:
        # It's odd!
        quartile_1 = data_list[int(half_length / 2)]
        quartile_3 = data_list[list_length - int((half_length + 1) / 2)]
    else:
        # It's even!
        quartile_1 = (data_list[half_length / 2] + data_list[half_length / 2 - 1]) / 2
        quartile_3 = (data_list[list_length - half_length / 2] + data_list[list_length - half_length / 2 - 1]) / 2

    inter_quartile = quartile_3 - quartile_1
    return quartile_1, quartile_3
