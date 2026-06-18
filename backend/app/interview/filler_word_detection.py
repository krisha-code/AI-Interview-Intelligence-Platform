def detect_filler_words(transcript):

    filler_words = [
        "um",
        "uh",
        "like",
        "you know",
        "actually",
        "basically",
        "literally",
        "kind of",
        "sort of"
    ]

    transcript = transcript.lower()

    filler_count = 0

    for word in filler_words:
        filler_count += transcript.count(word)

    return filler_count

def filler_score(filler_count):

    if filler_count <= 2:
        return 100

    elif filler_count <= 5:
        return 80

    elif filler_count <= 10:
        return 60

    else:
        return 40