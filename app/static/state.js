// Shared mutable frontend application state.
//
// Kept in a classic script so existing workflow code can
// continue using these bindings during incremental refactoring.

let currentScreen = "step1";

let storedJobText = "";
let storedResumeText = "";
let storedAnalysis = null;
let generatedApplication = null;

let storedGapAnswers = [];
let storedGapVerification = null;

let storedIntegrityResult = null;

let achievementAnalysis = null;
let achievementAnswers = [];
let achievementVerification = null;

let recruiterReview = null;

let interviewPreparation = null;

let activeRequirementFilter = "ALL";
