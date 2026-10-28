

function updateNavigation() {

    const navigation =
        document.getElementById(
            "appNavigation"
        );


    if (!navigation) {
        return;
    }


    if (currentScreen === "step1") {

        navigation.classList.add(
            "hidden"
        );

    } else {

        navigation.classList.remove(
            "hidden"
        );
    }
}


function goBack() {

    if (currentScreen === "step2") {

        showOnly(
            "step1"
        );

        return;
    }


    if (currentScreen === "analysisScreen") {

        showOnly(
            "step2"
        );

        return;
    }


    if (currentScreen === "verificationScreen") {

        showOnly(
            "analysisScreen"
        );

        return;
    }


    if (currentScreen === "achievementScreen") {

        showOnly(
            "verificationScreen"
        );

        return;
    }


    if (currentScreen === "integrityScreen") {

        showOnly(
            "verificationScreen"
        );

        return;
    }


    if (currentScreen === "results") {

        showOnly(
            "integrityScreen"
        );

        return;
    }


    if (currentScreen === "loading") {

        if (storedAnalysis) {

            showOnly(
                "analysisScreen"
            );

        } else {

            showOnly(
                "step2"
            );
        }
    }
}













function showOnly(id) {
    currentScreen = id;
    updateNavigation();

    [
        "step1",
        "step2",
        "loading",
        "analysisScreen",
        "verificationScreen",
        "achievementScreen",
        "integrityScreen",
        "results"
    ].forEach(section => {

        el(section).classList.add(
            "hidden"
        );

    });


    el(id).classList.remove(
        "hidden"
    );


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function showStep1() {

    showOnly(
        "step1"
    );
}


function showStep2() {

    const text =
        el("jobText").value.trim();

    const file =
        el("jobFile").files[0];


    if (!text && !file) {

        alert(
            "Paste or upload a job posting."
        );

        return;
    }


    showOnly(
        "step2"
    );
}


function setLoading(
    title,
    text
) {

    el("loadingTitle").textContent =
        title;

    el("loadingText").textContent =
        text;

    showOnly(
        "loading"
    );
}


async function analyzeApplication() {

    const resumeText =
        el("resumeText").value.trim();

    const resumeFile =
        el("resumeFile").files[0];


    if (!resumeText && !resumeFile) {

        alert(
            "Paste or upload your resume."
        );

        return;
    }


    const data =
        new FormData();


    data.append(
        "job_text",
        el("jobText").value
    );


    data.append(
        "resume_text",
        el("resumeText").value
    );


    const jobFile =
        el("jobFile").files[0];


    if (jobFile) {

        data.append(
            "job_file",
            jobFile
        );
    }


    if (resumeFile) {

        data.append(
            "resume_file",
            resumeFile
        );
    }


    setLoading(
        "Analyzing your resume...",
        "Comparing requirements, experience, and ATS terminology."
    );


    try {

        const response =
            await fetch(
                "/api/analyze",
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
                    "Analysis failed."
                )
            );
        }


        storedJobText =
            result.job_text;

        storedResumeText =
            result.resume_text;

        storedAnalysis =
            result.analysis;


        displayAnalysis();


    }

    catch (error) {

        alert(
            error.message
        );

        showOnly(
            "step2"
        );
    }
}


function displayAnalysis() {

    const a =
        storedAnalysis;


    el("roleTitle").textContent =
        a.job_title +
        (
            a.company
            ? " — " + a.company
            : ""
        );


    el("currentMatch").textContent =
        a.current_match_score + "%";


    el("potentialMatch").textContent =
        a.estimated_tailored_score + "%";


    el("currentATS").textContent =
        a.current_ats_score + "%";


    el("potentialATS").textContent =
        a.estimated_tailored_ats_score + "%";


    el("analysisSummary").textContent =
        a.executive_summary;


    fillList(
        "strengths",
        a.strengths
    );


    fillList(
        "gaps",
        a.gaps
    );


    const supportedKeywords =
        a.keyword_analysis.filter(
            k =>
                k.status === "SUPPORTED" ||
                k.status === "TRANSFERABLE"
        );


    fillKeywordObjects(
        "keywords",
        supportedKeywords
    );


    buildGapQuestions(
        a.gap_questions
    );


    displayRequirementAnalysis();


    showOnly(
        "analysisScreen"
    );
}


