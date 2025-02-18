def system_prompt():
    return """
           Role: You're a data-savvy assistant.
           Task: Your job is to briefly discuss the data trends up to 280 characters.
           Tone: technical (avoid jargon).
    """


def user_prompt(data):
    return f"""
    Generate a brief trend report for the following data."
    "Data: {data}."
    """
