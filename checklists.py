"""Mortgage requirement checklists for gap detection."""

from enum import Enum
from dataclasses import dataclass

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ChecklistItem:
    key: str
    description: str
    severity: Severity
    example_question: str

# Loan type detection triggers
LOAN_TYPE_TRIGGERS = {
    "FHA": ["fha", "federal housing", "hud", "mip", "upfront mip", "203b", "203k"],
    "VA": ["va", "veteran", "military", "certificate of eligibility", "coe", "funding fee"],
    "USDA": ["usda", "rural development", "rural housing", "guaranteed rural"],
    "Conventional": ["conventional", "fannie mae", "freddie mac", "conforming", "gse"],
    "Jumbo": ["jumbo", "non-conforming", "high balance", "super conforming"],
    "Reverse": ["reverse mortgage", "hecm", "home equity conversion"],
}

# Core checklist items
CHECKLIST = {
    "loan_product": [
        ChecklistItem("loan_type", "Loan type clearly specified", Severity.CRITICAL,
                     "What type of loan is this? (FHA, VA, Conventional, etc.)"),
        ChecklistItem("loan_amount", "Loan amount or range specified", Severity.CRITICAL,
                     "What is the expected loan amount range?"),
        ChecklistItem("interest_rate_type", "Fixed or adjustable rate specified", Severity.HIGH,
                     "Is this a fixed-rate or adjustable-rate mortgage?"),
        ChecklistItem("loan_term", "Loan term specified (15, 20, 30 years)", Severity.HIGH,
                     "What loan terms should be supported?"),
        ChecklistItem("ltv_limits", "LTV limits defined", Severity.HIGH,
                     "What are the maximum LTV ratios for this product?"),
    ],
    "borrower": [
        ChecklistItem("dti_thresholds", "DTI thresholds defined", Severity.CRITICAL,
                     "What are the front-end and back-end DTI limits?"),
        ChecklistItem("credit_score", "Minimum credit score requirements", Severity.CRITICAL,
                     "What is the minimum credit score required?"),
        ChecklistItem("income_verification", "Income verification method specified", Severity.HIGH,
                     "How should income be verified? (W2, tax returns, bank statements)"),
        ChecklistItem("employment_history", "Employment history requirements", Severity.MEDIUM,
                     "What employment history is required?"),
        ChecklistItem("reserves", "Reserve requirements specified", Severity.MEDIUM,
                     "How many months of reserves are required?"),
    ],
    "property": [
        ChecklistItem("property_types", "Eligible property types listed", Severity.HIGH,
                     "What property types are eligible? (SFR, Condo, Multi-unit)"),
        ChecklistItem("occupancy", "Occupancy type specified", Severity.HIGH,
                     "What occupancy types are allowed? (Primary, Second home, Investment)"),
        ChecklistItem("appraisal", "Appraisal requirements defined", Severity.HIGH,
                     "What are the appraisal requirements?"),
    ],
    "compliance": [
        ChecklistItem("trid_timing", "TRID disclosure timing requirements", Severity.CRITICAL,
                     "How will TRID timing requirements be enforced?"),
        ChecklistItem("hmda_fields", "HMDA data collection requirements", Severity.CRITICAL,
                     "Which HMDA fields need to be collected?"),
        ChecklistItem("fair_lending", "Fair lending compliance approach", Severity.CRITICAL,
                     "How will fair lending compliance be ensured?"),
        ChecklistItem("state_specific", "State-specific requirements noted", Severity.HIGH,
                     "Which states will this product be offered in? Any state-specific rules?"),
    ],
}

def detect_loan_type(text: str) -> dict:
    """Detect loan type from requirement text."""
    text_lower = text.lower()
    detected = []

    for loan_type, triggers in LOAN_TYPE_TRIGGERS.items():
        if any(trigger in text_lower for trigger in triggers):
            detected.append(loan_type)

    return {
        "primary_type": detected[0] if detected else "Conventional",
        "all_detected": detected,
        "confidence": 0.9 if detected else 0.5
    }

def get_checklist_for_loan_type(loan_type: str) -> dict:
    """Get enhanced checklist based on loan type."""
    base = CHECKLIST.copy()

    # Add loan-type specific items
    if loan_type == "FHA":
        base["fha_specific"] = [
            ChecklistItem("mip_calculation", "MIP calculation rules", Severity.CRITICAL,
                         "How should upfront and annual MIP be calculated?"),
            ChecklistItem("fha_limits", "FHA loan limits by county", Severity.HIGH,
                         "How will FHA loan limits be determined?"),
        ]
    elif loan_type == "VA":
        base["va_specific"] = [
            ChecklistItem("entitlement", "VA entitlement verification", Severity.CRITICAL,
                         "How will VA entitlement be verified?"),
            ChecklistItem("funding_fee", "VA funding fee calculation", Severity.CRITICAL,
                         "How should the VA funding fee be calculated?"),
        ]

    return base
