from datasets import load_dataset
from gpt import *
from git import *
import re

sympy_dir = "/Users/lawrencetang/Documents/python/sympy"

def check_for_sympy(dataset):
    matches = []
    for i, entry in enumerate(dataset['test']):  # Adjust split if needed
        # Check if the 'repo' field contains 'sympy'
        if 'sympy' in entry["repo"]:
            matches.append(entry)
    return matches

def run_on_oracle_text(example):
    matches = re.findall(r'<code>(.*?)</code>', example["text"], re.DOTALL)
    relevant_code = ' '.join(matches)
    relevant_code = extract_blocks(relevant_code)
    problem_statement = example["problem_statement"]
    return run_loop(problem_statement, relevant_code)


def extract_blocks(content):
    # Regular expression pattern to match text between any start and end markers with file names
    pattern = re.compile(r'\[start of (.*?)\](.*?)\[end of \1\]', re.DOTALL)

    # Find all matches (the file name and the corresponding block)
    blocks = pattern.findall(content)

    # Return the extracted blocks as a list of tuples (file name, block content)
    return blocks

def run_loop(problem_statement, relevant_code, num_loops=5):
    return get_new_code(problem_statement, relevant_code)


# Load the dataset
dataset = load_dataset("princeton-nlp/SWE-bench_Lite_oracle")

# Inspect the dataset
sympy_examples = check_for_sympy(dataset)
for example in sympy_examples:
    checkout(sympy_dir, example["base_commit"])
    new_files = run_on_oracle_text(example)
    new_files = [(n[0], remove_first_and_last_line(n[1])) for n in new_files]
    replace_new_files(sympy_dir, new_files)