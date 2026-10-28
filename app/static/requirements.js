// Requirement-analysis UI and filtering.

function normalizeRequirementValue(
    value
) {

    return (
        value || ""
    )
        .trim()
        .toUpperCase();
}


function displayRequirementAnalysis() {

    if (
        !storedAnalysis ||
        !storedAnalysis.requirements
    ) {
        return;
    }


    const requirements =
        storedAnalysis.requirements;


    const supported =
        requirements.filter(
            item =>
                normalizeRequirementValue(
                    item.status
                ) === "SUPPORTED"
        ).length;


    const transferable =
        requirements.filter(
            item =>
                normalizeRequirementValue(
                    item.status
                ) === "TRANSFERABLE"
        ).length;


    const missing =
        requirements.filter(
            item =>
                normalizeRequirementValue(
                    item.status
                ) === "MISSING"
        ).length;


    el("totalRequirements").textContent =
        requirements.length;


    el("supportedCount").textContent =
        supported;


    el("transferableCount").textContent =
        transferable;


    el("missingCount").textContent =
        missing;


    renderRequirements(
        requirements
    );
}


function renderRequirements(
    requirements
) {

    const container =
        el("requirementMatrix");


    if (!container) {
        return;
    }


    container.innerHTML = "";


    let filtered =
        requirements;


    if (
        activeRequirementFilter === "REQUIRED" ||
        activeRequirementFilter === "PREFERRED"
    ) {

        filtered =
            requirements.filter(
                item =>
                    normalizeRequirementValue(
                        item.importance
                    ) === activeRequirementFilter
            );

    }


    if (
        activeRequirementFilter === "MISSING"
    ) {

        filtered =
            requirements.filter(
                item =>
                    normalizeRequirementValue(
                        item.status
                    ) === "MISSING"
            );
    }


    if (!filtered.length) {

        const empty =
            document.createElement(
                "div"
            );


        empty.className =
            "requirement-empty";


        empty.textContent =
            "No requirements match this filter.";


        container.appendChild(
            empty
        );


        return;
    }


    filtered.forEach(
        (item, index) => {

            const status =
                normalizeRequirementValue(
                    item.status
                );


            const importance =
                normalizeRequirementValue(
                    item.importance
                );


            const card =
                document.createElement(
                    "div"
                );


            card.className =
                "requirement-card " +
                requirementStatusClass(
                    status
                );


            const keywords =
                (
                    item.keywords || []
                )
                .map(
                    keyword =>
                        `<span class="requirement-keyword">
                            ${escapeHtml(keyword)}
                        </span>`
                )
                .join("");


            card.innerHTML = `

                <div class="requirement-card-header">

                    <div class="requirement-title">

                        <span class="requirement-number">
                            ${index + 1}
                        </span>

                        <strong>
                            ${escapeHtml(item.requirement)}
                        </strong>

                    </div>


                    <div class="requirement-badges">

                        <span class="importance-badge">
                            ${escapeHtml(importance)}
                        </span>

                        <span class="
                            status-badge
                            ${requirementStatusClass(status)}
                        ">
                            ${escapeHtml(status)}
                        </span>

                    </div>

                </div>


                <div class="requirement-evidence">

                    <div class="requirement-label">
                        Evidence
                    </div>

                    <div class="requirement-value">
                        ${escapeHtml(
                            item.evidence ||
                            "No direct evidence found."
                        )}
                    </div>

                </div>


                ${
                    keywords
                    ? `
                        <div class="requirement-keywords">

                            <div class="requirement-label">
                                ATS Terms
                            </div>

                            <div>
                                ${keywords}
                            </div>

                        </div>
                    `
                    : ""
                }


                ${
                    item.impact
                    ? `
                        <div class="requirement-detail">

                            <span class="requirement-label">
                                Impact:
                            </span>

                            ${escapeHtml(item.impact)}

                        </div>
                    `
                    : ""
                }


                ${
                    item.recommendation
                    ? `
                        <div class="requirement-detail">

                            <span class="requirement-label">
                                Recommendation:
                            </span>

                            ${escapeHtml(item.recommendation)}

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


function requirementStatusClass(
    status
) {

    if (status === "SUPPORTED") {
        return "status-supported";
    }


    if (status === "TRANSFERABLE") {
        return "status-transferable";
    }


    return "status-missing";
}


function filterRequirements(
    filter
) {

    activeRequirementFilter =
        filter;


    document
        .querySelectorAll(
            ".requirement-filter"
        )
        .forEach(
            button => {

                if (
                    button.dataset.filter === filter
                ) {

                    button.classList.add(
                        "active"
                    );

                } else {

                    button.classList.remove(
                        "active"
                    );
                }

            }
        );


    if (
        storedAnalysis &&
        storedAnalysis.requirements
    ) {

        renderRequirements(
            storedAnalysis.requirements
        );
    }
}
