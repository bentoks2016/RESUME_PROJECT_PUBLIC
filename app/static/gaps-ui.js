// Experience-gap collection and verification workflow.

function buildGapQuestions(
    gaps
) {

    const container =
        el("gapQuestions");

    container.innerHTML = "";


    if (!gaps || !gaps.length) {

        container.innerHTML = `
            <div class="gap-item">
                <strong>
                    No major experience gaps require
                    verification.
                </strong>
                <p>
                    You can proceed to generate the
                    optimized application.
                </p>
            </div>
        `;

        return;
    }


    gaps.forEach(
        (gap, index) => {

            const wrapper =
                document.createElement(
                    "div"
                );

            wrapper.className =
                "gap-item";

            wrapper.dataset.gapId =
                gap.id;


            const examples =
                (gap.suggested_examples || [])
                    .map(
                        item =>
                            `<li>${escapeHtml(item)}</li>`
                    )
                    .join("");


            wrapper.innerHTML = `

                <div class="gap-question-number">
                    GAP ${index + 1}
                </div>

                <h3>
                    ${escapeHtml(gap.requirement)}
                </h3>

                <p class="gap-reason">
                    ${escapeHtml(gap.reason)}
                </p>


                ${
                    examples
                    ? `
                        <div class="examples">

                            <strong>
                                Experience that may be relevant:
                            </strong>

                            <ul>
                                ${examples}
                            </ul>

                        </div>
                    `
                    : ""
                }


                <div class="gap-decision">

                    <div class="gap-decision-title">
                        Do you have this experience?
                    </div>

                    <label>

                        <input
                            type="radio"
                            name="gap_${escapeHtml(gap.id)}"
                            value="no"
                            checked
                            data-gap-choice="${escapeHtml(gap.id)}"
                        >

                        No

                    </label>


                    <label>

                        <input
                            type="radio"
                            name="gap_${escapeHtml(gap.id)}"
                            value="yes"
                            data-gap-choice="${escapeHtml(gap.id)}"
                        >

                        Yes

                    </label>

                </div>


                <div
                    id="gap_details_${escapeHtml(gap.id)}"
                    class="gap-evidence-fields hidden"
                >

                    <label class="gap-field">

                        <span>
                            What did you personally do?
                        </span>

                        <textarea
                            data-field="description"
                            data-gap-id="${escapeHtml(gap.id)}"
                            placeholder="Describe your responsibilities, work, project, or accomplishment..."
                        ></textarea>

                    </label>


                    <label class="gap-field">

                        <span>
                            Where or in what context?
                        </span>

                        <input
                            type="text"
                            data-field="context"
                            data-gap-id="${escapeHtml(gap.id)}"
                            placeholder="Employer, project, business, course, research, etc."
                        >

                    </label>


                    <label class="gap-field">

                        <span>
                            Result or business impact
                            (if available)
                        </span>

                        <input
                            type="text"
                            data-field="results"
                            data-gap-id="${escapeHtml(gap.id)}"
                            placeholder="Outcome, improvement, users, revenue, time saved, etc."
                        >

                    </label>


                    <label class="gap-field">

                        <span>
                            Relevant tools or technologies
                            (if applicable)
                        </span>

                        <input
                            type="text"
                            data-field="technologies"
                            data-gap-id="${escapeHtml(gap.id)}"
                            placeholder="Platforms, software, programming languages, methodologies..."
                        >

                    </label>

                </div>
            `;


            container.appendChild(
                wrapper
            );
        }
    );
}


function toggleGapDetails(
    gapId
) {

    const selected =
        document.querySelector(
            `input[name="gap_${CSS.escape(gapId)}"]:checked`
        );

    const details =
        document.getElementById(
            `gap_details_${gapId}`
        );


    if (!selected || !details) {
        return;
    }


    if (selected.value === "yes") {

        details.classList.remove(
            "hidden"
        );

    } else {

        details.classList.add(
            "hidden"
        );
    }
}


