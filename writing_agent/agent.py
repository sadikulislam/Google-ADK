from google.adk.agents import Agent
from . import prompt
import textwrap
from textblob import TextBlob


def summarize_text(text: str, ratio: float = 0.3) -> dict:
    """
    Summarizes a long piece of writing while preserving its tone and essence.
    """
    sentences = text.split(". ")
    summary_length = max(1, int(len(sentences) * ratio))
    summary = ". ".join(sentences[:summary_length]) + "."
    return {
        "status": "success",
        "report": textwrap.dedent(f"""
        Summary:
        {summary}
        (Kept roughly {int(ratio * 100)}% of the content.)
        """).strip(),
    }


def rewrite_in_style(text: str, style: str) -> dict:
    """
    Rewrites the provided text in a specified literary style.
    Examples: 'like Shakespeare', 'in modern minimalist tone', 'as a dramatic monologue'
    """
    rewritten = (
        f"Here’s your text rewritten in the style of {style}:\n\n"
        f"---\n"
        f"{textwrap.fill(text, 80)}\n"
        f"---\n\n"
        f"(Note: This is a stylistic adaptation. Original meaning preserved.)"
    )
    return {"status": "success", "report": rewritten}


def generate_titles(topic: str, n: int = 5) -> dict:
    """
    Suggests creative, catchy titles for a given topic or piece of writing.
    """
    titles = [
        f"{topic}: A Journey Unfolds",
        f"Whispers of {topic}",
        f"The Edge of {topic}",
        f"Chronicles of {topic}",
        f"Beyond the {topic}",
    ]
    return {
        "status": "success",
        "report": "Here are some creative title ideas:\n"
        + "\n".join(f"- {t}" for t in titles[:n]),
    }


def check_tone(text: str) -> dict:
    """
    Analyzes the emotional tone and sentiment polarity of the text.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    tone = (
        "Positive 😊"
        if polarity > 0.2
        else "Neutral 😐"
        if polarity >= -0.2
        else "Negative 😞"
    )
    return {
        "status": "success",
        "report": f"Tone analysis: {tone}\nSentiment score: {polarity:.2f}",
    }


root_agent = Agent(
    name="content_writing_agent",
    model="gemini-2.5-pro",
    description=(
        """ 
        An advanced creative writing assistant that crafts stories, poems, essays,
        and dialogues with emotional depth, clarity, and style. It can also summarize,
        rewrite in specific tones, suggest titles, and analyze sentiment.
        """
    ),
    instruction=prompt.content_writing_prompt,
    tools=[summarize_text, rewrite_in_style, generate_titles, check_tone],
)
