from agents.data_science_agent import DataScienceAgent
import numpy as np
import json

def run_test():
    """
    Tests the DataScienceAgent's ability to generate a fairer dataset.
    """
    print("--- Creating test dataset with known bias ---")
    num_samples = 200
    # Create a dataset where feature 0 is strongly correlated with the protected attribute
    dummy_data = np.random.rand(num_samples, 5)
    dummy_protected_attributes = (dummy_data[:, 0] > 0.7).astype(int)
    
    # Ensure the groups are imbalanced to make the test realistic
    num_in_group_1 = np.sum(dummy_protected_attributes)
    print(f"Initial data distribution: {num_samples - num_in_group_1} in group 0, {num_in_group_1} in group 1.")

    ds_agent = DataScienceAgent()
    result = ds_agent.generate_fair_private_data(dummy_data, dummy_protected_attributes)

    print("\n\n========== DATASCIENCE AGENT TEST RESULT ==========")
    print(json.dumps(result, indent=2))
    print("\n================================================")
    print("Note: A lower 'new_fairness_score' demonstrates the agent successfully reduced bias.")

if __name__ == "__main__":
    run_test()