function fillList(
    id,
    values
) {

    const list =
        el(id);


    list.innerHTML = "";


    if (!values || !values.length) {

        const li =
            document.createElement("li");

        li.textContent =
            "None identified.";

        list.appendChild(li);

        return;
    }


    values.forEach(value => {

        const li =
            document.createElement("li");

        li.textContent =
            value;

        list.appendChild(li);

    });
}


function fillKeywordObjects(
    id,
    values
) {

    const container =
        el(id);

    container.innerHTML = "";


    values.forEach(item => {

        const span =
            document.createElement("span");

        span.className =
            "keyword";

        span.textContent =
            item.keyword;

        container.appendChild(
            span
        );

    });
}


function fillKeywords(
    id,
    values
) {

    const container =
        el(id);

    container.innerHTML = "";


    values.forEach(value => {

        const span =
            document.createElement("span");

        span.className =
            "keyword";

        span.textContent =
            value;

        container.appendChild(
            span
        );

    });
}




















async function generateVerifiedApplication() {

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
        "achievement_verification_json",
        JSON.stringify(
            achievementVerification || {}
        )
    );


    setLoading(
        "Building your optimized application...",
        "Using your verified experience and supported ATS terminology to create the final documents."
    );


    try {

        console.log("GENERATE REQUEST STATE", {
            job_text: storedJobText ? "present" : "MISSING",
            resume_text: storedResumeText ? "present" : "MISSING",
            analysis_json: storedAnalysis ? "present" : "MISSING",
            gap_answers_json: storedGapAnswers ? "present" : "MISSING",
            verification_json: storedGapVerification ? "present" : "MISSING",
            achievement_verification_json:
                achievementVerification ? "present" : "MISSING"
        });

        const response =
            await fetch(
                "/api/generate",
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
                    "Application generation failed."
                )
            );
        }


        generatedApplication =
            result;


        await runIntegrityCheck();


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


function displayFinalResults() {

    const app =
        generatedApplication;


    el("finalMatch").textContent =
        app.final_match_score + "%";


    el("finalATS").textContent =
        app.final_ats_score + "%";


    fillKeywords(
        "keywordsAdded",
        app.keywords_added || []
    );

    displayATSOptimizationAudit(
        app.ats_optimization
    );


    fillList(
        "remainingGaps",
        app.remaining_gaps || []
    );


    el("resumePreview").textContent =
        resumeToText(
            app.resume
        );


    el("coverLetterPreview").textContent =
        coverLetterToText(
            app.cover_letter
        );


    showOnly(
        "results"
    );
}


function resumeToText(
    resume
) {

    let output = "";


    output +=
        resume.name +
        "\n";


    const contact = [];


    if (resume.contact.phone) {
        contact.push(
            resume.contact.phone
        );
    }


    if (resume.contact.email) {
        contact.push(
            resume.contact.email
        );
    }


    if (resume.contact.linkedin) {
        contact.push(
            resume.contact.linkedin
        );
    }


    output +=
        contact.join(" | ") +
        "\n";


    if (resume.contact.location) {

        output +=
            resume.contact.location +
            "\n";
    }


    output +=
        "\nPROFILE\n";

    output +=
        "────────────────────────────────────────\n";


    resume.profile.forEach(
        item => {

            output +=
                "• " +
                item +
                "\n";
        }
    );


    output +=
        "\nEXPERIENCE\n";

    output +=
        "────────────────────────────────────────\n";


    resume.career_positions.forEach(
        position => {

            output +=
                position.job_title +
                "    " +
                position.dates +
                "\n";


            output +=
                position.employer +
                (
                    position.location
                    ? "    " + position.location
                    : ""
                ) +
                "\n\n";
        }
    );


    resume.skill_groups.forEach(
        group => {

            output +=
                group.name +
                "\n";


            group.accomplishments.forEach(
                accomplishment => {

                    output +=
                        "• " +
                        accomplishment +
                        "\n";
                }
            );


            output += "\n";
        }
    );


    if (
        resume.education &&
        resume.education.length
    ) {

        output +=
            "EDUCATION\n";

        output +=
            "────────────────────────────────────────\n";


        resume.education.forEach(
            item => {

                output +=
                    item.program_name +
                    (
                        item.dates
                        ? "    " + item.dates
                        : ""
                    ) +
                    "\n";


                output +=
                    item.school_name +
                    (
                        item.location
                        ? "    " + item.location
                        : ""
                    ) +
                    "\n\n";
            }
        );
    }


    if (
        resume.additional_training &&
        resume.additional_training.length
    ) {

        output +=
            "ADDITIONAL TRAINING\n";

        output +=
            "────────────────────────────────────────\n";


        resume.additional_training.forEach(
            item => {

                output +=
                    item.course_name +
                    (
                        item.date
                        ? "    " + item.date
                        : ""
                    ) +
                    "\n";


                output +=
                    item.provider +
                    (
                        item.location
                        ? "    " + item.location
                        : ""
                    ) +
                    "\n\n";
            }
        );
    }


    return output;
}


