import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from memory_agent.agent import memory_agent
from utils import call_agent_async

load_dotenv()

# === Part 1 : Initialize the Persistent service ===
# Using SQLite database for persistent storage
db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# ==== Part 2 : Define initial State ====
# This will only be used when creating a new session
initial_state = {
    "user_name": "Om Wankhede",
    "reminders": [],
}

async def main_async():
    # setup constants
    APP_NAME = "Memory Agent"
    USER_ID = "aiwithom"

    # === Part 3 : Session Management ===
    # check for existing session for this user
    existing_resp = session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID,
    )  # returns ListSessionsResponse wrapper [web:5][web:2]

    # Extract the inner list of Session objects safely
    sessions = list(getattr(existing_resp, "sessions", []) or [])  # [] if None [web:5][web:2]

    # if there's an existing session, use it otherwise create a new one
    if sessions:
        # Prefer the most recent session (defensive sort)
        sessions.sort(key=lambda s: getattr(s, "last_update_time", 0.0), reverse=True)  # [web:5]
        SESSION_ID = sessions[0].id
        print(f"Continuing existing session : {SESSION_ID}")
    else:
        # Create a new session with initial state
        new_session = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"Created new session : {SESSION_ID}")

    # === Part 4 : Agent Runner setup ===
    runner = Runner(
        agent=memory_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )  # Runner works with user_id + session_id per turn [web:22]

    # === Part 5 : Interactive Conversation loop ===
    print("\nWelcome to the Memory Agent Chat!")
    print("Your reminders will be remembered across conversations.")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        # Get the user input
        user_input = input("You: ")

        # Check if the user wants to exit
        if user_input.lower() in ['exit', 'quit']:
            print("Ending conversation. Your data has been saved to the database.")
            break

        # Process the user query through the agent
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)  # expects runner.run_async inside [web:22]


if __name__ == "__main__":
    asyncio.run(main_async())
