"""One-shot Gemini connectivity check.

After putting your key in chatbot-api/.env, run:

    python -m app.check_gemini
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    if not settings.google_api_key:
        print("GOOGLE_API_KEY is not set - add it to chatbot-api/.env first.")
        return

    model = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.google_api_key,
        temperature=0,
    )
    reply = model.invoke("Say hello to a new teammate in fewer than 10 words.")
    print(f"Model : {settings.gemini_model}")
    print(f"Reply : {reply.content}")


if __name__ == "__main__":
    main()
