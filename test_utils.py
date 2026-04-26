from utils import parse_prompts, parse_rubrics
import os


def test_parse_prompts():
    # Create a dummy prompt file
    with open("test_prompt.md", "w", encoding="utf-8") as f:
        f.write("prompt1->\nHello\n----------------------\nprompt2->\nWorld\n")

    prompts = parse_prompts("test_prompt.md")
    assert prompts[1] == "Hello"
    assert prompts[2] == "World"
    os.remove("test_prompt.md")


def test_parse_rubrics():
    # Create a dummy rubric file
    with open("test_rubric.md", "w", encoding="utf-8") as f:
        f.write("### 2.1 BACKEND_API_SPEC –\n| A | B |\n|---|---|\n| 1 | 2 |\n")

    rubrics = parse_rubrics("test_rubric.md")
    assert "BACKEND_API_SPEC" in rubrics
    assert "| A | B |" in rubrics["BACKEND_API_SPEC"]
    os.remove("test_rubric.md")
