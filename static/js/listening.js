document.addEventListener("DOMContentLoaded", function() {
    const audio = document.getElementById("mainAudio");
    const checkAudio = document.getElementById("checkAudio");
    const overlay = document.getElementById("startOverlay");
    const content = document.getElementById("listeningContent");
    const groups = Array.from(document.querySelectorAll(".listening-group"));
    
    let currentStep = 1;
    let timeRemaining = TOTAL_TIME;
    let testStarted = false;

    // 1. START TEST
    document.getElementById("btnStart").onclick = () => {
        checkAudio.pause();
        overlay.style.display = "none";
        content.style.display = "block";
        testStarted = true;
        audio.play();
        startTimer();
    };

    // 2. TIMER LOGIC
    function startTimer() {
        const timerText = document.getElementById("timerText");
        const interval = setInterval(() => {
            if (timeRemaining <= 0) {
                clearInterval(interval);
                finishTest();
            }
            timeRemaining--;
            const m = Math.floor(timeRemaining / 60);
            const s = timeRemaining % 60;
            timerText.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        }, 1000);
    }

    // 3. NAVIGATION (MAP Fix bilan)
    function showStep(step) {
        groups.forEach(g => g.style.display = "none");
        const activeGroup = document.querySelector(`.listening-group[data-step="${step}"]`);
        if (activeGroup) {
            activeGroup.style.display = "block";
            document.getElementById("groupLabel").textContent = step;
        }
        window.scrollTo(0, 0);
    }

    document.getElementById("btnNext").onclick = () => {
        if (currentStep < groups.length) {
            currentStep++;
            showStep(currentStep);
        }
    };

    document.getElementById("btnPrev").onclick = () => {
        if (currentStep > 1) {
            currentStep--;
            showStep(currentStep);
        }
    };

    // 4. AUTO-SAVE (Map tanlash muammosini hal qiladi)
    document.addEventListener("change", (e) => {
        if (e.target.hasAttribute("data-qid")) {
            const qid = e.target.getAttribute("data-qid");
            const val = e.target.value;
            
            fetch(SAVE_URL, {
                method: "POST",
                headers: { 
                    "X-CSRFToken": CSRF_TOKEN,
                    "Content-Type": "application/x-www-form-urlencoded" 
                },
                body: `question_id=${qid}&value=${encodeURIComponent(val)}`
            });
        }
    });

    // 5. FINISH
    async function finishTest() {
        if(confirm("Testni yakunlaysizmi?")) {
            const res = await fetch(SUBMIT_URL, {
                method: "POST",
                headers: { "X-CSRFToken": CSRF_TOKEN }
            });
            const data = await res.json();
            window.location.href = data.redirect;
        }
    }
    document.getElementById("btnFinish").onclick = finishTest;
});