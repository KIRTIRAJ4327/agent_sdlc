"""Author and Critic agents for ReqGuard."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from checklists import detect_loan_type, get_checklist_for_loan_type, Severity

class ReqGuardAuthor:
    """Author agent: Extracts and structures requirements."""

    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Business Systems Analyst for mortgage systems.
Extract structured requirements from the provided BRD/User Story.

Loan Type Detected: {loan_type}

CRITICAL INSTRUCTION:
Extract ONLY what is explicitly stated or strongly implied in the input.
Do NOT invent, hallucinate, or auto-complete detailed requirements that are not present.
If a section (like 'Regulatory' or 'Data') is not mentioned in the input, state "Not specified in input" for that section.

Provide a structured analysis:
1. Functional Requirements (what the system must do)
2. Non-Functional Requirements (performance, security)
3. Regulatory Requirements (TRID, HMDA, state laws)
4. Integration Requirements (systems to connect with)
5. Data Requirements (fields, validations)
"""),
            ("human", "{requirements}")
        ])

    def extract(self, raw_requirements: str) -> dict:
        """Extract structured requirements."""
        loan_info = detect_loan_type(raw_requirements)

        chain = self.prompt | self.llm
        result = chain.invoke({
            "loan_type": loan_info["primary_type"],
            "requirements": raw_requirements
        })

        return {
            "loan_classification": loan_info,
            "structured_requirements": result.content,
            "raw_input": raw_requirements
        }


class ReqGuardCritic:
    """Critic agent: Finds gaps, edge cases, compliance issues."""

    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a CRITIC. Your job is to ATTACK these requirements.
Find problems, not solutions. Be adversarial.

Checklist gaps found: {checklist_gaps}

Find additional issues:
1. Edge cases not covered
2. Ambiguous language that will cause defects
3. Missing integration points
4. Regulatory gaps beyond the checklist
5. Conflicts or contradictions

Be harsh. Production failures are expensive.
"""),
            ("human", "{requirements}")
        ])

    def critique(self, author_output: dict, checklist_gaps: list) -> dict:
        """Critique the requirements."""

        chain = self.prompt | self.llm
        result = chain.invoke({
            "checklist_gaps": [g["description"] for g in checklist_gaps],
            "requirements": author_output["structured_requirements"]
        })

        return {
            "checklist_gaps": checklist_gaps,
            "llm_critique": result.content,
            "loan_type": author_output["loan_classification"]["primary_type"]
        }

    def check_against_checklist(self, author_output: dict) -> list:
        """Check requirements against checklist using LLM for intelligent validation."""
        loan_type = author_output["loan_classification"]["primary_type"]
        checklist = get_checklist_for_loan_type(loan_type)
        requirements_text = author_output["structured_requirements"]

        gaps = []
        for category, items in checklist.items():
            # Create a prompt to check all items in this category at once
            checklist_items_text = "\n".join([f"- {item.key}: {item.description}" for item in items])

            prompt = f"""Review the following requirements text and determine if these specific checklist items are covered.
            
            REQUIREMENTS:
            {requirements_text[:4000]}
            
            CHECKLIST ITEMS TO VERIFY:
            {checklist_items_text}
            
            For each item, answer YES if it is covered/addressed, or NO if it is missing/undefined.
            IMPORTANT: If the requirement is mentioned (even indirectly or with specific values like numbers), mark it as YES.
            
            Return ONLY a JSON object: {{"item_key": "YES/NO"}}
            
            Example: {{"loan_amount": "YES", "dti_thresholds": "NO"}}
            """

            try:
                # Use LLM to intelligently check if requirements are covered
                response = self.llm.invoke(prompt)
                content = response.content.strip().replace("```json", "").replace("```", "")
                import json
                results = json.loads(content)

                for item in items:
                    # If the LLM says NO (or didn't return a result for it), mark as gap
                    status = results.get(item.key, "NO").upper()
                    if "NO" in status:
                        gaps.append({
                            "category": category,
                            "key": item.key,
                            "description": item.description,
                            "severity": item.severity.value,
                            "question": item.example_question
                        })
            except Exception as e:
                # Fallback to loose keyword matching if LLM fails
                print(f"LLM validation failed for {category}: {e}. Falling back to keywords.")
                for item in items:
                    if item.key.replace("_", " ") not in requirements_text.lower():
                        gaps.append({
                            "category": category,
                            "key": item.key,
                            "description": item.description,
                            "severity": item.severity.value,
                            "question": item.example_question
                        })

        return gaps


def calculate_confidence(gaps: list, llm_critique: str = "") -> float:
    """Calculate confidence using hybrid Rule + LLM approach."""
    
    # 1. Rule-Based Score (The "Math")
    rule_score = 1.0
    for gap in gaps:
        if gap["severity"] == "critical":
            rule_score -= 0.10  # Reduced from 0.15 to be less punitive
        elif gap["severity"] == "high":
            rule_score -= 0.05  # Reduced from 0.08
        elif gap["severity"] == "medium":
            rule_score -= 0.02  # Reduced from 0.03
    rule_score = max(0.0, rule_score)

    # 2. LLM Sentiment Score (The "Vibe")
    # If the critique is very negative ("catastrophic", "failure"), lower the score.
    # Simple heuristic for now to avoid another API call:
    critique_lower = llm_critique.lower()
    llm_penalty = 0.0
    if "catastrophic" in critique_lower or "critical failure" in critique_lower:
        llm_penalty = 0.20
    elif "major gap" in critique_lower or "serious" in critique_lower:
        llm_penalty = 0.10

    # 3. Blended Score
    # We trust the rules more (70%) than the sentiment (30%)
    final_score = rule_score - llm_penalty
    
    return max(0.0, min(1.0, final_score))


def determine_outcome(confidence: float) -> str:
    """Determine outcome based on confidence."""
    if confidence >= 0.95:
        return "complete"
    elif confidence >= 0.70:
        return "partial"
    else:
        return "clarify"


def generate_questions(gaps: list, max_questions: int = 5) -> list:
    """Generate prioritized questions from gaps."""
    # Sort by severity
    sorted_gaps = sorted(gaps, key=lambda g:
        {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(g["severity"], 4))

    questions = []
    for gap in sorted_gaps[:max_questions]:
        questions.append({
            "question": gap["question"],
            "severity": gap["severity"],
            "category": gap["category"]
        })

    return questions
