# labs/run_all_tests.py
import os
import sys

# Ensure labs directory is in the import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_identity import test_identity_fidelity
from test_memory import test_memory_scaling_and_ambiguity
from test_pipeline import test_knowledge_promotion_pipeline
from test_governance import test_governance_compliance
from test_context_assembly import test_context_assembly_budgets

def run_suite():
    print("==================================================")
    print("   JARVIS PHASE 0 VALIDATION TEST SUITE           ")
    print("==================================================")
    
    report = {}
    
    # 1. Identity Test
    try:
        identity_results = test_identity_fidelity()
        report["Identity Test"] = "PASSED" if identity_results else "FAILED (No models found)"
    except Exception as e:
        print(f"Error running Identity tests: {e}")
        report["Identity Test"] = f"CRASHED: {e}"
        
    # 2. Memory Test
    print("\n" + "="*50)
    try:
        memory_results = test_memory_scaling_and_ambiguity()
        report["Memory Test"] = "PASSED" if memory_results else "FAILED"
    except Exception as e:
        print(f"Error running Memory tests: {e}")
        report["Memory Test"] = f"CRASHED: {e}"
        
    # 3. Pipeline Test
    print("\n" + "="*50)
    try:
        pipeline_results = test_knowledge_promotion_pipeline()
        report["Pipeline Test"] = "PASSED" if pipeline_results else "FAILED"
    except Exception as e:
        print(f"Error running Pipeline tests: {e}")
        report["Pipeline Test"] = f"CRASHED: {e}"
        
    # 4. Governance Test
    print("\n" + "="*50)
    try:
        gov_results = test_governance_compliance()
        report["Governance Test"] = "PASSED" if gov_results else "FAILED"
    except Exception as e:
        print(f"Error running Governance tests: {e}")
        report["Governance Test"] = f"CRASHED: {e}"
        
    # 5. Context Assembly Test
    print("\n" + "="*50)
    try:
        assembly_results = test_context_assembly_budgets()
        report["Context Assembly Test"] = "PASSED" if assembly_results else "FAILED"
    except Exception as e:
        print(f"Error running Context Assembly tests: {e}")
        report["Context Assembly Test"] = f"CRASHED: {e}"
        
    print("\n==================================================")
    print("            FINAL DASHBOARD REPORT                ")
    print("==================================================")
    for test_name, status in report.items():
        print(f"  - {test_name:<25}: {status}")
    print("==================================================")

if __name__ == "__main__":
    run_suite()
