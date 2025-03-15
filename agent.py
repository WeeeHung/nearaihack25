from nearai.agents.environment import Environment

# IMPORT THE MULTI-AGENT SYSTEM
from Agents.Screening_agent import ScreeningAgent
from Agents.Due_dillegence_report_agent import DueDiligenceReportAgent

def run(env: Environment):
    # A system message guides an agent to solve specific tasks.
    prompt = {
        "role": "system", 
        "content": "You are a helpful agent that coordinates due diligence analysis. "
                   "Your role is to collect information from users and pass it to specialized analysis agents. "
                   "You can handle PDF files, TXT files, and URLs that users provide. "
                   "When users share these resources, you will forward them to the appropriate analysis agents "
                   "and then compile their findings into a comprehensive due diligence report. "
                   "Ask users for any additional information needed to complete a thorough analysis."
    }

    screening_agent = ScreeningAgent(env)
    due_diligence_report_agent = DueDiligenceReportAgent(env)

    screening_output = screening_agent.run(prompt)
    report_output = due_diligence_report_agent.run([screening_output])

    env.add_reply(report_output)
    # Give the prompt back to the user
    env.request_user_input()

run(env)