from nearai.agents.environment import Environment

# IMPORT THE MULTI-AGENT SYSTEM
from Agents.Screening_agent import ScreeningAgent

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

    # Use the model set in the metadata to generate a response
    # result = env.completion([prompt] + env.list_messages()) # including the prompt with the full chat history (TODO: check if this is necessary)

    screening_output = ScreeningAgent.run(prompt)

    result = screening_output
    # Store the result in the chat history
    env.add_reply(result)

    # Give the prompt back to the user
    env.request_user_input()

run(env)