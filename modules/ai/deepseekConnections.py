from typing import Literal
from openai import OpenAI
from pyautogui import confirm

from config.secrets import *
from config import settings
from modules.helpers import print_lg, critical_error_log, convert_to_json
from modules.ai.prompts import *


# ------------------------------------------------------------------
# Client
# ------------------------------------------------------------------

def deepseek_create_client() -> OpenAI | None:
    """
    Creates a DeepSeek client using OpenAI-compatible API.
    """
    try:
        if not use_AI:
            raise ValueError("AI is disabled (use_AI=False in secrets.py)")

        if not llm_api_key or "YOUR_API_KEY" in llm_api_key:
            raise ValueError("Invalid or missing API key")

        base_url = llm_api_url.rstrip("/")

        print_lg("Creating DeepSeek client...")
        client = OpenAI(
            api_key=llm_api_key,
            base_url=base_url
        )

        # Lightweight validation
        client.models.list()

        print_lg("---- DEEPSEEK CLIENT READY ----")
        print_lg(f"API URL : {base_url}")
        print_lg(f"Model   : {llm_model}")
        print_lg("--------------------------------")

        return client

    except Exception as e:
        msg = "Failed to create DeepSeek client"
        critical_error_log(msg, e)

        if settings.showAiErrorAlerts:
            if confirm(
                f"{msg}\n{e}",
                "DeepSeek Error",
                ["Pause AI error alerts", "Continue"]
            ) == "Pause AI error alerts":
                settings.showAiErrorAlerts = False

        return None


# ------------------------------------------------------------------
# Completion
# ------------------------------------------------------------------

def deepseek_completion(
    client: OpenAI,
    messages: list[dict],
    response_format: dict | None = None,
    temperature: float = 0.0,
    stream: bool = stream_output
) -> str | dict:
    """
    Executes a DeepSeek chat completion.
    """
    if not client:
        raise ValueError("DeepSeek client not initialized")

    try:
        params = {
            "model": llm_model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }

        if response_format:
            params["response_format"] = response_format

        print_lg("Calling DeepSeek API...")
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
            raise ValueError("Empty response from DeepSeek")

        if response_format:
            return convert_to_json(result)

        return result

    except Exception as e:
        critical_error_log("DeepSeek completion failed", e)
        raise ValueError(f"DeepSeek API error: {e}")


# ------------------------------------------------------------------
# Skill Extraction
# ------------------------------------------------------------------

def deepseek_extract_skills(
    client: OpenAI,
    job_description: str,
    stream: bool = stream_output
) -> dict:
    """
    Extracts skills from a job description.
    """
    try:
        print_lg("Extracting skills using DeepSeek...")

        prompt = deepseek_extract_skills_prompt.format(job_description)
        messages = [{"role": "user", "content": prompt}]

        return deepseek_completion(
            client=client,
            messages=messages,
            response_format={"type": "json_object"},
            stream=stream
        )

    except Exception as e:
        critical_error_log("Skill extraction failed", e)
        return {"error": str(e)}


# ------------------------------------------------------------------
# Question Answering
# ------------------------------------------------------------------

def deepseek_answer_question(
    client: OpenAI,
    question: str,
    options: list[str] | None = None,
    question_type: Literal[
        "text", "textarea", "single_select", "multiple_select"
    ] = "text",
    job_description: str | None = None,
    about_company: str | None = None,
    user_information_all: str | None = None,
    stream: bool = stream_output
) -> str | dict:
    """
    Answers application questions using DeepSeek.
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

        messages = [{"role": "user", "content": prompt}]

        return deepseek_completion(
            client=client,
            messages=messages,
            temperature=0.1,
            stream=stream
        )

    except Exception as e:
        critical_error_log("Question answering failed", e)
        return {"error": str(e)}
