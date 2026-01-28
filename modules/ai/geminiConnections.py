from google import genai
from typing import Literal
import re

from config.secrets import llm_model, llm_api_key
from config import settings
from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *
from pyautogui import confirm


# ------------------------------------------------------------------
# Gemini Client
# ------------------------------------------------------------------

def gemini_create_client():
    """
    Creates and validates Gemini client.
    Returns genai.Client or None
    """
    try:
        if not llm_api_key or "YOUR_API_KEY" in llm_api_key:
            raise ValueError("Gemini API key is missing or invalid")

        print_lg("Configuring Gemini client...")
        client = genai.Client(api_key=llm_api_key)

        # lightweight validation call
        client.models.get(model=llm_model)

        print_lg("---- GEMINI CLIENT CONFIGURED ----")
        print_lg(f"Using model: {llm_model}")
        print_lg("---------------------------------")

        return client

    except Exception as e:
        msg = "Failed to configure Gemini client"
        critical_error_log(msg, e)

        if settings.showAiErrorAlerts:
            if confirm(
                f"{msg}\n{e}",
                "Gemini Error",
                ["Pause AI error alerts", "Continue"]
            ) == "Pause AI error alerts":
                settings.showAiErrorAlerts = False

        return None


# ------------------------------------------------------------------
# Completion
# ------------------------------------------------------------------

def gemini_completion(
    client: genai.Client,
    prompt: str,
    is_json: bool = False
) -> str | dict:
    """
    Calls Gemini for text or JSON completion
    """
    if not client:
        raise ValueError("Gemini client not initialized")

    try:
        print_lg("Calling Gemini API...")

        response = client.models.generate_content(
            model=llm_model,
            contents=prompt
        )

        result = response.text
        if not result:
            raise ValueError("Empty response from Gemini")

        if is_json:
            result = re.sub(r"```json|```", "", result).strip()
            return convert_to_json(result)

        return result

    except Exception as e:
        critical_error_log("Gemini completion failed", e)
        return {"error": str(e)}


# ------------------------------------------------------------------
# Skill Extraction
# ------------------------------------------------------------------

def gemini_extract_skills(
    client: genai.Client,
    job_description: str
) -> dict | list[str]:
    """
    Extracts skills from job description
    """
    try:
        print_lg("Extracting skills using Gemini...")
        prompt = (
            extract_skills_prompt.format(job_description)
            + "\n\nRespond ONLY with valid JSON."
        )

        return gemini_completion(client, prompt, is_json=True)

    except Exception as e:
        critical_error_log("Skill extraction failed", e)
        return {"error": str(e)}


# ------------------------------------------------------------------
# Question Answering
# ------------------------------------------------------------------

def gemini_answer_question(
    client: genai.Client,
    question: str,
    options: list[str] | None = None,
    question_type: Literal[
        "text", "textarea", "single_select", "multiple_select"
    ] = "text",
    job_description: str | None = None,
    about_company: str | None = None,
    user_information_all: str | None = None,
) -> str | dict:
    """
    Answers application questions using Gemini
    """
    try:
        print_lg(f"Answering question: {question}")

        user_info = user_information_all or ""
        prompt = ai_answer_prompt.format(user_info, question)

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

        return gemini_completion(client, prompt)

    except Exception as e:
        critical_error_log("Question answering failed", e)
        return {"error": str(e)}
