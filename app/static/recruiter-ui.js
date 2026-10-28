// Recruiter / hiring-manager simulation workflow.

async function runRecruiterReview() {

    if (
        !storedJobText ||
        !generatedApplication
    ) {

        alert(
            "Generate the application before running the recruiter review."
        );

        return;
    }


    const intro =
        el("recruiterReviewIntro");

    const loading =
        el("recruiterReviewLoading");

    const results =
        el("recruiterReviewResults");


    if (intro) {
        intro.classList.add(
            "hidden"
        );
    }


    if (results) {
        results.classList.add(
            "hidden"
        );
    }


    if (loading) {
        loading.classList.remove(
            "hidden"
        );
    }


    const data =
        new FormData();


    data.append(
        "job_text",
        storedJobText
    );


    data.append(
        "application_json",
        JSON.stringify(
            generatedApplication
        )
    );


    try {

        const response =
            await fetch(
                "/api/recruiter-review",
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
                    "Recruiter review failed."
                )
            );
        }


        recruiterReview =
            result;


        displayRecruiterReview();


    }

    catch (error) {

        alert(
            error.message
        );


        if (loading) {
            loading.classList.add(
                "hidden"
            );
        }


        if (recruiterReview) {

            if (results) {
                results.classList.remove(
                    "hidden"
                );
            }

        } else {

            if (intro) {
                intro.classList.remove(
                    "hidden"
                );
            }
        }
    }
}


function displayRecruiterReview() {

    const review =
        recruiterReview;


    if (!review) {
        return;
    }


    const loading =
        el("recruiterReviewLoading");

    const intro =
        el("recruiterReviewIntro");

    const results =
        el("recruiterReviewResults");


    if (loading) {
        loading.classList.add(
            "hidden"
        );
    }


    if (intro) {
        intro.classList.add(
            "hidden"
        );
    }


    el("recruiterRecommendation").textContent =
        formatRecruiterRecommendation(
            review.interview_recommendation
        );


    el("recruiterFirstImpression").textContent =
        review.first_impression || "";


    fillRecruiterList(
        "recruiterStrongestSignals",
        review.strongest_signals,
        "No immediate strengths were identified."
    );


    renderRecruiterConcerns(
        review.concerns || []
    );


    fillRecruiterList(
        "recruiterUnclearPoints",
        review.unclear_points,
        "No major clarity issues were identified."
    );


    fillRecruiterList(
        "recruiterMissingSignals",
        review.missing_signals,
        "No important missing signals were identified."
    );


    fillRecruiterList(
        "recruiterBuzzwordRisks",
        review.buzzword_risks,
        "No material buzzword or over-positioning risks were identified."
    );


    renderRecruiterInterviewQuestions(
        review.likely_interview_questions || []
    );


    el("recruiterBottomLine").textContent =
        review.bottom_line || "";


    if (results) {
        results.classList.remove(
            "hidden"
        );
    }
}


function formatRecruiterRecommendation(
    value
) {

    const normalized =
        (
            value ||
            ""
        )
        .trim()
        .toUpperCase();


    const labels = {
        STRONG_YES: "STRONG YES",
        YES: "YES",
        MAYBE: "MAYBE",
        NO: "NO"
    };


    return (
        labels[normalized] ||
        normalized ||
        "NOT AVAILABLE"
    );
}


function fillRecruiterList(
    id,
    values,
    emptyMessage
) {

    const list =
        el(id);


    if (!list) {
        return;
    }


    list.innerHTML = "";


    if (
        !values ||
        !values.length
    ) {

        const item =
            document.createElement(
                "li"
            );


        item.textContent =
            emptyMessage;


        list.appendChild(
            item
        );

        return;
    }


    values.forEach(
        value => {

            const item =
                document.createElement(
                    "li"
                );


            item.textContent =
                value;


            list.appendChild(
                item
            );
        }
    );
}


function renderRecruiterConcerns(
    concerns
) {

    const container =
        el("recruiterConcerns");


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (!concerns.length) {

        const clean =
            document.createElement(
                "div"
            );


        clean.className =
            "integrity-clean";


        clean.textContent =
            "No material recruiter concerns were identified.";


        container.appendChild(
            clean
        );

        return;
    }


    concerns.forEach(
        concern => {

            const card =
                document.createElement(
                    "div"
                );


            const severity =
                (
                    concern.severity ||
                    "CLARIFICATION"
                )
                .toLowerCase()
                .replace(
                    /[^a-z]+/g,
                    "-"
                );


            card.className =
                "integrity-issue severity-" +
                severity;


            card.innerHTML = `

                <div class="integrity-issue-header">

                    <strong>
                        ${escapeHtml(
                            concern.category ||
                            "Recruiter Concern"
                        )}
                    </strong>

                    <span class="severity-badge">
                        ${escapeHtml(
                            concern.severity ||
                            "CLARIFICATION"
                        )}
                    </span>

                </div>


                <p>
                    ${escapeHtml(
                        concern.observation ||
                        ""
                    )}
                </p>


                <div>

                    <span class="requirement-label">
                        Why it matters
                    </span>

                    <p>
                        ${escapeHtml(
                            concern.why_it_matters ||
                            ""
                        )}
                    </p>

                </div>


                ${
                    concern.evidence
                    ? `
                        <div>

                            <span class="requirement-label">
                                What triggered this impression
                            </span>

                            <p>
                                ${escapeHtml(
                                    concern.evidence
                                )}
                            </p>

                        </div>
                    `
                    : ""
                }


                ${
                    concern.suggested_fix
                    ? `
                        <div class="integrity-correction">

                            <span class="requirement-label">
                                What to improve
                            </span>

                            <p>
                                ${escapeHtml(
                                    concern.suggested_fix
                                )}
                            </p>

                        </div>
                    `
                    : ""
                }
            `;


            container.appendChild(
                card
            );
        }
    );
}


function renderRecruiterInterviewQuestions(
    questions
) {

    const container =
        el("recruiterInterviewQuestions");


    if (!container) {
        return;
    }


    container.innerHTML = "";


    if (!questions.length) {

        const empty =
            document.createElement(
                "div"
            );


        empty.className =
            "integrity-clean";


        empty.textContent =
            "No application-specific interview questions were identified.";


        container.appendChild(
            empty
        );

        return;
    }


    questions.forEach(
        (item, index) => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "requirement-card";


            card.innerHTML = `

                <div class="requirement-card-header">

                    <strong>
                        ${index + 1}.
                        ${escapeHtml(
                            item.question ||
                            ""
                        )}
                    </strong>

                </div>


                <div class="requirement-detail">

                    <span class="requirement-label">
                        Why they may ask
                    </span>

                    <p>
                        ${escapeHtml(
                            item.why_asked ||
                            ""
                        )}
                    </p>

                </div>


                ${
                    item.evidence_to_prepare
                    ? `
                        <div class="requirement-detail">

                            <span class="requirement-label">
                                Evidence to prepare
                            </span>

                            <p>
                                ${escapeHtml(
                                    item.evidence_to_prepare
                                )}
                            </p>

                        </div>
                    `
                    : ""
                }
            `;


            container.appendChild(
                card
            );
        }
    );
}
