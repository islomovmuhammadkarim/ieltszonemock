from django.core.management.base import BaseCommand, CommandError
from listening.models import (
    ListeningTest,
    ListeningQuestionGroup,
    ListeningQuestion,
    ListeningOption,
)


class Command(BaseCommand):
    help = "Seed IELTS-style Listening (30 questions) with groups for a given ListeningTest."

    def add_arguments(self, parser):
        parser.add_argument("--test-id", type=int, required=True, help="ListeningTest ID (e.g. 1)")
        parser.add_argument("--force", action="store_true", help="Delete existing groups/questions for this test first")

    def handle(self, *args, **opts):
        test_id = opts["test_id"]
        force = opts["force"]

        test = ListeningTest.objects.filter(id=test_id).first()
        if not test:
            raise CommandError(f"ListeningTest id={test_id} not found.")

        if force:
            ListeningOption.objects.filter(question__test=test).delete()
            ListeningQuestion.objects.filter(test=test).delete()
            ListeningQuestionGroup.objects.filter(test=test).delete()
            self.stdout.write(self.style.WARNING("Existing listening data cleared (force=True)."))

        def get_group(order, part, group_type, title, instructions, data=None):
            g, _ = ListeningQuestionGroup.objects.get_or_create(
                test=test,
                order=order,
                defaults={
                    "part": part,
                    "group_type": group_type,
                    "title": title,
                    "instructions": instructions,
                    "data": data or {},
                },
            )
            # Update if exists (keep image untouched)
            g.part = part
            g.group_type = group_type
            g.title = title
            g.instructions = instructions
            g.data = data or {}
            g.save(update_fields=["part", "group_type", "title", "instructions", "data"])
            return g

        def upsert_question(
            order,
            part,
            qtype,
            group,
            prompt,
            instructions="",
            data=None,
            answer_key=None,
            options=None,
        ):
            q, created = ListeningQuestion.objects.get_or_create(
                test=test,
                order=order,
                defaults={
                    "part": part,
                    "qtype": qtype,
                    "group": group,
                    "prompt": prompt,
                    "instructions": instructions,
                    "data": data or {},
                    "answer_key": answer_key or {},
                },
            )
            # keep it idempotent
            q.part = part
            q.qtype = qtype
            q.group = group
            q.prompt = prompt
            q.instructions = instructions
            q.data = data or {}
            q.answer_key = answer_key or {}
            q.save(update_fields=["part", "qtype", "group", "prompt", "instructions", "data", "answer_key"])

            if options:
                for key, text in options:
                    ListeningOption.objects.get_or_create(
                        question=q,
                        key=key,
                        defaults={"text": text},
                    )
                    # update text if option exists
                    ListeningOption.objects.filter(question=q, key=key).update(text=text)

            return q, created

        # ---------------------------
        # GROUPS (IELTS-like)
        # ---------------------------
        g1 = get_group(
            order=1,
            part=1,
            group_type="notes",
            title="Part 1 — Form completion",
            instructions="Complete the form. Write NO MORE THAN ONE WORD AND/OR A NUMBER for each answer.",
            data={"default_max_words": 2},
        )

        g2 = get_group(
            order=2,
            part=2,
            group_type="map",
            title="Part 2 — Map/Plan",
            instructions="Look at the map. Choose the correct letter A–F.",
            data={"labels": ["A", "B", "C", "D", "E", "F"], "note": "Upload the map image in this group (admin)."},
        )

        g3 = get_group(
            order=3,
            part=2,
            group_type="mcq",
            title="Part 2 — Multiple choice",
            instructions="Choose the correct answer A, B or C.",
            data={},
        )

        g4 = get_group(
            order=4,
            part=3,
            group_type="mcq",
            title="Part 3 — Discussion (MCQ)",
            instructions="Choose the correct answer A, B or C.",
            data={},
        )

        g5 = get_group(
            order=5,
            part=4,
            group_type="notes",
            title="Part 4 — Lecture notes",
            instructions="Complete the notes. Write NO MORE THAN TWO WORDS AND/OR A NUMBER for each answer.",
            data={"default_max_words": 2},
        )

        created_questions = 0

        # ---------------------------
        # PART 1 (Q1–Q10) short / gap-fill (notes)
        # ---------------------------
        part1 = [
            (1, "Student’s surname", {"values": ["johnson"], "case_sensitive": False, "max_words": 1}),
            (2, "Booking type", {"values": ["interview"], "case_sensitive": False, "max_words": 1}),
            (3, "Preferred day", {"values": ["wednesday"], "case_sensitive": False, "max_words": 1}),
            (4, "Card required", {"values": ["student"], "case_sensitive": False, "max_words": 1}),
            (5, "Fee (number)", {"values": ["15", "fifteen"], "case_sensitive": False, "max_words": 1}),
            (6, "Arrival time", {"values": ["10:30", "10.30", "ten thirty"], "case_sensitive": False, "max_words": 2}),
            (7, "Building next to", {"values": ["library"], "case_sensitive": False, "max_words": 1}),
            (8, "ID document type", {"values": ["passport", "id"], "case_sensitive": False, "max_words": 1}),
            (9, "Room number", {"values": ["204", "two oh four"], "case_sensitive": False, "max_words": 2}),
            (10, "Contact email", {"values": ["info"], "case_sensitive": False, "max_words": 1}),
        ]
        for i, label, ak in part1:
            q, created = upsert_question(
                order=i,
                part=1,
                qtype="short",
                group=g1,
                prompt=f"{label}: ________",
                instructions="Write ONE word and/or a number.",
                data={"max_words": ak.get("max_words", 1)},
                answer_key=ak,
            )
            created_questions += int(created)

        # ---------------------------
        # PART 2 MAP (Q11–Q15) map
        # ---------------------------
        # Rasm: g2.image ni admin’da upload qilasiz
        map_items = [
            (11, "Information desk", "D"),
            (12, "Main entrance", "C"),
            (13, "Café", "A"),
            (14, "Car park", "F"),
            (15, "Ticket office", "B"),
        ]
        for order, place, correct in map_items:
            q, created = upsert_question(
                order=order,
                part=2,
                qtype="map",
                group=g2,
                prompt=f"Which letter shows the {place}?",
                instructions="Choose a letter A–F.",
                data={"pool": ["A", "B", "C", "D", "E", "F"]},
                answer_key={"value": correct},
            )
            created_questions += int(created)

        # ---------------------------
        # PART 2 MCQ (Q16–Q20) mcq_single
        # ---------------------------
        mcq2 = [
            (16, "What is the talk mainly about?", "B", [("A", "A campus tour"), ("B", "A city museum"), ("C", "A job interview")]),
            (17, "What time does the event start?", "A", [("A", "2 pm"), ("B", "3 pm"), ("C", "4 pm")]),
            (18, "Where is the meeting held?", "C", [("A", "Sports hall"), ("B", "Library"), ("C", "Main hall")]),
            (19, "What should visitors bring?", "B", [("A", "A passport"), ("B", "A printed ticket"), ("C", "A map")]),
            (20, "What is included in the price?", "A", [("A", "Entrance ticket"), ("B", "Free meal"), ("C", "Transport")]),
        ]
        for order, prompt, correct, options in mcq2:
            q, created = upsert_question(
                order=order,
                part=2,
                qtype="mcq_single",
                group=g3,
                prompt=prompt,
                instructions="Choose A, B or C.",
                data={},
                answer_key={"value": correct},
                options=options,
            )
            created_questions += int(created)

        # ---------------------------
        # PART 3 MCQ (Q21–Q25) mcq_single
        # ---------------------------
        mcq3 = [
            (21, "What is the students’ project topic?", "B", [("A", "Climate change"), ("B", "Urban transport"), ("C", "Online learning")]),
            (22, "What is the main research method?", "A", [("A", "A survey"), ("B", "Lab experiment"), ("C", "Field trip")]),
            (23, "Who will prepare the slides?", "C", [("A", "The tutor"), ("B", "Ben"), ("C", "Anna")]),
            (24, "When is the deadline?", "A", [("A", "Friday"), ("B", "Monday"), ("C", "Wednesday")]),
            (25, "What will they do next week?", "B", [("A", "Submit final report"), ("B", "Give a presentation"), ("C", "Start new topic")]),
        ]
        for order, prompt, correct, options in mcq3:
            q, created = upsert_question(
                order=order,
                part=3,
                qtype="mcq_single",
                group=g4,
                prompt=prompt,
                instructions="Choose A, B or C.",
                data={},
                answer_key={"value": correct},
                options=options,
            )
            created_questions += int(created)

        # ---------------------------
        # PART 4 (Q26–Q30) short / gap-fill (notes)
        # ---------------------------
        part4 = [
            (26, "The lecture is mainly about", {"values": ["solar energy", "renewable energy"], "case_sensitive": False, "max_words": 2}),
            (27, "The key factor is", {"values": ["temperature"], "case_sensitive": False, "max_words": 1}),
            (28, "The experiment used", {"values": ["water"], "case_sensitive": False, "max_words": 1}),
            (29, "The result showed", {"values": ["improvement", "increase"], "case_sensitive": False, "max_words": 1}),
            (30, "The final recommendation was", {"values": ["more research", "further research"], "case_sensitive": False, "max_words": 2}),
        ]
        for order, stem, ak in part4:
            q, created = upsert_question(
                order=order,
                part=4,
                qtype="short",
                group=g5,
                prompt=f"{stem}: ________",
                instructions="Write NO MORE THAN TWO WORDS AND/OR A NUMBER.",
                data={"max_words": ak.get("max_words", 2)},
                answer_key=ak,
            )
            created_questions += int(created)

        self.stdout.write(self.style.SUCCESS(
            f"Seed done for ListeningTest #{test.id}. Created new questions: {created_questions}. "
            f"Total questions now: {ListeningQuestion.objects.filter(test=test).count()}."
        ))
        self.stdout.write(self.style.WARNING(
            "Map image: Admin panelda Group (type=map) ga kirib rasm (image) ni upload qiling."
        ))
