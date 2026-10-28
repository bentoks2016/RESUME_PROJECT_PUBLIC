"""
Synthetic benchmark data for Phase 4 model evaluation.

All names, employers, projects, and facts in this module
are fictional and exist solely for model benchmarking.
"""

JOB_TEXT = """
Senior Operations Transformation Manager

Northstar Manufacturing is seeking a Senior Operations
Transformation Manager.

Required:
- Lead complex operational transformation programs.
- Manage cross-functional stakeholders.
- Improve operational performance using data.
- Lead automation initiatives.
- Manage project risk and governance.
- Coach teams through organizational change.
- Strong executive communication.

Preferred:
- Direct SAP S/4HANA implementation experience.
- Experience applying AI to industrial operations.
- Experience in multi-site manufacturing environments.

The role will lead transformation initiatives across
several manufacturing sites and work with technology,
operations, engineering, and senior leadership.
"""


RESUME_TEXT = """
ALEX MORGAN

Operations transformation professional with 11 years
of experience in manufacturing and operational
improvement.

EXPERIENCE

Transformation Manager
Fictional Meridian Components
2019-2026

- Led a cross-functional operational improvement
  program across four manufacturing sites.
- Coordinated operations, engineering, finance, and
  technology stakeholders.
- Introduced automated production reporting that
  reduced weekly manual reporting effort by 18 hours.
- Managed program risks, governance reviews, and
  executive status reporting.
- Led adoption workshops for supervisors and
  operational teams.
- Used Power BI dashboards to identify production
  bottlenecks and prioritize improvement activity.
- Participated in ERP modernization projects involving
  SAP-related business processes but did not personally
  implement SAP S/4HANA.
- Supported technology-enabled process improvements.

Operations Improvement Lead
Fictional Apex Industrial
2015-2019

- Led continuous-improvement projects in manufacturing.
- Facilitated cross-functional problem-solving sessions.
- Developed performance reporting for site leadership.

EDUCATION

Bachelor of Business Administration

TRAINING

Lean Six Sigma Green Belt
Project Management Fundamentals
"""


# Facts deliberately NOT present in the synthetic resume.
PROHIBITED_CANDIDATE_CLAIMS = [
    "implemented SAP S/4HANA",
    "led an SAP S/4HANA implementation",
    "implemented artificial intelligence",
    "implemented AI",
    "led AI implementation",
    "machine learning implementation",
]


# Important benchmark distinctions:
#
# DIRECT:
# - multi-site manufacturing
# - cross-functional leadership
# - transformation leadership
# - automation/reporting
# - risk/governance
# - change/adoption
#
# TRANSFERABLE/ADJACENT:
# - SAP-related ERP modernization exposure
#
# MISSING:
# - direct SAP S/4HANA implementation
# - industrial AI implementation
