from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
    if not enrollment:
        enrollment = Enrollment.objects.create(user=user, course=course)

    selected_choice_ids = [
        int(value) for key, value in request.POST.items() if key.startswith('choice_')
    ]

    submission = Submission.objects.create(enrollment=enrollment)
    selected_choices = Choice.objects.filter(id__in=selected_choice_ids)
    submission.choices.set(selected_choices)
    submission.save()

    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)


def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    total_score = 0
    total_grade = 0
    selected_ids = submission.choices.values_list('id', flat=True)

    for question in course.question_set.all():
        total_grade += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade

    percent = (total_score / total_grade) * 100 if total_grade > 0 else 0

    context['course'] = course
    context['submission'] = submission
    context['total_score'] = total_score
    context['total_grade'] = total_grade
    context['percent'] = round(percent, 2)
    context['selected_ids'] = selected_ids

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
