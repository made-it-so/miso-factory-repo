import os
from . import agents

def run_pipeline(job_id: str, prompt: str):
    """
    The main entry point for the Genesis Pipeline, now with the first real agent.
    """
    print(f"ORCHESTRATOR: Starting true agent pipeline for job {job_id}.")
    
    # 1. Call the EthicsAgent
    ethics_agent = agents.EthicsAgent()
    is_compliant, rationale = ethics_agent.evaluate(prompt)

    # 2. Halt if the prompt is not compliant
    if not is_compliant:
        print(f"ORCHESTRATOR: Pipeline halted by EthicsAgent for job {job_id}.")
        return f"Job failed: {rationale}"

    # --- Placeholder for subsequent agents ---
    
    # 3. Create the output directory if it doesn't exist
    output_dir = "generated_projects"
    os.makedirs(output_dir, exist_ok=True)
    
    # 4. Write the actual output file
    output_path = os.path.join(output_dir, f"{job_id}_mip_001.md")
    report_content = f"# MISO Improvement Proposal: MIP-001\n\n"
    report_content += f"## Prompt Analysis\n\n- **Original Prompt:** {prompt}\n"
    report_content += f"- **Ethical Compliance Check:** {rationale}\n\n"
    report_content += "## Research Findings\n\n- **[Placeholder]** Analysis of agentic workflow advancements would be detailed here.\n"
    
    with open(output_path, "w") as f:
        f.write(report_content)
    
    result_message = f"MIP-001 research complete. Report generated at {output_path}"
    print(f"ORCHESTRATOR: Pipeline finished for job {job_id}. Report at {output_path}")
    
    return result_message
