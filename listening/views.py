from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from attempts.models import Attempt
from mocks.models import MockSection
from listening.models import (
    ListeningTest,
    ListeningQuestionGroup,
    ListeningQuestion,
    ListeningAttemptAnswer,
)


def _get_active_attempt(request) -> Attempt | None:
    attempt_id = request.session.get("active_attempt_id")
    if not attempt_id:
        return None
    return Attempt.objects.select_related("mock").filter(id=attempt_id).first()


def _get_listening_test_for_attempt(attempt: Attempt) -> ListeningTest:
    section = get_object_or_404(MockSection, mock=attempt.mock, section="listening")
    return get_object_or_404(ListeningTest, section=section)


def _ensure_attempt_ok(request) -> Attempt | None:
    """
    Listening page va API lar uchun umumiy guard:
    - attempt bo'lishi shart
    - status in_progress bo'lishi shart
    - current_section listening bo'lishi shart
    """
    attempt = _get_active_attempt(request)
    if not attempt:
        return None
    if attempt.status != "in_progress":
        return None
    if attempt.current_section != "listening":
        return None
    return attempt


@login_required
@require_http_methods(["GET"])
def listening_page(request):
    attempt = _get_active_attempt(request)
    if not attempt:
        return redirect("mock_list")

    # attempt tugagan bo'lsa qayta kirishni bloklaymiz (audio bug fix)
    if attempt.status != "in_progress":
        return redirect("mock_detail", slug=attempt.mock.slug)

    # section boshqa bo'lsa instructionsga qaytaramiz
    if attempt.current_section != "listening":
        return redirect(f"/{attempt.current_section}/")

    test = _get_listening_test_for_attempt(attempt)

    groups = (
        ListeningQuestionGroup.objects
        .filter(test=test)
        .prefetch_related("questions__options")
        .order_by("order")
    )

    return render(
        request,
        "listening/test.html",
        {
            "attempt": attempt,
            "test": test,
            "groups": groups,
            "total_seconds": test.duration_seconds,
        }
    )


def _normalize_response(q: ListeningQuestion, raw_value: str) -> dict:
    """
    Frontend save-answer endpointdan keladigan value ni qtype bo'yicha JSONga aylantiramiz.
    HTML template'da:
      - short -> input value (string)
      - tfng/map/mcq_single -> select value (string)
      - mcq_multi -> "A,C" ko'rinishida keladi (string)
    """
    raw_value = (raw_value or "").strip()

    if q.qtype == "mcq_multi":
        # "A,C" -> ["A","C"]
        values = [x.strip() for x in raw_value.split(",") if x.strip()]
        return {"values": values}

    if q.qtype == "short":
        return {"text": raw_value}

    # tfng, map, mcq_single, matching va boshqalar:
    return {"value": raw_value}


@login_required
@require_POST
def listening_save_answer(request):
    attempt = _ensure_attempt_ok(request)
    if not attempt:
        return HttpResponseForbidden()

    test = _get_listening_test_for_attempt(attempt)

    qid = request.POST.get("question_id")
    value = request.POST.get("value", "")

    if not qid:
        return JsonResponse({"ok": False, "error": "question_id required"}, status=400)

    # Savol shu testga tegishli bo'lishi shart (xavfsizlik)
    question = get_object_or_404(ListeningQuestion, id=qid, test=test)

    response = _normalize_response(question, value)

    ListeningAttemptAnswer.objects.update_or_create(
        attempt=attempt,
        question=question,
        defaults={"response": response},
    )

    return JsonResponse({"ok": True})


@login_required
@require_POST
def listening_submit(request):
    """
    Finish bosilganda:
      - attempt listening yakunlandi (status o'zgartirmaymiz, chunki full mock davom etadi)
      - current_section -> reading
    """
    attempt = _ensure_attempt_ok(request)
    if not attempt:
        # Agar attempt yo'q yoki tugagan bo'lsa mock detailga qaytaramiz
        attempt0 = _get_active_attempt(request)
        if attempt0:
            return JsonResponse({"ok": False, "redirect": f"/mocks/{attempt0.mock.slug}/"}, status=400)
        return JsonResponse({"ok": False, "redirect": "/mocks/"}, status=400)

    # Listening tugadi -> readingga o'tamiz
    attempt.current_section = "reading"
    attempt.save(update_fields=["current_section"])

    return JsonResponse({"ok": True, "redirect": "/reading/"})


@login_required
@require_POST
def listening_terminate(request):
    """
    Pause/ended/cheat bo'lsa:
    - attempt.status = terminated
    - finished_at qo'yiladi
    """
    attempt = _get_active_attempt(request)
    if not attempt:
        return JsonResponse({"ok": False, "redirect": "/mocks/"}, status=400)

    if attempt.status == "in_progress":
        attempt.status = "terminated"
        attempt.finished_at = timezone.now()
        attempt.save(update_fields=["status", "finished_at"])

    return JsonResponse({"ok": True, "redirect": f"/mocks/{attempt.mock.slug}/"})
