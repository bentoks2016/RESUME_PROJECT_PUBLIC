// Achievement and quantification optimization workflow.

async function startAchievementOptimizer() {

    setLoading(
        "Finding achievement opportunities...",
        "Looking for important resume statements that could be strengthened with factual scope, results, or metrics."
    );


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


    try {

        const response =
            await fetch(
                "/api/analyze-achievements",
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
                    "Achievement analysis failed."
                )
            );
        }


        achievementAnalysis =
            result;


        displayAchievementOpportunities();


    }

    catch (error) {

        alert(
            error.message
        );


        showOnly(
            "verificationScreen"
        );
    }
}


function displayAchievementOpportunities() {

    const analysis =
        achievementAnalysis;


    el("achievementSummary").textContent =
        analysis.summary;


    const container =
        el("achievementOpportunities");


    container.innerHTML = "";


    const opportunities =
        analysis.opportunities || [];


    if (!opportunities.length) {

        container.innerHTML = `
            <div class="integrity-clean">
                Your resume already contains sufficiently
                detailed accomplishment statements for
                this stage.
            </div>
        `;

        showOnly(
            "achievementScreen"
        );

        return;
    }


    opportunities.forEach(
        (item, index) => {

            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "achievement-item";


            const questions =
                (
                    item.suggested_questions || []
                )
                .map(
                    question =>
                        `<li>${escapeHtml(question)}</li>`
                )
                .join("");


            card.innerHTML = `

                <div class="achievement-header">

                    <div>

                        <div class="gap-question-number">
                            OPPORTUNITY ${index + 1}
                        </div>

                        <strong>
                            ${escapeHtml(item.source_role || "Resume Achievement")}
                        </strong>

                    </div>


                    <span class="priority-badge priority-${escapeHtml(
                        (item.priority || "MEDIUM").toLowerCase()
                    )}">
                        ${escapeHtml(item.priority)}
                    </span>

                </div>


                <div class="achievement-source">

                    <span class="requirement-label">
                        Current Statement
                    </span>

                    <p>
                        "${escapeHtml(item.source_statement)}"
                    </p>

                </div>


                <div class="achievement-weakness">

                    <span class="requirement-label">
                        Opportunity
                    </span>

                    <p>
                        ${escapeHtml(item.weakness)}
                    </p>

                </div>


                ${
                    questions
                    ? `
                        <div class="examples">

                            <strong>
                                Think about:
                            </strong>

                            <ul>
                                ${questions}
                            </ul>

                        </div>
                    `
                    : ""
                }


                <div class="achievement-decision">

                    <label>

                        <input
                            type="radio"
                            name="achievement_${escapeHtml(item.id)}"
                            value="skip"
                            checked
                            data-achievement-choice="${escapeHtml(item.id)}"
                        >

                        I don't have more information

                    </label>


                    <label>

                        <input
                            type="radio"
                            name="achievement_${escapeHtml(item.id)}"
                            value="add"
                            data-achievement-choice="${escapeHtml(item.id)}"
                        >

                        Add details

                    </label>

                </div>


                <div
                    id="achievement_fields_${escapeHtml(item.id)}"
                    class="achievement-fields hidden"
                >

                    <label class="gap-field">

                        <span>
                            What action did you take?
                        </span>

                        <textarea
                            data-achievement-id="${escapeHtml(item.id)}"
                            data-achievement-field="action"
                            placeholder="What did you personally do?"
                        ></textarea>

                    </label>


                    <label class="gap-field">

                        <span>
                            Scope
                        </span>

                        <input
                            type="text"
                            data-achievement-id="${escapeHtml(item.id)}"
                            data-achievement-field="scope"
                            placeholder="Team size, clients, states, users, project size, data volume, etc."
                        >

                    </label>


                    <label class="gap-field">

                        <span>
                            Result or impact
                        </span>

                        <input
                            type="text"
                            data-achievement-id="${escapeHtml(item.id)}"
                            data-achievement-field="result"
                            placeholder="What changed or improved because of the work?"
                        >

                    </label>


                    <label class="gap-field">

                        <span>
                            Specific metrics
                        </span>

                        <input
                            type="text"
                            data-achievement-id="${escapeHtml(item.id)}"
                            data-achievement-field="metrics"
                            placeholder="Revenue, %, time saved, number of clients, accuracy, etc. Leave blank if unknown."
                        >

                    </label>


                    <label class="gap-field">

                        <span>
                            Additional context
                        </span>

                        <input
                            type="text"
                            data-achievement-id="${escapeHtml(item.id)}"
                            data-achievement-field="context"
                            placeholder="Employer, project, customer problem, operating environment, etc."
                        >

                    </label>

                </div>
            `;


            container.appendChild(
                card
            );
        }
    );


    showOnly(
        "achievementScreen"
    );
}


