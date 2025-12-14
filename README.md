# ReqGuard Prototype

AI-powered mortgage requirements validator using adversarial validation pattern.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# GOOGLE_API_KEY=your-gemini-api-key-here
```

### 3. Run the Application

**Option A: Web UI (Recommended)**
```bash
streamlit run ui.py
```

**Option B: Command Line Test**
```bash
python main.py
```

## How It Works

ReqGuard uses an **Author-Critic-Gate** pattern:

1. **Author** - Extracts and structures requirements
2. **Critic** - Finds gaps, compliance issues, and edge cases
3. **Gate** - Human decision point for approval or refinement

## Features

- **Loan Type Detection** - Automatically classifies FHA, VA, Conventional, etc.
- **Gap Detection** - Checks against mortgage compliance checklists
- **Confidence Scoring** - Quantifies requirement completeness
- **Human-in-the-Loop** - BSA makes final approval decisions

## Confidence Thresholds

- **Complete** (≥95%): Auto-forward to next stage
- **Partial** (70-94%): Continue with warning
- **Clarify** (<70%): Human input required

## Sample Test Cases

### Test 1: FHA Loan (Incomplete)
```
Build an FHA loan origination system for first-time homebuyers.
Support loans up to $450,000 with 3.5% down payment.
Integrate with existing credit pull system.
```
Expected: Detects FHA type, finds MIP and DTI gaps

### Test 2: VA Loan (Incomplete)
```
Create a VA loan processing module for veterans.
Support purchase and refinance transactions.
Funding fee should be waived for disabled veterans.
```
Expected: Detects VA type, finds entitlement and credit score gaps

### Test 3: Conventional (Complete)
```
Build a conventional conforming loan module.
Loan type: Conventional 30-year fixed
Loan amount: $100,000 - $726,200 (2024 conforming limits)
LTV: Up to 97% with PMI, 80% without
DTI: Front-end 28%, Back-end 36% (43% with compensating factors)
Credit score: Minimum 620, better pricing at 740+
Property types: SFR, Condo, 2-4 unit
Occupancy: Primary residence only
TRID: LE within 3 days, CD 3 days before close
HMDA: Collect all required fields per 2024 guidelines
Income: W2 (2 years), tax returns for self-employed
Reserves: 2 months for loans up to $500K
```
Expected: High confidence (≥95%), few or no gaps

## Architecture

```
INPUT → Author (extract) → Critic (attack) → Gate (human) → OUTPUT
           ↑                    │
           └────────────────────┘
              (max 3 iterations)
```

## Project Structure

```
reqguard-prototype/
├── checklists.py    # Loan type detection & validation rules
├── agents.py        # Author & Critic agents
├── main.py          # LangGraph workflow
├── ui.py            # Streamlit interface
├── requirements.txt
└── .env.example
```

## Demo Script (5 minutes)

1. Show the problem: "30% of mortgage projects require rework"
2. Paste incomplete FHA requirements
3. Show loan type detection
4. Show structured requirements from Author
5. Show gaps found by Critic
6. Show confidence score and outcome
7. Show prioritized questions
8. Demonstrate approve/refine workflow

## Built With

- **LangChain** - LLM framework
- **LangGraph** - Workflow orchestration
- **Gemini** - Google's LLM
- **Streamlit** - Web UI

## Next Steps

To build the full 6-agent system, see `SYSTEM_PROMPT.md` in the parent directory.
