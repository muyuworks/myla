from typing import Dict, List

def plain_messages(messages: List[Dict], model=None):
    text = []
    for m in messages:
        role = m['role']
        text.append(f"{role}: {m['content']}")
    return '\n'.join(text)