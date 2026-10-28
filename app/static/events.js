// Static UI event wiring.
//
// HTML declares user intent through data-action.
// Workflow behavior remains owned by the corresponding
// application/domain functions.

document.addEventListener(
    "click",
    event => {

        const target =
            event.target.closest(
                "[data-action]"
            );


        if (!target) {
            return;
        }


        const action =
            target.dataset.action;


        switch (action) {

            case "go-back":
                goBack();
                break;


            case "show-step-2":
                showStep2();
                break;


            case "show-step-1":
                showStep1();
                break;


            case "analyze-application":
                analyzeApplication();
                break;


            case "filter-requirements":
                filterRequirements(
                    target.dataset.filter
                );
                break;


            case "verify-gap-answers":
                verifyGapAnswers();
                break;


            case "show-analysis":
                showOnly(
                    "analysisScreen"
                );
                break;


            case "start-achievement-optimizer":
                startAchievementOptimizer();
                break;


            case "show-verification":
                showOnly(
                    "verificationScreen"
                );
                break;


            case "submit-achievement-answers":
                submitAchievementAnswers();
                break;


            case "continue-final-results":
                continueToFinalResults();
                break;


            case "download-resume":
                downloadResume();
                break;


            case "download-cover-letter":
                downloadCoverLetter();
                break;


            case "run-interview-preparation":
                runInterviewPreparation();
                break;


            case "run-recruiter-review":
                runRecruiterReview();
                break;


            case "start-over":
                startOver();
                break;
        }
    }
);


// Dynamic choice controls are created after analysis.
// Event delegation keeps executable JavaScript out of
// generated HTML attributes.

document.addEventListener(
    "change",
    event => {

        const target =
            event.target;


        if (
            target.matches(
                "[data-gap-choice]"
            )
        ) {

            toggleGapDetails(
                target.dataset.gapChoice
            );

            return;
        }


        if (
            target.matches(
                "[data-achievement-choice]"
            )
        ) {

            toggleAchievementFields(
                target.dataset.achievementChoice
            );
        }
    }
);
