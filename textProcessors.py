import re

def process_markdown(text):
    bold_pattern = re.compile(r'\*\*(.*?)\*\*')
    def replace_bold(match):
        return f"<b> {match.group(1)}</b>"
    # Header patterns
    h1_pattern = re.compile(r'#{1}(.*?)(?=\n|$)')
    h2_pattern = re.compile(r'#{2}(.*?)(?=\n|$)')
    h3_pattern = re.compile(r'#{3}(.*?)(?=\n|$)')
    def replace_h1(match):
        return f"<h1>{match.group(1)}</h1>\n"
    def replace_h2(match):
        return f"<h2>{match.group(1)}</h2>\n"
    def replace_h3(match):
        return f"<h3>{match.group(1)}</h3>\n"
    new_text = re.sub(bold_pattern, replace_bold, text)
    new_text = re.sub(h3_pattern, replace_h3, new_text)
    new_text = re.sub(h2_pattern, replace_h2, new_text)
    new_text = re.sub(h1_pattern, replace_h1, new_text)
    return new_text