from nearai.agents.environment import Environment


def run(env: Environment):
    # A system message guides an agent to solve specific tasks.
    prompt = {"role": "system", "content": "You are a helpful agent that will ask for Company data and give a basic Due Diligence report."}

    # Use the model set in the metadata to generate a response
    result = env.completion([prompt] + env.list_messages())

    # Store the result in the chat history
    env.add_reply(result)

    # Give the prompt back to the user
    env.request_user_input()

run(env)