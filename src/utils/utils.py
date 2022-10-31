import textwrap


def title_wrapper(text: str) -> str:
    split_text = textwrap.wrap(text, 30)
    return "<br>".join(split_text)
