import os
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from question_answering_agent import question_answering_agent

# Load environment variables early so the model picks them up
load_dotenv()  # expects GOOGLE_API_KEY or Vertex AI envs [web:62]

def ensure_auth():
    """
    Ensure either Gemini API Key or Vertex AI env configuration is present.
    - Gemini API: set GOOGLE_API_KEY
    - Vertex AI: set GOOGLE_GENAI_USE_VERTEXAI=true, GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("1", "true", "yes")
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    if api_key:
        return  # Gemini API path OK [web:74][web:62]
    if use_vertex and project and location:
        return  # Vertex AI path OK [web:74]
    raise RuntimeError(
        "Missing model credentials. Set either:\n"
        " - GOOGLE_API_KEY=<your_gemini_api_key>\n"
        "or all of:\n"
        " - GOOGLE_GENAI_USE_VERTEXAI=true\n"
        " - GOOGLE_CLOUD_PROJECT=<gcp_project_id>\n"
        " - GOOGLE_CLOUD_LOCATION=<region, e.g., us-central1>\n"
    )  # [web:62][web:74]

ensure_auth()

# Create a new session service to store state
session_service_stateful = InMemorySessionService()  # [web:57]

initial_state = {
    "user_name": "Om Wankhede",
    "user_preferences": """
        I like to play Pickleball, Disc Golf, and Tennis.
        My favorite food is Mexican.
        My favorite TV show is Game of Thrones.
        Loves it when people like and subscribe to his YouTube channel.
    """,
}

# Create a NEW session
APP_NAME = "Om Bot"
USER_ID = "om_wankhede"
SESSION_ID = str(uuid.uuid4())
stateful_session = session_service_stateful.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state,
)
print("CREATED NEW SESSION:")
print(f"\tSession ID: {SESSION_ID}")

runner = Runner(
    agent=question_answering_agent,
    app_name=APP_NAME,
    session_service=session_service_stateful,
)  # standard Runner usage [web:57]

new_message = types.Content(
    role="user", parts=[types.Part(text="What is Om's favorite TV show?")]
)  # Content/Part usage [web:22]

for event in runner.run(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=new_message,
):
    if event.is_final_response():
        if event.content and event.content.parts:
            print(f"Final Response: {event.content.parts[0].text}")

print("==== Session Event Exploration ====")
session = session_service_stateful.get_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

# Log final Session state
print("=== Final Session State ===")
for key, value in session.state.items():
    print(f"{key}: {value}")
