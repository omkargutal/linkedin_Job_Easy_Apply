##> Shared Response Definitions
array_of_strings = {"type": "array", "items": {"type": "string"}}
"""
Schema representing an array of strings, e.g. ["item1", "item2"]
"""
#<


##> Skill Extraction

# Message format = [{"role": "user", "content": extract_skills_prompt}]

extract_skills_prompt = """
You are an AI system that extracts and categorizes skills from a job description.
Identify all mentioned skills and organize them into the following five groups:

1. "tech_stack": Programming languages, frameworks, libraries, databases, and development tools
   (e.g., Python, SQL, ETL, Power BI, Spark, Research).
2. "technical_skills": Broader technical competencies or domains
   (e.g., System Design, Data Engineering, Microservices, Distributed Systems).
3. "other_skills": Soft skills and non-technical abilities
   (e.g., Communication, Leadership, Cross-functional collaboration).
4. "required_skills": Skills explicitly stated as mandatory or expected.
5. "nice_to_have": Skills listed as optional, preferred, or advantageous.

Return ONLY a valid JSON object in the exact format below, without any additional text:
{{
    "tech_stack": [],
    "technical_skills": [],
    "other_skills": [],
    "required_skills": [],
    "nice_to_have": []
}}

JOB DESCRIPTION:
{}
"""
"""
Insert the job description using `extract_skills_prompt.format(job_description)`
"""

# DeepSeek-optimized prompt (JSON-only output, no schema enforcement)
deepseek_extract_skills_prompt = """
You are an AI system that extracts and categorizes skills from a job description.
Identify all mentioned skills and organize them into the following five groups:

1. "tech_stack": Programming languages, frameworks, libraries, databases, and development tools.
2. "technical_skills": Broader technical competencies or engineering domains.
3. "other_skills": Soft skills and non-technical abilities.
4. "required_skills": Skills explicitly marked as mandatory or expected.
5. "nice_to_have": Skills listed as optional or preferred.

IMPORTANT:
- Return ONLY a valid JSON object in the exact structure shown below.
- Do NOT include explanations, comments, or extra text.
- Each field must be an array of strings (empty if none).

{{
    "tech_stack": ["Example Skill"],
    "technical_skills": ["Example Skill"],
    "other_skills": ["Example Skill"],
    "required_skills": ["Example Skill"],
    "nice_to_have": ["Example Skill"]
}}

JOB DESCRIPTION:
{}
"""
"""
Use `deepseek_extract_skills_prompt.format(job_description)` to inject the job description
"""


extract_skills_response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "Skills_Extraction_Response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "tech_stack": array_of_strings,
                "technical_skills": array_of_strings,
                "other_skills": array_of_strings,
                "required_skills": array_of_strings,
                "nice_to_have": array_of_strings,
            },
            "required": [
                "tech_stack",
                "technical_skills",
                "other_skills",
                "required_skills",
                "nice_to_have",
            ],
            "additionalProperties": False
        },
    },
}
"""
JSON schema for the skill extraction response
"""
#<


##> ------ Dheeraj Deshwal Feature ------
##> Form Question Answering

# Message format = [{"role": "user", "content": ai_answer_prompt}]

ai_answer_prompt = """
You are an AI assistant completing form responses in a natural, human-like manner.
Follow these rules strictly:

1. If the question asks for years of experience, duration, or any numeric value, return ONLY the number.
2. If the question is a Yes/No question, return ONLY "Yes" or "No".
3. If a brief explanation is required, respond with a single concise sentence.
4. If a detailed answer is required, provide a structured and human-like response within 350 characters.
5. Do NOT repeat or restate the question.
6. Use the provided user information when relevant.

USER INFORMATION:
{}

QUESTION:
{}
"""

