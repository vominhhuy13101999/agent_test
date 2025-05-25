from difflib import Differ

def compare_texts(text1, text2):
    d = Differ()
    diff = list(d.compare(text1.split(), text2.split()))
    changes = [line for line in diff if line.startswith('+ ') or line.startswith('- ')]
    return '\n'.join(changes)
