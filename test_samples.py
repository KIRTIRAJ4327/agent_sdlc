"""Sample test requirements for ReqGuard prototype."""

# Test 1: FHA Loan (Should detect FHA, find MIP gaps)
FHA_INCOMPLETE = """
Build an FHA loan origination system for first-time homebuyers.
Support loans up to $450,000 with 3.5% down payment.
Integrate with existing credit pull system.
"""

# Test 2: VA Loan (Should detect VA, find entitlement gaps)
VA_INCOMPLETE = """
Create a VA loan processing module for veterans.
Support purchase and refinance transactions.
Funding fee should be waived for disabled veterans.
"""

# Test 3: Complete Conventional Loan (Should pass with high confidence)
CONVENTIONAL_COMPLETE = """
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
"""

# Test 4: USDA Loan (Should detect USDA)
USDA_INCOMPLETE = """
We need a USDA rural development loan product for low-income borrowers.
Target rural areas with 100% financing.
"""

# Test 5: Jumbo Loan (Should detect Jumbo)
JUMBO_INCOMPLETE = """
Create a jumbo loan product for high-net-worth individuals.
Loan amounts from $800,000 to $3,000,000.
Private banking integration required.
"""


def run_all_tests():
    """Run all sample tests."""
    from main import run_analysis

    tests = [
        ("FHA Incomplete", FHA_INCOMPLETE),
        ("VA Incomplete", VA_INCOMPLETE),
        ("Conventional Complete", CONVENTIONAL_COMPLETE),
        ("USDA Incomplete", USDA_INCOMPLETE),
        ("Jumbo Incomplete", JUMBO_INCOMPLETE),
    ]

    print("=" * 80)
    print("REQGUARD PROTOTYPE - TEST SUITE")
    print("=" * 80)

    for test_name, test_req in tests:
        print(f"\n\n{'=' * 80}")
        print(f"TEST: {test_name}")
        print(f"{'=' * 80}")
        print(f"\nInput Requirements:\n{test_req[:100]}...")

        try:
            result = run_analysis(test_req)

            print(f"\n[OK] Loan Type: {result['loan_type']['primary_type']}")
            print(f"[OK] Confidence: {result['confidence']:.0%}")
            print(f"[OK] Outcome: {result['outcome']}")
            print(f"[OK] Gaps Found: {len(result['gaps'])}")
            print(f"[OK] Questions Generated: {len(result['questions'])}")

            if result['questions']:
                print(f"\nTop 3 Questions:")
                for i, q in enumerate(result['questions'][:3], 1):
                    print(f"  {i}. [{q['severity']}] {q['question']}")

            print(f"\n{'=' * 80}")
            print("TEST PASSED [OK]")

        except Exception as e:
            print(f"\n{'=' * 80}")
            print(f"TEST FAILED [X]: {str(e)}")
            import traceback
            traceback.print_exc()

    print(f"\n\n{'=' * 80}")
    print("ALL TESTS COMPLETED")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    run_all_tests()
