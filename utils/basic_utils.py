"""
collection of simple helper functions
"""

import ast
import re

def extract_html_content(text: str, tag: str) -> str:
    pattern = fr'<{tag}.*?>(.*?)</{tag}>'
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else ''


def extract_lists_from_string(s: str):
    try:
        if not isinstance(s, str):
            return []

        # Find all potential list-like substrings using regex
        list_matches = re.findall(r'\[.*?]', s)

        extracted_lists = []
        for match in list_matches:
            try:
                parsed_list = ast.literal_eval(match)
                if isinstance(parsed_list, list):
                    extracted_lists.append(parsed_list)
            except (SyntaxError, ValueError):
                continue  # Skip non-parsable lists

        return extracted_lists if extracted_lists else []

    except Exception:
        return []


