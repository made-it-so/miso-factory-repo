from agents.genesis_agent import GenesisAgent
from agents.auditor_agent import AuditorAgent
from agents.gauntlet import Gauntlet
from agents.test_generation_agent import TestGenerationAgent
import os
import json

def run_colosseum_challenge(challenge, target_file, max_retries=3):
    """
    Runs a full generate -> (lint -> security -> complexity) -> correct -> audit -> generate_tests -> run_tests cycle.
    """
    print(f"--- COLOSSEUM CHALLENGE STARTED ---")
    print(f"Target: {target_file}\nChallenge: {challenge}")

    target_file_path = os.path.join('agents', target_file)
    with open(target_file_path, 'r', encoding='utf-8') as f:
        original_code = f.read()

    genesis_agent = GenesisAgent()
    gauntlet = Gauntlet(min_score=7.0, max_complexity=10)
    auditor_agent = AuditorAgent()
    test_agent = TestGenerationAgent()

    challenger_code = original_code
    for attempt in range(max_retries):
        print(f"\n--- Cycle Attempt #{attempt + 1} ---")
        
        current_challenge = challenge
        if attempt > 0:
            current_challenge = f"Your previous attempt failed a check. Please fix the following errors and resubmit the code.\n\nFailure Report:\n{failure_details}\n\nOriginal Challenge: {challenge}"

        challenger_code = genesis_agent.generate_challenger_code(current_challenge, challenger_code)
        
        # --- THE GAUNTLET: FULL SEQUENCE ---
        linter_result = gauntlet.run_linter_check(challenger_code)
        if not linter_result["passed"]:
            print(f"\nAttempt #{attempt + 1} FAILED Linter. Retrying...")
            failure_details = linter_result['details']
            continue

        security_result = gauntlet.run_security_check(challenger_code)
        if not security_result["passed"]:
            print(f"\nAttempt #{attempt + 1} FAILED Security Scan. Retrying...")
            failure_details = security_result['details']
            continue

        complexity_result = gauntlet.run_complexity_check(challenger_code)
        if not complexity_result["passed"]:
            print(f"\nAttempt #{attempt + 1} FAILED Complexity Check. Retrying...")
            failure_details = complexity_result['details']
            continue
        
        print("\nChallenger code PASSED all quantitative checks. Proceeding to Auditor review.")
        
        audit_result = auditor_agent.calculate_pacs_review(challenge, original_code, challenger_code, cohort_codes=[])
        print("\n========== AUDIT REPORT ==========\n" + json.dumps(audit_result, indent=2))

        print("\nAudit passed. Proceeding to generate unit tests...")
        generated_tests = test_agent.generate_tests(challenger_code, target_file)
        print("\n========== GENERATED PYTEST TESTS ==========\n" + generated_tests)
        
        test_run_result = gauntlet.run_unit_tests(challenger_code, generated_tests, target_file)
        
        print("\n--- COLOSSEUM CHALLENGE FINISHED ---")
        return {"audit": audit_result, "tests": generated_tests, "test_run": test_run_result}

    print("\n--- COLOSSEUM CHALLENGE FINISHED (FAILED) ---")
    return {"error": "Challenger code failed The Gauntlet after max retries."}

if __name__ == "__main__":
    test_challenge = "Refactor this code to include full PEP 484 type hints and add Google-style docstrings to the class and all methods."
    test_file = "anonymizer_agent.py"
    result = run_colosseum_challenge(test_challenge, test_file)
    print("\n\n========== FINAL RESULT ==========")
    print(json.dumps(result, indent=2))
