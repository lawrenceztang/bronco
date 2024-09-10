from datasets import load_dataset
from gpt import *
from git import *

sympy_dir = "/Users/lawrencetang/Documents/python/sympy"

def check_for_sympy(dataset):
    matches = []
    for i, entry in enumerate(dataset['test']):  # Adjust split if needed
        # Check if the 'repo' field contains 'sympy'
        if 'sympy' in entry["repo"]:
            matches.append(entry)
    return matches

def run_algo(example):
    return get_fix(example["text"] + "\n\n\n")


# Load the dataset
dataset = load_dataset("princeton-nlp/SWE-bench_Lite_oracle")

# Inspect the dataset
sympy_examples = check_for_sympy(dataset)
for example in sympy_examples:
    checkout(sympy_dir, example["base_commit"])
    fix = run_algo(example)
    patch(sympy_dir, fix)
    pass

