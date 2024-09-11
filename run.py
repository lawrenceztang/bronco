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
    problem_statement = example["problem_statement"]
    return run_loop(problem_statement, relevant_code)


def run_loop(problem_statement, relevant_code, num_loops=5):
    patch = ""
    previous_patch = None
    patch_error = None
    for _ in range(num_loops):
        patch = get_patch(problem_statement, relevant_code, previous_patch, patch_error)
        extracted_patch = remove_first_and_last_line(patch)
        result = run_patch(sympy_dir, extracted_patch)
        print(result)
        if result[:5] == "Patch":
            break
        previous_patch = patch
        patch_error = result
    return patch

# Load the dataset
dataset = load_dataset("princeton-nlp/SWE-bench_Lite_oracle")

# Inspect the dataset
sympy_examples = check_for_sympy(dataset)
for example in sympy_examples:
    checkout(sympy_dir, example["base_commit"])
    patch = run_on_oracle_text(example)
    print(run_patch(sympy_dir, patch))
    pass