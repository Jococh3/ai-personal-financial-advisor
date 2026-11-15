from pathlib import Path

# Load the rules file, one rule per line
path = Path(__file__).resolve().parent.parent / "data" / "rules.txt"
rules = []
for line in path.read_text().splitlines():
    if line.strip():
        rules.append(line.strip())


def find_rules(text, count=3):
    # The words to search for
    words = set()
    for word in text.lower().split():
        words.add(word.strip("?.,!"))

    # Each rule starts with topic words, like "fraud suspicious: ..."
    # Score a rule by how many of its topics appear in our words
    scored = []
    for rule in rules:
        tags = rule.split(":")[0]
        score = 0
        for tag in tags.split():
            if tag in words:
                score += 1
        if score > 0:
            scored.append((score, rule))

    # Return the best matches
    scored.sort(reverse=True)
    best = []
    for score, rule in scored[:count]:
        best.append(rule)
    return best