function toggleAchievementFields(
    id
) {

    const selected =
        document.querySelector(
            `input[name="achievement_${CSS.escape(id)}"]:checked`
        );


    const fields =
        document.getElementById(
            `achievement_fields_${id}`
        );


    if (!selected || !fields) {
        return;
    }


    if (selected.value === "add") {

        fields.classList.remove(
            "hidden"
        );

    } else {

        fields.classList.add(
            "hidden"
        );
    }
}


function achievementFieldValue(
    id,
    field
) {

    const element =
        document.querySelector(
            `[data-achievement-id="${CSS.escape(id)}"][data-achievement-field="${field}"]`
        );


    return element
        ? element.value.trim()
        : "";
}


function collectAchievementAnswers() {

    return (
        achievementAnalysis.opportunities || []
    ).map(
        item => {

            const selected =
                document.querySelector(
                    `input[name="achievement_${CSS.escape(item.id)}"]:checked`
                );


            const addDetails =
                selected &&
                selected.value === "add";


            return {

                opportunity_id:
                    item.id,

                source_statement:
                    item.source_statement,

                has_more_detail:
                    Boolean(addDetails),

                action:
                    addDetails
                    ? achievementFieldValue(
                        item.id,
                        "action"
                    )
                    : "",

                scope:
                    addDetails
                    ? achievementFieldValue(
                        item.id,
                        "scope"
                    )
                    : "",

                result:
                    addDetails
                    ? achievementFieldValue(
                        item.id,
                        "result"
                    )
                    : "",

                metrics:
                    addDetails
                    ? achievementFieldValue(
                        item.id,
                        "metrics"
                    )
                    : "",

                context:
                    addDetails
                    ? achievementFieldValue(
                        item.id,
                        "context"
                    )
                    : ""
            };
        }
    );
}


async function submitAchievementAnswers() {

    achievementAnswers =
        collectAchievementAnswers();


    const meaningful =
        achievementAnswers.filter(
            item =>
                item.has_more_detail
        );


    for (const item of meaningful) {

        const combined =
            (
                item.action +
                item.scope +
                item.result +
                item.metrics +
                item.context
            ).trim();


        if (combined.length < 20) {

            alert(
                "Please provide meaningful detail for each achievement you chose to enhance."
            );

            return;
        }
    }


    if (!meaningful.length) {

        achievementVerification = {
            achievements: [],
            accepted_count: 0,
            skipped_count:
                achievementAnswers.length,
            summary:
                "No additional achievement details were provided."
        };


        await generateVerifiedApplication();

        return;
    }


    setLoading(
        "Verifying your accomplishments...",
        "Turning your factual details into stronger achievement statements without inventing results."
    );


    const data =
        new FormData();


    data.append(
        "job_text",
        storedJobText
    );


    data.append(
        "achievement_answers_json",
        JSON.stringify(
            achievementAnswers
        )
    );


    try {

        const response =
            await fetch(
                "/api/verify-achievements",
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
                    "Achievement verification failed."
                )
            );
        }


        achievementVerification =
            result;


        await generateVerifiedApplication();


    }

    catch (error) {

        alert(
            error.message
        );


        showOnly(
            "achievementScreen"
        );
    }
}
