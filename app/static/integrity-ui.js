// Factual-integrity workflow and presentation.

async function runIntegrityCheck() {

    setLoading(
        "Checking factual integrity...",
        "Comparing every material claim against your original resume and verified experience."
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
        "gap_answers_json",
        JSON.stringify(
            storedGapAnswers
        )
    );


    data.append(
        "verification_json",
        JSON.stringify(
            storedGapVerification
        )
    );


    data.append(
        "application_json",
        JSON.stringify(
            generatedApplication
        )
    );


    data.append(
        "achievement_verification_json",
        JSON.stringify(
            achievementVerification || {}
        )
    );


    try {

        const response =
            await fetch(
                "/api/check-integrity",
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
                    "Integrity check failed."
                )
            );
        }


        storedIntegrityResult =
            result;


        displayIntegrityResults();


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


function displayIntegrityResults() {

    const result =
        storedIntegrityResult;


    el("integrityScore").textContent =
        result.integrity_score + "%";


    el("integritySummary").textContent =
        result.summary;


    el("supportedClaims").textContent =
        result.supported_claims;


    el("reframedClaims").textContent =
        result.reasonable_reframes;


    el("unsupportedClaims").textContent =
        result.unsupported_claims;


    el("contradictions").textContent =
        result.contradictions;


    const status =
        el("integrityStatus");


    const button =
        el("continueAfterIntegrity");


    if (result.passed) {

        status.textContent =
            "PASSED";

        status.className =
            "integrity-status integrity-pass";

        button.textContent =
            "Continue to Documents →";

    } else {

        status.textContent =
            "REVIEW REQUIRED";

        status.className =
            "integrity-status integrity-fail";

        button.textContent =
            "Continue With Warnings →";
    }


    const container =
        el("integrityIssues");


    container.innerHTML = "";


    const issues =
        result.claims.filter(
            claim =>
                claim.status === "UNSUPPORTED" ||
                claim.status === "CONTRADICTION"
        );


    if (!issues.length) {

        container.innerHTML = `
            <div class="integrity-clean">
                No material unsupported claims or
                contradictions were detected.
            </div>
        `;

    } else {

        issues.forEach(
            claim => {

                const card =
                    document.createElement(
                        "div"
                    );


                const severity =
                    (
                        claim.severity ||
                        "LOW"
                    ).toLowerCase();


                card.className =
                    "integrity-issue severity-" +
                    severity;


                card.innerHTML = `

                    <div class="integrity-issue-header">

                        <strong>
                            ${escapeHtml(claim.category)}
                        </strong>

                        <span class="severity-badge">
                            ${escapeHtml(claim.severity)}
                        </span>

                    </div>


                    <div class="integrity-claim">

                        <span class="requirement-label">
                            Generated Claim
                        </span>

                        <p>
                            ${escapeHtml(claim.claim)}
                        </p>

                    </div>


                    <div>

                        <span class="requirement-label">
                            Evidence
                        </span>

                        <p>
                            ${escapeHtml(
                                claim.source_evidence ||
                                "No supporting evidence found."
                            )}
                        </p>

                    </div>


                    <div>

                        <span class="requirement-label">
                            Why Flagged
                        </span>

                        <p>
                            ${escapeHtml(claim.explanation)}
                        </p>

                    </div>


                    ${
                        claim.suggested_correction
                        ? `
                            <div class="integrity-correction">

                                <span class="requirement-label">
                                    Suggested Correction
                                </span>

                                <p>
                                    ${escapeHtml(
                                        claim.suggested_correction
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


    showOnly(
        "integrityScreen"
    );
}


function continueToFinalResults() {

    displayFinalResults();
}
