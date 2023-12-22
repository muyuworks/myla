from typing import Dict, List


def plain_messages(messages: List[Dict], model=None, roles=['user', 'assistant', 'system']):
    text = []
    for m in messages:
        role = m['role']
        if role in roles:
            text.append(f"{role}: {m['content']}")
    return '\n'.join(text)
