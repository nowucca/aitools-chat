import re


def extract_delimited_content(response: str,
                              output_delimiter: str="```",
                              label: str="diff",
                              return_response_on_failure: bool=False) -> str | None:
    """
    Extracts triple backtick from a string.

    Args:
    - s (str): The string to extract diff from.
    - label (str): The label of the triple backtick.

    Returns:
    - str: The extracted content not including the triple backticks or label.
    """

    diff_pattern = re.compile(r'{regex}'.format(regex=(f"{output_delimiter}{label}\n(.*?)\n{output_delimiter}".format(label=label, output_delimiter=output_delimiter))), re.DOTALL)
    match = diff_pattern.search(response)
    if match:
        return match.group(1)
    else:
        return response if return_response_on_failure else None


