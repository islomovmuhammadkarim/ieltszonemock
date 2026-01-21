from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods

from attempts.models import Attempt
from mocks.models import MockSection
from .models import (
    ReadingTest, ReadingPassage, ReadingQuestionGroup,
    ReadingQuestion, ReadingAttemptAnswer
)

def _get_active_attempt(request):
    attempt_id = request.session.get("active_attempt_id")
    if not attempt_id:
        return None
    return Attempt.objects.select_related("mock").filter(id=attempt_id).first()

def _get_reading_test(attempt):
    section = get_object_or_404(MockSection, mock=attempt.mock, section="reading")
    return get_object_or_404(ReadingTest, section=section)

def _ensure_attempt_ok(request):
    attempt = _get_active_attempt(request)
    if not attempt:
        return None
    if attempt.status != "in_progress":
        return None
    if attempt.current_section != "reading":
        return None
    return attempt

@login_required
@require_http_methods(["GET"])
def reading_page(request):
    attempt = _get_active_attempt(request)
    if not attempt:
        return redirect("mock_list")
    if attempt.status != "in_progress":
        return redirect("mock_detail", slug=attempt.mock.slug)
    if attempt.current_section != "reading":
        return redirect("mock_detail", slug=attempt.mock.slug)

    test = _get_reading_test(attempt)

    passages = (
        ReadingPassage.objects
        .filter(test=test)
        .prefetch_related("groups__questions__options")
        .order_by("order")
    )

    return render(request, "reading/test.html", {
        "attempt": attempt,
        "test": test,
        "passages": passages,
        "total_seconds": test.duration_seconds,
    })

def _normalize_response(q: ReadingQuestion, raw_value: str) -> dict:
    raw_value = (raw_value or "").strip()

    if q.qtype in ("mcq_multi",):
        values = [x.strip() for x in raw_value.split(",") if x.strip()]
        return {"values": values}

    if q.qtype in ("short",):
        return {"text": raw_value}

    return {"value": raw_value}

@login_required
@require_POST
def reading_save_answer(request):
    attempt = _ensure_attempt_ok(request)
    if not attempt:
        return HttpResponseForbidden()

    test = _get_reading_test(attempt)

    qid = request.POST.get("question_id")
    value = request.POST.get("value", "")
    if not qid:
        return JsonResponse({"ok": False, "error": "question_id required"}, status=400)

    question = get_object_or_404(ReadingQuestion, id=qid, test=test)
    response = _normalize_response(question, value)

    ReadingAttemptAnswer.objects.update_or_create(
        attempt=attempt,
        question=question,
        defaults={"response": response},
    )
    return JsonResponse({"ok": True})

@login_required
@require_POST
def reading_submit(request):
    attempt = _ensure_attempt_ok(request)
    if not attempt:
        return JsonResponse({"ok": False, "redirect": "/mocks/"}, status=400)

    attempt.current_section = "writing"
    attempt.save(update_fields=["current_section"])
    return JsonResponse({"ok": True, "redirect": "/writing/"})

@login_required
@require_POST
def reading_terminate(request):
    attempt = _get_active_attempt(request)
    if not attempt:
        return JsonResponse({"ok": False, "redirect": "/mocks/"}, status=400)

    if attempt.status == "in_progress":
        attempt.status = "terminated"
        attempt.finished_at = timezone.now()
        attempt.save(update_fields=["status", "finished_at"])

    return JsonResponse({"ok": True, "redirect": f"/mocks/{attempt.mock.slug}/"})
