import json
import os


PYTHON_DATA_TYPES_TUTORIAL = """Python Tutorial 1: Data Types in Python

Let's learn Python from the fundamentals, gradually moving toward advanced topics
such as machine learning, deep learning, and generative AI. The examples below use
practical data-processing and data-science scenarios.

1. What are data types?

A data type describes the kind of value a variable refers to and the operations
that are appropriate for that value. Python determines types at runtime; you do
not normally declare a variable's type.

name = "Ilaaf"
age = 29
salary = 31000.50
is_data_scientist = True

Here, name is str, age is int, salary is float, and is_data_scientist is bool.
Use type() to inspect a value:

name = "Ilaaf"
print(type(name))  # <class 'str'>

2. Built-in data types

Numeric: int, float, complex
Text: str
Boolean: bool
Sequences: list, tuple, range
Mapping: dict
Sets: set, frozenset
Binary: bytes, bytearray, memoryview
Special value: None, whose type is NoneType

A. Numeric types

int stores whole numbers, including negative numbers:

age = 29
number_of_employees = 500
temperature = -10
print(type(age))  # <class 'int'>

float stores numbers with a fractional part. Data science uses floats for
measurements, probabilities, model predictions, and statistical calculations:

salary = 31000.50
accuracy = 0.957
print(type(salary))  # <class 'float'>

complex stores a real and an imaginary component:

x = 5 + 3j
print(x)        # (5+3j)
print(type(x))  # <class 'complex'>
print(x.real)   # 5.0
print(x.imag)   # 3.0

B. Text: str

str represents text. Strings may use single quotes, double quotes, or triple
quotes:

name = "Ilaaf"
role = 'Data Scientist'
message = \"\"\"Welcome to Python\"\"\"
print(type(name))  # <class 'str'>

Strings are immutable: you cannot replace an individual character in place.
For example, name[0] = "A" raises TypeError. Create a new string instead:

name = "A" + name[1:]

C. Boolean: bool

bool has two values, True and False. Booleans are often used in conditions:

accuracy = 95
if accuracy > 90:
    print("Model performance is good")
else:
    print("Model needs improvement")

D. Sequence types

Sequences keep values in an order.

list is ordered and mutable (changeable); it allows duplicate values and can
contain values of different types:

skills = ["Python", "SQL", "Machine Learning"]
skills.append("Deep Learning")
print(skills)

tuple is ordered and immutable (not changeable):

coordinates = (10, 20, 30)

Both lists and tuples support indexing starting at zero. Assigning to
coordinates[0] raises TypeError, while assigning to a list item is allowed.

range represents a sequence of integers, commonly used in loops. The stop
value is excluded:

numbers = range(1, 6)
print(list(numbers))  # [1, 2, 3, 4, 5]

E. Mapping: dict

dict stores key-value pairs. Keys are unique; dictionaries are mutable and
preserve insertion order:

employee = {
    "name": "Ilaaf",
    "age": 29,
    "company": "HTC",
    "role": "Data Scientist",
}
print(employee["name"])  # Ilaaf
employee["company"] = "Google"

Dictionaries are useful for structured records and API data, for example:

customer = {
    "customer_id": 101,
    "purchase_amount": 5000.0,
    "is_fraud": False,
}

F. Set types

set is a mutable, unordered collection of unique, hashable values. It removes
duplicates and does not support positional indexing:

numbers = {10, 20, 30, 10, 20}
print(numbers)  # {10, 20, 30} (display order may vary)

frozenset is an immutable set; its elements cannot be added or removed:

fixed_numbers = frozenset([10, 20, 30])

G. Binary types

Binary types represent byte data, useful when working with files, networking,
and multimedia:

data = bytes([65, 66, 67])
print(data)  # b'ABC'

bytes is immutable, bytearray is mutable, and memoryview provides access to
binary data without copying it.

H. NoneType

None represents the absence of a value. Its type is NoneType:

result = None
print(result)       # None
print(type(result)) # <class 'NoneType'>

3. List vs tuple vs set vs dictionary

list:       [value, ...]       ordered, mutable, allows duplicates
tuple:      (value, ...)       ordered, immutable, allows duplicates
set:        {value, ...}       unordered, mutable, unique elements
dictionary: {key: value, ...}  insertion-ordered, mutable, unique keys

Remember: list is a changeable sequence; tuple is a fixed sequence; set keeps
unique elements; dictionary maps keys to values.

4. Checking types dynamically

type() returns an object's type. isinstance() checks whether it has a given type:

x = 100
print(type(x))              # <class 'int'>
print(isinstance(x, int))   # True
print(isinstance(x, str))   # False

5. Practice

For these assignments, identify each value's type:

a = 100
b = 10.5
c = "Python"
d = True
e = [10, 20, 30]
f = (10, 20, 30)
g = {10, 20, 30}
h = {"name": "Ilaaf"}

What happens here?

values = [10, 20, 30]
values[0] = 100  # Works: lists are mutable

fixed_values = (10, 20, 30)
fixed_values[0] = 100  # Raises TypeError: tuples are immutable

6. What to learn next

After data types, study mutability, indexing and slicing, operators,
conditions, loops, collection methods, list comprehensions, functions,
object-oriented programming, exception handling, and then libraries such as
NumPy and Pandas for data science."""


