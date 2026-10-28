// Evidence-constrained interview preparation workflow.

async function runInterviewPreparation() {
    if (
        !storedJobText ||
        !storedResumeText ||
        !generatedApplication ||
        !storedGapVerification
    ) {
        alert(
            "Complete application generation and gap verification before building interview preparation."
        );
        return;
    }

    const intro =
        el("interviewPreparationIntro");
    const loading =
        el("interviewPreparationLoading");
    const results =
        el("interviewPreparationResults");

    intro?.classList.add("hidden");
    results?.classList.add("hidden");
    loading?.classList.remove("hidden");

    const data =
        new FormData();

    data.append(
        "job_text",
        storedJobText
    );

    data.append(
        "resume_text",
        storedResumeText
    );

    data.append(
        "application_json",
        JSON.stringify(
            generatedApplication
        )
    );

    data.append(
        "verification_json",
        JSON.stringify(
            storedGapVerification
        )
    );

    data.append(
        "achievement_verification_json",
        JSON.stringify(
            achievementVerification || {}
        )
    );

    if (recruiterReview) {
        data.append(
            "recruiter_review_json",
            JSON.stringify(
                recruiterReview
            )
        );
    }

    try {
        const response =
            await fetch(
                "/api/interview-preparation",
                {
                    method: "POST",
                    body: data
                }
            );

        const result =
            await response.json();

        if (!response.ok) {
            throw new Error(
                formatApiError(
                    result,
                    "Interview preparation failed."
                )
            );
        }

        interviewPreparation =
            result;

        displayInterviewPreparation();
    }
    catch (error) {
        alert(
            error.message
        );

        loading?.classList.add("hidden");

        if (interviewPreparation) {
            results?.classList.remove(
                "hidden"
            );
        } else {
            intro?.classList.remove(
                "hidden"
            );
        }
    }
}


function displayInterviewPreparation() {
    const preparation =
        interviewPreparation;

    if (!preparation) {
        return;
    }

    el("interviewPreparationIntro")
        ?.classList.add("hidden");

    el("interviewPreparationLoading")
        ?.classList.add("hidden");

    el(
        "interviewPreparationSummary"
    ).textContent =
        preparation.preparation_summary || "";

    renderLikelyInterviewQuestions(
        preparation.likely_questions || []
    );

    renderSTARStories(
        preparation.star_stories || []
    );

    renderGapInterviewPreparation(
        preparation.gap_preparation || []
    );

    renderEmployerQuestions(
        preparation.questions_for_employer || []
    );

    fillInterviewList(
        "interviewFinalAdvice",
        preparation.final_advice,
        "No additional preparation advice."
    );

    el("interviewPreparationResults")
        ?.classList.remove("hidden");
}


function fillInterviewList(
    id,
    values,
    emptyMessage
) {
    const container =
        el(id);

    if (!container) {
        return;
    }

    container.innerHTML = "";

    const items =
        values && values.length
            ? values
            : [emptyMessage];

    items.forEach(value => {
        const item =
            document.createElement("li");

        item.textContent =
            value;

        container.appendChild(
            item
        );
    });
}


function interviewCard() {
    const card =
        document.createElement("div");

    card.className =
        "requirement-card";

    return card;
}


function renderLikelyInterviewQuestions(
    questions
) {
    const container =
        el("interviewLikelyQuestions");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!questions.length) {
        container.textContent =
            "No specific interview questions were generated.";
        return;
    }

    questions.forEach(
        (item, index) => {
            const card =
                interviewCard();

            card.innerHTML = `
<div class="requirement-card-header">
    <strong>
        ${index + 1}.
        ${escapeHtml(item.question)}
    </strong>
    <span class="importance-badge">
        ${escapeHtml(
            item.likelihood || "MEDIUM"
        )}
    </span>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Category
    </span>
    <p>
        ${escapeHtml(item.category || "")}
    </p>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Why this is likely
    </span>
    <p>
        ${escapeHtml(item.why_likely || "")}
    </p>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        What they are testing
    </span>
    <p>
        ${escapeHtml(
            item.interviewer_is_testing || ""
        )}
    </p>
</div>
`;

            container.appendChild(
                card
            );
        }
    );
}


