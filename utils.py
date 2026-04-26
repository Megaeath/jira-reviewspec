import re


def parse_prompts(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    prompts = {}
    # Match patterns like prompt1-> ... ----------------------
    # Or prompt1-> ... ``
    sections = re.split(r"-{10,}|`{2,}", content)
    for section in sections:
        match = re.search(r"prompt(\d+)->\s*(.*)", section, re.DOTALL)
        if match:
            prompts[int(match.group(1))] = match.group(2).strip()
    return prompts


def parse_rubrics(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    rubrics = {}
    # Find headers like ### 2.1 BACKEND_API_SPEC
    # Then find the table below it
    sections = re.split(r"###\s*2\.\d+\s*", content)
    for section in sections:
        header_match = re.match(r"([A-Z_]+)\s*–", section)
        if header_match:
            doc_type = header_match.group(1).strip()
            # Find the first table in this section
            table_match = re.search(r"\|.*\|.*\n\|.*\|.*\n(\|.*\|.*\n)+", section)
            if table_match:
                rubrics[doc_type] = table_match.group(0).strip()
    return rubrics
