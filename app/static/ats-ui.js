// ATS optimization audit presentation.

function fillKeywordsOrEmpty(
    id,
    values,
    emptyMessage = "No keywords identified."
) {

    const container = el(id);

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!values || !values.length) {

        const empty = document.createElement("span");

        empty.className = "keyword-empty";

        empty.textContent = emptyMessage;

        container.appendChild(empty);

        return;
    }

    values.forEach(value => {

        const badge = document.createElement("span");

        badge.className = "keyword";

        badge.textContent = value;

        container.appendChild(badge);
    });
}


function displayATSOptimizationAudit(
    audit
) {

    if (!audit) {
        return;
    }


    // --------------------------------------------
    // Deterministic Python ATS audit
    // --------------------------------------------

    if (el("deterministicATS")) {

        el("deterministicATS").textContent =
            (
                audit.deterministic_ats_score ?? 0
            ) + "%";
    }


    if (el("atsStructureStatus")) {

        const structureStatus =
            el("atsStructureStatus");


        if (audit.structure_passed) {

            structureStatus.textContent =
                "ATS-SAFE";

            structureStatus.className =
                "ats-structure-pass";

        } else {

            structureStatus.textContent =
                "REVIEW REQUIRED";

            structureStatus.className =
                "ats-structure-fail";
        }
    }


    fillKeywordsOrEmpty(
        "authorizedKeywords",
        audit.authorized_keywords || [],
        "No authorized ATS terms identified."
    );


    fillKeywordsOrEmpty(
        "actualKeywordsFound",
        audit.keywords_found || [],
        "No authorized keywords detected."
    );


    fillKeywordsOrEmpty(
        "actualKeywordsMissing",
        audit.keywords_missing || [],
        "All authorized keywords were found."
    );


    const issueContainer =
        el("atsStructureIssuesContainer");


    const issueList =
        el("atsStructureIssues");


    if (
        issueContainer &&
        issueList
    ) {

        const issues =
            audit.structure_issues || [];


        issueList.innerHTML = "";


        if (issues.length) {

            issues.forEach(
                issue => {

                    const li =
                        document.createElement(
                            "li"
                        );

                    li.textContent =
                        issue;

                    issueList.appendChild(
                        li
                    );
                }
            );


            issueContainer.classList.remove(
                "hidden"
            );

        } else {

            issueContainer.classList.add(
                "hidden"
            );
        }
    }

    fillKeywordsOrEmpty(
        "headlineKeywords",
        audit.headline_keywords,
        "No headline keywords used."
    );

    fillKeywordsOrEmpty(
        "profileKeywords",
        audit.profile_keywords,
        "No profile keywords used."
    );

    fillKeywordsOrEmpty(
        "skillGroupKeywords",
        audit.skill_group_keywords,
        "No skill-group keywords used."
    );

    fillKeywordsOrEmpty(
        "accomplishmentKeywords",
        audit.accomplishment_keywords,
        "No accomplishment keywords used."
    );

    fillKeywordsOrEmpty(
        "excludedKeywords",
        audit.excluded_unsupported_keywords,
        "No unsupported keywords were excluded."
    );

    renderKeywordPlacementDetails(
        audit.keyword_placements || []
    );
}


function renderKeywordPlacementDetails(
    placements
) {

    const container = el(
        "keywordPlacementDetails"
    );

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!placements.length) {

        container.innerHTML = `
            <p class="help-text">
                No detailed keyword placement information
                was returned.
            </p>
        `;

        return;
    }

    placements.forEach(item => {

        const row = document.createElement("div");

        row.className = (
            "keyword-placement-row " +
            (
                item.included
                ? "keyword-included"
                : "keyword-excluded"
            )
        );

        const placementText =
            item.placement && item.placement.length
            ? item.placement.join(", ")
            : "Not included";

        row.innerHTML = `
            <div class="keyword-placement-top">
                <strong>
                    ${escapeHtml(item.keyword)}
                </strong>

                <span class="keyword-placement-status">
                    ${
                        item.included
                        ? "INCLUDED"
                        : "EXCLUDED"
                    }
                </span>
            </div>

            <div class="keyword-placement-meta">
                Importance:
                ${escapeHtml(item.importance || "N/A")}
                &nbsp; | &nbsp;
                Evidence:
                ${escapeHtml(item.evidence_status || "N/A")}
                &nbsp; | &nbsp;
                Placement:
                ${escapeHtml(placementText)}
            </div>

            <div class="keyword-placement-rationale">
                ${escapeHtml(item.rationale || "")}
            </div>
        `;

        container.appendChild(row);
    });
}
