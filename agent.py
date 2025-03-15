from nearai.agents.environment import Environment
import json

# IMPORT THE MULTI-AGENT SYSTEM
from Agents.screening_agent import ScreeningAgent
from Agents.due_dillegence_report_agent import DueDiligenceReportAgent
from Agents.financials_agent import FinancialsAgent
from Agents.competitors_agent import CompetitorsAgent
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

    env.add_system_log("Starting due diligence analysis")
        
    screening_agent = ScreeningAgent(env)
    financials_agent = FinancialsAgent(env)
    competitors_agent = CompetitorsAgent(env)
    due_diligence_report_agent = DueDiligenceReportAgent(env)

    env.add_system_log("All agents initialized")

    messages = env.list_messages()
    system_prompt = json.dumps(prompt) if isinstance(prompt, dict) else str(prompt)
    message_strings = [str(msg) for msg in messages]
    
    screening_output = screening_agent.run([system_prompt] + message_strings)
    financials_output = financials_agent.run(screening_output)
    competitors_output = competitors_agent.run(screening_output)
    report_output = due_diligence_report_agent.run([screening_output, financials_output, competitors_output])
    
    env.add_reply(report_output)
    # Give the prompt back to the user
    env.request_user_input()

run(env)