function coverLetterToText(
    letter
) {

    let output = "";


    output +=
        letter.candidate_name +
        "\n";


    const contact = [];


    if (letter.candidate_contact.phone) {

        contact.push(
            letter.candidate_contact.phone
        );
    }


    if (letter.candidate_contact.email) {

        contact.push(
            letter.candidate_contact.email
        );
    }


    if (letter.candidate_contact.linkedin) {

        contact.push(
            letter.candidate_contact.linkedin
        );
    }


    output +=
        contact.join(" | ") +
        "\n";


    if (letter.candidate_contact.location) {

        output +=
            letter.candidate_contact.location +
            "\n";
    }


    output += "\n";


    if (letter.date_line) {

        output +=
            letter.date_line +
            "\n\n";
    }


    const recipientLines = [

        letter.recipient.name,

        letter.recipient.position,

        letter.recipient.employer,

        letter.recipient.address,

        letter.recipient.phone,

        letter.recipient.email
    ];


    recipientLines.forEach(
        line => {

            if (line) {

                output +=
                    line +
                    "\n";
            }
        }
    );


    output += "\n";


    if (letter.subject_line) {

        output +=
            letter.subject_line +
            "\n\n";
    }


    output +=
        letter.salutation +
        "\n\n";


    output +=
        letter.paragraph_1 +
        "\n\n";


    output +=
        letter.paragraph_2 +
        "\n\n";


    output +=
        letter.paragraph_3 +
        "\n\n";


    output +=
        letter.paragraph_4 +
        "\n\n";


    output +=
        letter.closing +
        ",\n\n";


    output +=
        letter.candidate_name;


    return output;
}


async function downloadResume() {

    const data =
        new FormData();


    data.append(
        "resume_json",
        JSON.stringify(
            generatedApplication.resume
        )
    );


    const filename =
        safeFileName(
            storedAnalysis.company +
            "_" +
            storedAnalysis.job_title +
            "_Resume"
        );


    data.append(
        "filename",
        filename
    );


    await downloadFile(
        "/api/download/resume",
        data,
        filename + ".docx"
    );
}


async function downloadCoverLetter() {

    const data =
        new FormData();


    data.append(
        "cover_letter_json",
        JSON.stringify(
            generatedApplication.cover_letter
        )
    );


    const filename =
        safeFileName(
            storedAnalysis.company +
            "_" +
            storedAnalysis.job_title +
            "_Cover_Letter"
        );


    data.append(
        "filename",
        filename
    );


    await downloadFile(
        "/api/download/cover-letter",
        data,
        filename + ".docx"
    );
}











function startOver() {

    // Restore shared application state to the same
    // values used for a fresh page load.
    storedJobText = "";
    storedResumeText = "";
    storedAnalysis = null;
    generatedApplication = null;

    storedGapAnswers = [];
    storedGapVerification = null;

    storedIntegrityResult = null;

    achievementAnalysis = null;
    achievementAnswers = [];
    achievementVerification = null;

    recruiterReview = null;
    interviewPreparation = null;

    activeRequirementFilter = "ALL";


    el("jobText").value = "";

    el("resumeText").value = "";

    el("jobFile").value = "";

    el("resumeFile").value = "";


    // Restore the visual requirement-filter default.
    document
        .querySelectorAll(
            ".requirement-filter"
        )
        .forEach(
            button => {

                button.classList.toggle(
                    "active",
                    button.dataset.filter === "ALL"
                );
            }
        );


    showOnly(
        "step1"
    );
}
