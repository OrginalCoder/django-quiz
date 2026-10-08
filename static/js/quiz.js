document.addEventListener("DOMContentLoaded", () => {
  const quizContainer = document.getElementById("quizApp");
  if (!quizContainer) return;

  const categorySlug = quizContainer.dataset.categorySlug;
  const questionApiUrl = `/quiz/${categorySlug}/question/`;
  const answerApiUrl = `/quiz/${categorySlug}/answer/`;

  const questionTextEl = document.getElementById("questionText");
  const choicesContainerEl = document.getElementById("choicesContainer");
  const progressBarEl = document.getElementById("progressBarFill");
  const progressTextEl = document.getElementById("progressText");
  const difficultyPillEl = document.getElementById("difficultyPill");
  const pointsBadgeEl = document.getElementById("pointsBadge");
  const timerCircleEl = document.getElementById("timerCircle");
  const timerTextEl = document.getElementById("timerText");
  const codeSnippetBoxEl = document.getElementById("codeSnippetBox");

  const TOTAL_SECONDS = 30;
  const CIRCUMFERENCE = 157;
  let timerInterval = null;
  let remainingSeconds = TOTAL_SECONDS;
  let currentQuestionId = null;
  let isSubmitting = false;

  function getCsrfToken() {
    const name = "csrftoken=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(";");
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i].trim();
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

  function startTimer() {
    clearInterval(timerInterval);
    remainingSeconds = TOTAL_SECONDS;
    updateTimerVisuals(remainingSeconds);

    timerInterval = setInterval(() => {
      remainingSeconds--;
      updateTimerVisuals(remainingSeconds);

      if (remainingSeconds <= 0) {
        clearInterval(timerInterval);
        handleTimeout();
      }
    }, 1000);
  }

  function updateTimerVisuals(sec) {
    if (timerTextEl) timerTextEl.textContent = sec;
    if (timerCircleEl) {
      const offset = CIRCUMFERENCE - (sec / TOTAL_SECONDS) * CIRCUMFERENCE;
      timerCircleEl.style.strokeDashoffset = offset;
      if (sec <= 5) {
        timerCircleEl.classList.add("warning");
      } else {
        timerCircleEl.classList.remove("warning");
      }
    }
  }

  function stopTimer() {
    clearInterval(timerInterval);
  }

  async function loadQuestion() {
    isSubmitting = false;
    try {
      const res = await fetch(questionApiUrl);
      const data = await res.json();

      if (data.is_finished) {
        window.location.reload();
        return;
      }

      currentQuestionId = data.question_id;

      questionTextEl.textContent = data.text;
      progressTextEl.textContent = `${data.current_index} / ${data.total_questions}`;
      const percent = (data.current_index / data.total_questions) * 100;
      progressBarEl.style.width = `${percent}%`;

      difficultyPillEl.className = `pill pill-${data.difficulty}`;
      difficultyPillEl.innerHTML = `<span class="pill-dot"></span><span>${data.difficulty_display}</span>`;

      pointsBadgeEl.textContent = `+${data.points} ball`;

      if (codeSnippetBoxEl) {
        if (data.code_snippet) {
          codeSnippetBoxEl.style.display = "block";
          let escaped = data.code_snippet
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
          if (data.question_type === "code_fill") {
            escaped = escaped.replace(/____/g, '<span class="code-blank" id="codeBlank" style="background: rgba(108, 92, 231, 0.4); border-bottom: 2px solid var(--accent); padding: 0.1rem 0.5rem; border-radius: 4px; color: #ffd166; font-weight: bold;">____</span>');
          }
          codeSnippetBoxEl.innerHTML = `
            <div style="background: #0d1117; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; overflow: hidden;">
              <div style="background: #161b22; padding: 0.4rem 0.75rem; display: flex; align-items: center; gap: 0.4rem; border-bottom: 1px solid rgba(255,255,255,0.06);">
                <span style="width: 10px; height: 10px; border-radius: 50%; background: #ff5f56; display: inline-block;"></span>
                <span style="width: 10px; height: 10px; border-radius: 50%; background: #ffbd2e; display: inline-block;"></span>
                <span style="width: 10px; height: 10px; border-radius: 50%; background: #27c93f; display: inline-block;"></span>
                <span style="margin-left: 0.5rem; font-size: 0.75rem; color: #8b949e; font-family: monospace;">python / django</span>
              </div>
              <pre style="margin: 0; padding: 1rem 1.25rem; font-family: 'Fira Code', 'Courier New', monospace; font-size: 0.95rem; line-height: 1.6; color: #c9d1d9; overflow-x: auto;"><code>${escaped}</code></pre>
            </div>
          `;
        } else {
          codeSnippetBoxEl.style.display = "none";
          codeSnippetBoxEl.innerHTML = "";
        }
      }

      choicesContainerEl.innerHTML = "";
      data.choices.forEach((choice) => {
        const item = document.createElement("div");
        item.className = "choice-item";
        item.dataset.choiceId = choice.id;
        item.tabIndex = 0;

        item.innerHTML = `
          <div class="choice-badge">${choice.badge}</div>
          <span class="choice-text">${choice.text}</span>
        `;

        item.addEventListener("mouseenter", () => {
          const blank = document.getElementById("codeBlank");
          if (blank && !isSubmitting) blank.textContent = choice.text;
        });

        item.addEventListener("click", () => handleAnswer(choice.id, item));
        item.addEventListener("keydown", (e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            handleAnswer(choice.id, item);
          }
        });

        choicesContainerEl.appendChild(item);
      });

      choicesContainerEl.addEventListener("mouseleave", () => {
        const blank = document.getElementById("codeBlank");
        if (blank && !isSubmitting) blank.textContent = "____";
      });

      startTimer();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleAnswer(choiceId, selectedEl) {
    if (isSubmitting) return;
    isSubmitting = true;
    stopTimer();

    const allChoices = choicesContainerEl.querySelectorAll(".choice-item");
    allChoices.forEach((el) => el.classList.add("disabled"));

    try {
      const csrfToken = getCsrfToken();
      const res = await fetch(answerApiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          question_id: currentQuestionId,
          choice_id: choiceId,
        }),
      });

      const data = await res.json();

      if (data.is_correct) {
        if (selectedEl) selectedEl.classList.add("correct");
      } else {
        if (selectedEl) selectedEl.classList.add("wrong");
        const correctEl = choicesContainerEl.querySelector(`[data-choice-id="${data.correct_choice_id}"]`);
        if (correctEl) correctEl.classList.add("correct");
      }

      setTimeout(() => {
        if (data.is_finished && data.next_url) {
          window.location.href = data.next_url;
        } else {
          loadQuestion();
        }
      }, 1200);
    } catch (err) {
      console.error(err);
      isSubmitting = false;
    }
  }

  function handleTimeout() {
    if (isSubmitting) return;
    handleAnswer(null, null);
  }

  loadQuestion();
});