REVIEWED_EXAMPLES = [
    {
        "prompt": "What is Python?",
        "response": (
            "Python is a high-level, dynamically typed programming language with "
            "readable syntax. It supports procedural and object-oriented programming. "
            "The course material highlights its use in data science because libraries "
            "such as NumPy and Pandas support numerical work and data manipulation, "
            "while Matplotlib and Seaborn support visualization."
        ),
    },
    {
        "prompt": "Teach me Python",
        "response": (
            "Python is a readable, high-level programming language used for general "
            "programming and data science. Here are the basics:\n\n"
            "1. Store a value in a variable: name = \"Ada\"\n"
            "2. Use common types: age = 20, price = 3.5, numbers = [1, 2, 3]\n"
            "3. Make a decision: if age >= 18: print(\"adult\")\n"
            "4. Repeat work: for number in numbers: print(number)\n"
            "5. Reuse code with a function: def square(x): return x * x\n\n"
            "Python uses indentation to group statements. It is dynamically typed, "
            "so you do not normally declare a variable's type. Lists can be changed; "
            "tuples are fixed sequences; dictionaries map keys to values. Start by "
            "running small examples and changing them to see what happens."
        ),
    },
    {
        "prompt": "Teach me Python basics",
        "response": (
            "Python is a readable, high-level programming language. Start with "
            "variables (name = \"Ada\"), values such as integers, strings and lists, "
            "and print() to display results. Use if/else to choose what happens, for "
            "to repeat over a sequence, and def to define a reusable function. "
            "Indentation marks the statements inside a block. For example:\n\n"
            "for number in [1, 2, 3]:\n"
            "    print(number * number)\n\n"
            "This loop prints the square of each number. Try changing the list or "
            "the expression."
        ),
    },
    {
        "prompt": "Why is Python used in data science?",
        "response": (
            "Python is popular in data science because it is readable and has a broad "
            "library ecosystem. NumPy and Pandas help with numerical computation and "
            "data manipulation; Matplotlib and Seaborn help visualize data; and "
            "Scikit-learn, TensorFlow, and PyTorch support machine learning."
        ),
    },
    {
        "prompt": "What does dynamically typed mean in Python?",
        "response": (
            "In Python, variable types are determined from the values at runtime, so "
            "you generally do not write a type declaration for every variable. A name "
            "can later refer to a value of another type."
        ),
    },
    {
        "prompt": "What are the data types in Python?",
        "response": PYTHON_DATA_TYPES_TUTORIAL,
    },
    {
        "prompt": "Teach me Python. What are the data types in Python?",
        "response": PYTHON_DATA_TYPES_TUTORIAL,
    },
    {
        "prompt": "Teach me Python: what are the data types?",
        "response": PYTHON_DATA_TYPES_TUTORIAL,
    },
    {
        "prompt": "Name common built-in Python collection types.",
        "response": (
            "Common Python collection types include lists, tuples, ranges, dictionaries, "
            "sets, and frozensets. Lists and tuples are sequence types, dictionaries "
            "store mappings, and sets store distinct elements."
        ),
    },
    {
        "prompt": "What is the difference between a Python list and tuple?",
        "response": (
            "Both lists and tuples are sequence types. A list is mutable, so its "
            "elements can be changed after creation; a tuple is immutable, so its "
            "elements cannot be reassigned. Use a list for a changeable collection and "
            "a tuple for a fixed grouping of values."
        ),
    },
    {
        "prompt": "What is a Python dictionary?",
        "response": (
            "A Python dictionary is a mapping that associates keys with values. It is "
            "useful when values should be looked up by a meaningful key rather than "
            "only by their position."
        ),
    },
    {
        "prompt": "What is a data structure?",
        "response": (
            "A data structure is a way of organizing and storing data so a program can "
            "access and modify it. The choice of structure affects which operations "
            "are convenient and how efficiently they can be performed."
        ),
    },
    {
        "prompt": "What is an algorithm?",
        "response": (
            "An algorithm is a finite, well-defined sequence of effective steps for "
            "solving a problem. It takes input, produces output, and its instructions "
            "must be definite and terminate."
        ),
    },
    {
        "prompt": "What is the difference between an algorithm and a program?",
        "response": (
            "An algorithm is a language-independent plan for solving a problem. A "
            "program is an implementation of that plan in a programming language so a "
            "computer can execute it."
        ),
    },
    {
        "prompt": "What does time complexity describe?",
        "response": (
            "Time complexity describes how the amount of computation required by an "
            "algorithm grows with input size. It is commonly expressed with asymptotic "
            "notation such as Big-O, rather than a particular machine's clock time."
        ),
    },
    {
        "prompt": "Explain Big-O notation.",
        "response": (
            "Big-O notation gives an asymptotic upper bound on a function's growth. "
            "For example, saying an algorithm is O(n squared) means its running-time "
            "growth is bounded above by a constant multiple of n squared for "
            "sufficiently large n."
        ),
    },
    {
        "prompt": "What is the difference between Big-O, Big-Omega, and Big-Theta?",
        "response": (
            "Big-O describes an asymptotic upper bound, Big-Omega describes a lower "
            "bound, and Big-Theta describes a tight bound: both an upper and a lower "
            "bound up to constant factors."
        ),
    },
    {
        "prompt": "What is a database primary key?",
        "response": (
            "A primary key is one or more attributes that uniquely identify each row "
            "in a database table. Entity integrity requires each row to have a valid "
            "primary-key value."
        ),
    },
    {
        "prompt": "What is a foreign key?",
        "response": (
            "A foreign key is an attribute or set of attributes in one table that "
            "references a key in another table. Referential integrity requires the "
            "reference to match an existing key, keeping related records consistent."
        ),
    },
    {
        "prompt": "What is database normalization?",
        "response": (
            "Database normalization organizes relational tables to reduce unnecessary "
            "repetition of data and help avoid inconsistencies when records are "
            "inserted, updated, or deleted."
        ),
    },
    {
        "prompt": "What is data science?",
        "response": (
            "Data science is a multidisciplinary process for extracting useful or "
            "actionable insights from data. It combines mathematics, statistics, "
            "programming, machine learning, and knowledge of the problem domain, and "
            "can work with structured as well as unstructured data."
        ),
    },
    {
        "prompt": "What are the main stages of a data science workflow?",
        "response": (
            "A data science workflow commonly identifies a goal, collects and prepares "
            "data, explores and analyzes it, builds and evaluates a model when "
            "appropriate, and communicates or deploys the results. The process is "
            "iterative, so findings may lead back to earlier steps."
        ),
    },
    {
        "prompt": "What is data cleaning?",
        "response": (
            "Data cleaning identifies and addresses issues such as missing, duplicated, "
            "inconsistent, or incorrectly formatted values so the data is more suitable "
            "for analysis."
        ),
    },
    {
        "prompt": "What is supervised learning?",
        "response": (
            "Supervised learning trains a model using labeled examples, where the "
            "desired outcome is provided for each training case. The learned "
            "relationship can then be used to predict outcomes for new cases."
        ),
    },
    {
        "prompt": "What is unsupervised learning?",
        "response": (
            "Unsupervised learning works with data that has no provided target labels. "
            "It seeks patterns or structure in the data; clustering is a common "
            "example."
        ),
    },
    {
        "prompt": "How do supervised and unsupervised learning differ?",
        "response": (
            "Supervised learning uses labeled examples with known targets to learn "
            "predictions. Unsupervised learning has no target labels and instead looks "
            "for structure or patterns, such as groups, in the available data."
        ),
    },
    {
        "prompt": "What is the difference between classification and regression?",
        "response": (
            "Classification predicts a category or class, such as pass or fail. "
            "Regression predicts a numeric value, such as a measurement or forecast."
        ),
    },
    {
        "prompt": "What is clustering?",
        "response": (
            "Clustering is an unsupervised learning task that groups data points based "
            "on similarity, without using predefined class labels."
        ),
    },
    {
        "prompt": "What is overfitting?",
        "response": (
            "Overfitting occurs when a model fits the training examples too closely, "
            "including their noise, and consequently performs worse on new, unseen "
            "data."
        ),
    },
    {
        "prompt": "Why do we split data into training and validation sets?",
        "response": (
            "The training set is used to fit a model. A separate validation set helps "
            "estimate how well it generalizes and compare choices such as model "
            "settings without evaluating only on the data it learned from."
        ),
    },
    {
        "prompt": "What is the K-nearest neighbors algorithm?",
        "response": (
            "K-nearest neighbors (KNN) predicts for a new example using the labels or "
            "values of its K closest training examples. Feature scales matter because "
            "large-valued features can dominate distance calculations, so scaling may "
            "be needed."
        ),
    },
    {
        "prompt": "Why is feature normalization useful in KNN?",
        "response": (
            "KNN compares examples using distances. If features have very different "
            "scales, a large-scale feature can dominate the distance and hide the "
            "influence of smaller-scale features. Normalization brings features to "
            "comparable scales."
        ),
    },
    {
        "prompt": "What is artificial intelligence?",
        "response": (
            "Artificial intelligence (AI) is the field of building computer systems "
            "that perform tasks associated with intelligent behavior, such as "
            "reasoning, perception, language understanding, or decision-making."
        ),
    },
    {
        "prompt": "What is machine learning?",
        "response": (
            "Machine learning is an approach in which a computer model learns patterns "
            "from data to make predictions or decisions, rather than being given "
            "hand-written rules for every case."
        ),
    },
    {
        "prompt": "How are artificial intelligence and machine learning related?",
        "response": (
            "Machine learning is a set of methods for learning from data and is commonly "
            "used to build AI systems. AI is the broader goal or field; not every AI "
            "approach has to use machine learning."
        ),
    },
    {
        "prompt": "What is data visualization?",
        "response": (
            "Data visualization represents data graphically so people can inspect "
            "patterns, comparisons, and relationships. Python libraries used for "
            "visualization include Matplotlib and Seaborn."
        ),
    },
    {
        "prompt": "What is a relational database?",
        "response": (
            "A relational database organizes data into tables made of rows and columns. "
            "Keys can identify rows and express relationships between tables."
        ),
    },
    {
        "prompt": "What is the difference between a stack and a queue?",
        "response": (
            "A stack removes the most recently added item first (last in, first out). "
            "A queue removes the item that has been waiting longest (first in, first "
            "out)."
        ),
    },
    {
        "prompt": "What is object-oriented programming?",
        "response": (
            "Object-oriented programming organizes software around objects that combine "
            "state and behavior. Classes define the structure and behavior from which "
            "objects are created."
        ),
    },
    {
        "prompt": "What is cloud computing?",
        "response": (
            "Cloud computing provides computing resources, such as servers, storage, "
            "or software, over a network on demand instead of requiring users to manage "
            "all of the underlying infrastructure themselves."
        ),
    },
    {
        "prompt": "What is software engineering?",
        "response": (
            "Software engineering applies systematic methods to the specification, "
            "design, development, testing, deployment, and maintenance of software."
        ),
    },
    {
        "prompt": "Hi",
        "response": "Hello! What would you like to study?",
    },
    {
        "prompt": "Hello",
        "response": "Hello! What would you like to study?",
    },
    {
        "prompt": "How are you doing?",
        "response": (
            "I'm doing well, thanks for asking! I'm here and ready to help with "
            "your studies. How are you doing?"
        ),
    },
    {
        "prompt": "Who are you?",
        "response": (
            "I am GYANTRA, your private AI learning companion. I can help explain "
            "topics from your local MCA and MSc course materials."
        ),
    },
    {
        "prompt": "Hey",
        "response": "Hi! What would you like to study or work on today?",
    },
    {
        "prompt": "Good morning",
        "response": "Good morning! What would you like to learn about today?",
    },
    {
        "prompt": "Good afternoon",
        "response": "Good afternoon! What can I help you study today?",
    },
    {
        "prompt": "Good evening",
        "response": "Good evening! What would you like to work on?",
    },
    {
        "prompt": "I am doing great",
        "response": "Glad to hear it! What would you like to study or work on today?",
    },
    {
        "prompt": "I am doing well",
        "response": "That's good to hear! What can I help you with today?",
    },
    {
        "prompt": "I am fine",
        "response": "Good to hear! What would you like to study today?",
    },
    {
        "prompt": "Not really, I am having a hard day",
        "response": (
            "I'm sorry it's been a hard day. We can take things one step at a time. "
            "Would you like to talk about a study topic or try a small task?"
        ),
    },
    {
        "prompt": "Thank you",
        "response": "You're welcome! Let me know if you'd like to explore anything else.",
    },
    {
        "prompt": "Thanks",
        "response": "You're welcome! What else can I help you with?",
    },
    {
        "prompt": "Thanks for your help",
        "response": "You're very welcome. I'm glad I could help!",
    },
    {
        "prompt": "That was helpful",
        "response": "I'm glad it helped! Would you like an example or to explore another topic?",
    },
    {
        "prompt": "What can you do?",
        "response": (
            "I can help explain study topics, give examples, and work through "
            "questions step by step. Tell me the subject or question you'd like "
            "to start with."
        ),
    },
    {
        "prompt": "Can you help me?",
        "response": "Of course! Tell me what you're working on, and we'll take it step by step.",
    },
    {
        "prompt": "Can you explain this in simple words?",
        "response": (
            "Sure. Tell me the topic or paste the part you'd like explained, and "
            "I'll use simpler language."
        ),
    },
    {
        "prompt": "Can you give me an example?",
        "response": "Sure—what topic would you like an example for?",
    },
    {
        "prompt": "I don't understand",
        "response": (
            "That's okay. Which part or topic is confusing? I'll try a different "
            "explanation and break it into smaller steps."
        ),
    },
    {
        "prompt": "Please repeat that",
        "response": "Of course. Which part would you like me to repeat?",
    },
    {
        "prompt": "Can you quiz me?",
        "response": "Sure! What subject or topic should I quiz you on?",
    },
    {
        "prompt": "Let's study",
        "response": "Sounds good! What subject or topic would you like to study?",
    },
    {
        "prompt": "I'm confused",
        "response": (
            "No problem—we can slow down. Tell me which topic or step is confusing, "
            "and I'll explain it another way."
        ),
    },
    {
        "prompt": "Sorry",
        "response": "No need to apologize. What would you like help with?",
    },
    {
        "prompt": "I made a mistake",
        "response": "That's all right; mistakes are part of learning. What would you like to check?",
    },
    {
        "prompt": "That answer seems wrong",
        "response": (
            "Thanks for pointing that out. Tell me which part seems wrong or share "
            "the relevant course passage, and I'll review it carefully."
        ),
    },
    {
        "prompt": "Can you help with my homework?",
        "response": (
            "Yes. Share the question and what you've tried so far. I can explain "
            "the concepts and help you work toward a solution."
        ),
    },
    {
        "prompt": "I don't know what to study",
        "response": (
            "We can choose a starting point together. What course or subject are "
            "you taking, and what topics have you covered recently?"
        ),
    },
    {
        "prompt": "Goodbye",
        "response": "Goodbye! Good luck with your studies. Come back whenever you'd like to continue.",
    },
    {
        "prompt": "Bye",
        "response": "Bye! Take care, and good luck with your studies.",
    },
    {
        "prompt": "See you later",
        "response": "See you later! I'll be here when you're ready to study again.",
    },
    {
        "prompt": "Good night",
        "response": "Good night! Rest well, and good luck with your studies tomorrow.",
    },
    {
        "prompt": "Are you a real person?",
        "response": (
            "I'm an AI assistant, not a person. I can still help explain topics "
            "and practice study questions."
        ),
    },
    {
        "prompt": "Where did you get that answer?",
        "response": (
            "I generate answers from my training and the information available in "
            "this chat. I don't currently search your course PDFs while answering, "
            "so please check important details against your course material."
        ),
    },
    {
        "prompt": "Can you summarize something for me?",
        "response": "Yes. Paste the text or tell me the topic you'd like summarized.",
    },
    {
        "prompt": "Can you explain it step by step?",
        "response": "Absolutely. Tell me the topic or share the problem, and I'll break it into steps.",
    },
]


def extract_qa_from_corpus(
    corpus_path="data/corpus.txt",
    output_json="data/instructions.json",
):
    if not os.path.isfile(corpus_path):
        raise FileNotFoundError(f"Course corpus not found: {corpus_path}")

    os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as output_file:
        json.dump(REVIEWED_EXAMPLES, output_file, indent=2, ensure_ascii=False)

    print(
        f"Saved {len(REVIEWED_EXAMPLES)} reviewed course Q&A examples to "
        f"'{output_json}'."
    )


if __name__ == "__main__":
    extract_qa_from_corpus()
