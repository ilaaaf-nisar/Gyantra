import json
import math
import re
from pathlib import Path


SOURCE_MARKER = re.compile(r"===\s*SOURCE\s*:", re.IGNORECASE)
NON_WORD = re.compile(r"[^\w\s]", re.UNICODE)
WHITESPACE = re.compile(r"\s+")
QUESTION_FILLER_WORDS = {
    "a", "an", "and", "are", "about", "be", "between", "can", "could",
    "describe", "does", "for", "give", "how", "i", "in", "is", "it",
    "me", "of", "please", "the", "this", "to", "tell", "what", "when",
    "where", "which", "who", "why", "will", "with", "would",
}
MIN_MATCH_SCORE = 0.72
MIN_SHARED_TERMS = 1
SMALL_TALK_QUESTIONS = {
    "how are you",
    "how are you doing",
    "how s it going",
    "how is it going",
    "how are things",
    "what s up",
    "what is up",
}


def normalize_question(question):
    normalized = NON_WORD.sub(" ", question.casefold())
    normalized = re.sub(r"\bi m\b", "i am", normalized)
    return WHITESPACE.sub(" ", normalized).strip()


def _content_words(question):
    words = set()
    for word in normalize_question(question).split():
        if word in QUESTION_FILLER_WORDS:
            continue
        if len(word) > 4 and word.endswith("ies"):
            word = f"{word[:-3]}y"
        elif len(word) > 5 and word.endswith(("ches", "shes", "xes", "zes")):
            word = word[:-2]
        elif len(word) > 4 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
            word = word[:-1]
        words.add(word)
    return words


def _best_semantic_match(question, answers):
    question_words = _content_words(question)
    if len(question_words) < MIN_SHARED_TERMS:
        return None

    prompt_words = {
        prompt: _content_words(prompt)
        for prompt in answers
    }
    document_frequencies = {}
    for words in prompt_words.values():
        for word in words:
            document_frequencies[word] = document_frequencies.get(word, 0) + 1

    prompt_count = len(prompt_words)
    weights = {
        word: math.log((prompt_count + 1) / (frequency + 1)) + 1
        for word, frequency in document_frequencies.items()
    }
    question_weight = sum(weights.get(word, 1) for word in question_words)
    ranked_matches = []
    for prompt, words in prompt_words.items():
        shared_words = question_words & words
        if len(shared_words) < MIN_SHARED_TERMS:
            continue

        shared_weight = sum(weights.get(word, 1) for word in shared_words)
        prompt_weight = sum(weights.get(word, 1) for word in words)
        score = 2 * shared_weight / (question_weight + prompt_weight)
        ranked_matches.append((score, prompt))

    ranked_matches.sort(reverse=True)
    if not ranked_matches or ranked_matches[0][0] < MIN_MATCH_SCORE:
        return None
    if len(ranked_matches) > 1 and ranked_matches[0][0] - ranked_matches[1][0] < 0.08:
        return None
    return answers[ranked_matches[0][1]]


def load_reviewed_answers(path="data/instructions.json"):
    with Path(path).open("r", encoding="utf-8") as examples_file:
        examples = json.load(examples_file)
    if not isinstance(examples, list):
        raise ValueError(f"{path} must contain a JSON list of prompt/response pairs.")

    answers = {}
    for example in examples:
        if not isinstance(example, dict):
            continue
        prompt = example.get("prompt")
        response = example.get("response")
        if (
            isinstance(prompt, str)
            and isinstance(response, str)
            and prompt.strip()
            and response.strip()
            and not SOURCE_MARKER.search(response)
        ):
            answers[normalize_question(prompt)] = response.strip()
    return answers


def find_reviewed_answer(question, answers):
    normalized = normalize_question(question)
    answer = answers.get(normalized)
    if answer is not None:
        return answer

    small_talk_question = normalized
    for greeting in ("hello", "hi", "hey"):
        if small_talk_question.startswith(f"{greeting} "):
            small_talk_question = small_talk_question[len(greeting) + 1:]
            break
    if small_talk_question in SMALL_TALK_QUESTIONS:
        return answers.get(normalize_question("How are you doing?"))

    words = set(normalized.split())
    asks_about_types = (
        "data type" in normalized
        or "data types" in normalized
        or "built in type" in normalized
        or "built in types" in normalized
    )
    if "python" in words and asks_about_types:
        return answers.get(normalize_question("What are the data types in Python?"))

    teaching_intent = {
        "beginner", "basics", "beginning", "explain", "learn", "lesson",
        "start", "starting", "teach",
    }
    if "python" in words and words.intersection(teaching_intent):
        answer = answers.get(normalize_question("Teach me Python"))
        if answer is not None:
            return answer

    return _best_semantic_match(question, answers)
