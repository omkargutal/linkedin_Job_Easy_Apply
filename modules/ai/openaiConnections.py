from typing import Literal
from openai import OpenAI
from pyautogui import confirm

from config.secrets import *
from config import settings
from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *


# ------------------------------------------------------------------
# Error Handling
# ------------------------------------------------------------------

def ai_error_alert(message: str, error: Exception, title: str = "AI Error") -> None:
    """
    Centralized AI error handler
    """
    critical_error_log(message, error)

    if settings.showAiErrorAlerts:
        if confirm(
            f"{message}\n{error}",
            title,
            ["Pause AI error alerts", "Continue"]
        ) == "Pause AI error alerts":
            settings.showAiErrorAlerts = False


# ------------------------------------------------------------------
# Client
# ------------------------------------------------------------------

def ai_create_openai_client() -> OpenAI | None:
    """
    Creates OpenAI / OpenAI-compatible client
    """
    try:
        if not use_AI:
            raise ValueError("AI disabled (use_AI=False)")

        if not llm_api_key or "YOUR_API_KEY" in llm_api_key:
            raise ValueError("Invalid API key")

        base_url = llm_api_url.rstrip("/")

        print_lg("Creating OpenAI client...")
        client = OpenAI(api_key=llm_api_key, base_url=base_url)

        # lightweight validation
        client.models.list()

        print_lg("---- OPENAI CLIENT READY ----")
        print_lg(f"API URL : {base_url}")
        print_lg(f"Model   : {llm_model}")
        print_lg("--------------------------------")

        return client

    except Exception as e:
        ai_error_alert("Failed to create OpenAI client", e)
        return None


def ai_close_openai_client(client: OpenAI) -> None:
    """
    Safely closes client
    """
    try:
        if client:
            client.close()
    except Exception as e:
        ai_error_alert("Failed to close OpenAI client", e)


# ------------------------------------------------------------------
# Completion
# ------------------------------------------------------------------

def ai_completion(
    client: OpenAI,
    messages: list[dict],
    response_format: dict | None = None,
    temperature: float = 0.0,
    stream: bool = stream_output
) -> str | dict:
    """
    Core chat completion wrapper
    """
    if not client:
        raise ValueError("OpenAI client not initialized")

    try:
        params = {
            "model": llm_model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }

        if response_format and llm_spec in {"openai", "openai-like"}:
            params["response_format"] = response_format

        print_lg("Calling AI completion...")
        completion = client.chat.completions.create(**params)

        result = ""

        if stream:
            print_lg("-- STREAM START --")
            for chunk in completion:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    result += delta.content
                    print_lg(delta.content, end="", flush=True)
            print_lg("\n-- STREAM END --")
        else:
            result = completion.choices[0].message.content

        if not result:
            raise ValueError("Empty AI response")

        if response_format:
            return convert_to_json(result)

        return result

    except Exception as e:
        ai_error_alert("AI completion failed", e)
        raise


# ------------------------------------------------------------------
# Skill Extraction
# ------------------------------------------------------------------

def ai_extract_skills(
    client: OpenAI,
    job_description: str,
    stream: bool = stream_output
) -> dict:
    """
    Extracts skills from job description
    """
    try:
        print_lg("Extracting skills...")
        prompt = extract_skills_prompt.format(job_description)
        messages = [{"role": "user", "content": prompt}]

        return ai_completion(
            client,
            messages,
            response_format=extract_skills_response_format,
            stream=stream
        )

    except Exception as e:
        ai_error_alert("Skill extraction failed", e)
        return {"error": str(e)}


# ------------------------------------------------------------------
# Question Answering
# ------------------------------------------------------------------

def ai_answer_question(
    client: OpenAI,
    question: str,
    options: list[str] | None = None,
    question_type: Literal["text", "textarea", "single_select", "multiple_select"] = "text",
    job_description: str | None = None,
    about_company: str | None = None,
    user_information_all: str | None = None,
    stream: bool = stream_output
) -> str | dict:
    """
    Answers application questions
    """
    try:
        print_lg("Answering question with AI...")
        prompt = ai_answer_prompt.format(user_information_all or "N/A", question)

        if options and question_type in {"single_select", "multiple_select"}:
            prompt += "\n\nOPTIONS:\n" + "\n".join(f"- {o}" for o in options)
            prompt += (
                "\n\nSelect EXACTLY ONE option."
                if question_type == "single_select"
                else "\n\nSelect ALL applicable options."
            )

        if job_description:
            prompt += f"\n\nJOB DESCRIPTION:\n{job_description}"
        if about_company:
            prompt += f"\n\nABOUT COMPANY:\n{about_company}"

        messages = [{"role": "user", "content": prompt}]
        return ai_completion(client, messages, stream=stream)

    except Exception as e:
        ai_error_alert("Question answering failed", e)
        return {"error": str(e)}


# ------------------------------------------------------------------
# Placeholders (intentionally explicit)
# ------------------------------------------------------------------

def ai_gen_experience(*_, **__) -> dict:
    raise NotImplementedError("ai_gen_experience not implemented yet")


def ai_generate_resume(*_, **__) -> dict:
    raise NotImplementedError("ai_generate_resume not implemented yet")


def ai_generate_coverletter(*_, **__) -> dict:
    raise NotImplementedError("ai_generate_coverletter not implemented yet")


def ai_evaluate_resume(*_, **__) -> dict:
    raise NotImplementedError("ai_evaluate_resume not implemented yet")


def ai_check_job_relevance(*_, **__) -> dict:
    raise NotImplementedError("ai_check_job_relevance not implemented yet")
