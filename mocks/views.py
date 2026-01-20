from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from .models import Mock, MockSection, MockAccess
from attempts.models import Attempt


def _has_access(user, mock: Mock) -> bool:
    if mock.is_free:
        return True
    if not user.is_authenticated:
        return False
    return MockAccess.objects.filter(user=user, mock=mock).exists()


def _section_questions_count(section: MockSection) -> int | None:
    try:
        if section.section == "listening" and hasattr(section, "listening_test"):
            return section.listening_test.questions.count()
        if section.section == "reading" and hasattr(section, "reading_test"):
            return section.reading_test.questions.count()
        if section.section == "writing" and hasattr(section, "writing_test"):
            return section.writing_test.tasks.count()
        if section.section == "speaking" and hasattr(section, "speaking_test"):
            return section.speaking_test.parts.count()
    except Exception:
        return None
    return None


@require_http_methods(["GET"])
def mock_list(request):
    mocks = Mock.objects.filter(is_active=True).order_by("-id")
    return render(request, "mocks/start_mock.html", {"mocks": mocks})


@require_http_methods(["GET"])
def mock_detail(request, slug):
    mock = get_object_or_404(Mock, slug=slug, is_active=True)
    has_access = _has_access(request.user, mock)

    sections = list(mock.sections.all())
    for s in sections:
        s.duration_minutes = (s.duration_seconds // 60) if s.duration_seconds else None
        s.questions_count = _section_questions_count(s)

    return render(
        request,
        "mocks/mock_detail.html",
        {"mock": mock, "sections": sections, "has_access": has_access},
    )


@login_required
@require_http_methods(["GET", "POST"])
def mock_start(request, slug):
    mock = get_object_or_404(Mock, slug=slug, is_active=True)

    if not _has_access(request.user, mock):
        return redirect("mock_detail", slug=mock.slug)

    # qaysi section’dan boshlash (template: ?section=<id>)
    section_id = request.GET.get("section")
    if section_id:
        section_obj = get_object_or_404(MockSection, id=section_id, mock=mock)
        start_section = section_obj.section
    else:
        start_section = "listening"

    # oldingi active attemptni terminate
    active_attempt_id = request.session.get("active_attempt_id")
    if active_attempt_id:
        Attempt.objects.filter(id=active_attempt_id, status="in_progress").update(
            status="terminated",
            finished_at=timezone.now(),
        )

    attempt = Attempt.objects.create(
        mock=mock,
        status="in_progress",
        current_section=start_section,
    )

    request.session["active_attempt_id"] = attempt.id
    request.session["active_mock_slug"] = mock.slug

    return redirect(f"/{start_section}/")