function renderSTARStories(
    stories
) {
    const container =
        el("interviewSTARStories");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!stories.length) {
        container.textContent =
            "No evidence-supported STAR stories were generated.";
        return;
    }

    stories.forEach(story => {
        const card =
            interviewCard();

        const usefulFor =
            (
                story.useful_for_questions || []
            )
            .map(
                value =>
                    `<li>${escapeHtml(value)}</li>`
            )
            .join("");

        const missingDetails =
            (
                story.missing_details || []
            )
            .map(
                value =>
                    `<li>${escapeHtml(value)}</li>`
            )
            .join("");

        card.innerHTML = `
<div class="requirement-card-header">
    <strong>
        ${escapeHtml(story.title)}
    </strong>
    <span class="status-badge">
        ${escapeHtml(
            story.evidence_strength || ""
        )}
    </span>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Situation
    </span>
    <p>${escapeHtml(story.situation || "")}</p>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Task
    </span>
    <p>${escapeHtml(story.task || "")}</p>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Action
    </span>
    <p>${escapeHtml(story.action || "")}</p>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Result
    </span>
    <p>${escapeHtml(story.result || "")}</p>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Source evidence
    </span>
    <p>
        ${escapeHtml(
            story.source_evidence || ""
        )}
    </p>
</div>

${
    usefulFor
        ? `
<div class="requirement-detail">
    <span class="requirement-label">
        Useful for questions about
    </span>
    <ul>${usefulFor}</ul>
</div>
`
        : ""
}

${
    missingDetails
        ? `
<div class="verification-caution">
    <strong>
        Details to prepare before using this story
    </strong>
    <ul>${missingDetails}</ul>
</div>
`
        : ""
}
`;

        container.appendChild(
            card
        );
    });
}


function renderGapInterviewPreparation(
    gaps
) {
    const container =
        el("interviewGapPreparation");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!gaps.length) {
        container.textContent =
            "No material weak-area preparation was required.";
        return;
    }

    gaps.forEach(item => {
        const card =
            interviewCard();

        const transferable =
            (
                item.transferable_evidence || []
            )
            .map(
                value =>
                    `<li>${escapeHtml(value)}</li>`
            )
            .join("");

        const prohibited =
            (
                item.do_not_claim || []
            )
            .map(
                value =>
                    `<li>${escapeHtml(value)}</li>`
            )
            .join("");

        card.innerHTML = `
<div class="requirement-card-header">
    <strong>
        ${escapeHtml(item.requirement)}
    </strong>
    <span class="status-badge">
        ${escapeHtml(item.gap_type || "GAP")}
    </span>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Likely question
    </span>
    <p>
        ${escapeHtml(item.likely_question || "")}
    </p>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Truthful answer strategy
    </span>
    <p>
        ${escapeHtml(
            item.truthful_answer_strategy || ""
        )}
    </p>
</div>

${
    transferable
        ? `
<div class="requirement-detail">
    <span class="requirement-label">
        Transferable evidence
    </span>
    <ul>${transferable}</ul>
</div>
`
        : ""
}

<div class="requirement-detail">
    <span class="requirement-label">
        Bridge to strength
    </span>
    <p>
        ${escapeHtml(
            item.bridge_to_strength || ""
        )}
    </p>
</div>

${
    prohibited
        ? `
<div class="verification-caution">
    <strong>
        Do not claim
    </strong>
    <ul>${prohibited}</ul>
</div>
`
        : ""
}
`;

        container.appendChild(
            card
        );
    });
}


function renderEmployerQuestions(
    questions
) {
    const container =
        el("interviewEmployerQuestions");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!questions.length) {
        container.textContent =
            "No employer questions were generated.";
        return;
    }

    questions.forEach(
        (item, index) => {
            const card =
                interviewCard();

            card.innerHTML = `
<div class="requirement-card-header">
    <strong>
        ${index + 1}.
        ${escapeHtml(item.question)}
    </strong>
    <span class="importance-badge">
        ${escapeHtml(item.audience || "ANY")}
    </span>
</div>

<div class="requirement-detail">
    <span class="requirement-label">
        Why ask
    </span>
    <p>
        ${escapeHtml(item.why_ask || "")}
    </p>
</div>
`;

            container.appendChild(
                card
            );
        }
    );
}