function collectGapAnswers() {

    const gaps =
        storedAnalysis.gap_questions || [];


    return gaps.map(
        gap => {

            const selected =
                document.querySelector(
                    `input[name="gap_${CSS.escape(gap.id)}"]:checked`
                );


            const hasExperience =
                selected
                ? selected.value === "yes"
                : false;


            function fieldValue(
                field
            ) {

                const input =
                    document.querySelector(
                        `[data-gap-id="${CSS.escape(gap.id)}"][data-field="${field}"]`
                    );

                return input
                    ? input.value.trim()
                    : "";
            }


            return {

                gap_id:
                    gap.id,

                requirement:
                    gap.requirement,

                has_experience:
                    hasExperience,

                description:
                    hasExperience
                    ? fieldValue("description")
                    : "",

                context:
                    hasExperience
                    ? fieldValue("context")
                    : "",

                results:
                    hasExperience
                    ? fieldValue("results")
                    : "",

                technologies:
                    hasExperience
                    ? fieldValue("technologies")
                    : ""
            };
        }
    );
}


async function verifyGapAnswers() {

    const answers =
        collectGapAnswers();


    for (const answer of answers) {

        if (
            answer.has_experience &&
            answer.description.length < 20
        ) {

            alert(
                "For each gap marked Yes, please provide a meaningful description of what you actually did."
            );

            return;
        }
    }


    storedGapAnswers =
        answers;


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
        "analysis_json",
        JSON.stringify(
            storedAnalysis
        )
    );


    data.append(
        "gap_answers_json",
        JSON.stringify(
            answers
        )
    );


    setLoading(
        "Verifying your additional experience...",
        "Checking whether the information you provided supports the missing job requirements."
    );


    try {

        const response =
            await fetch(
                "/api/verify-gaps",
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
                    "Experience verification failed."
                )
            );
        }


        storedGapVerification =
            result;


        displayGapVerification();


    }

    catch (error) {

        alert(
            error.message
        );

        showOnly(
            "analysisScreen"
        );
    }
}


function displayGapVerification() {

    const verification =
        storedGapVerification;


    el("verificationSummary").textContent =
        verification.summary;


    el("verifiedExperienceCount").textContent =
        verification.verified_experience_count;


    el("remainingGapCount").textContent =
        verification.remaining_gap_count;


    const container =
        el("verificationItems");


    container.innerHTML = "";


    verification.items.forEach(
        item => {

            const card =
                document.createElement(
                    "div"
                );


            const resultClass =
                verificationResultClass(
                    item.verification_result
                );


            const keywords =
                (item.supported_keywords || [])
                    .map(
                        keyword =>
                            `<span class="requirement-keyword">
                                ${escapeHtml(keyword)}
                            </span>`
                    )
                    .join("");


            card.className =
                "verification-item " +
                resultClass;


            card.innerHTML = `

                <div class="verification-item-header">

                    <strong>
                        ${escapeHtml(item.requirement)}
                    </strong>

                    <span class="verification-badge ${resultClass}">
                        ${escapeHtml(item.verification_result)}
                    </span>

                </div>


                <div class="verification-evidence">

                    <span class="requirement-label">
                        Evidence Assessment
                    </span>

                    <p>
                        ${escapeHtml(item.evidence_summary)}
                    </p>

                </div>


                ${
                    keywords
                    ? `
                        <div>
                            <span class="requirement-label">
                                Newly Supported ATS Terms
                            </span>

                            <div>
                                ${keywords}
                            </div>
                        </div>
                    `
                    : ""
                }


                ${
                    item.caution
                    ? `
                        <div class="verification-caution">
                            ${escapeHtml(item.caution)}
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


    showOnly(
        "verificationScreen"
    );
}


function verificationResultClass(
    result
) {

    const normalized =
        (result || "").toUpperCase();


    if (normalized === "VERIFIED") {
        return "verification-verified";
    }


    if (normalized === "PARTIAL") {
        return "verification-partial";
    }


    if (normalized === "NEEDS_DETAIL") {
        return "verification-needs-detail";
    }


    return "verification-not-verified";
}
