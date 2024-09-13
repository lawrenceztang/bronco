from datasets import load_dataset
from gpt import *
from tools import *
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

def get_test_files_from_code(code):
    out = []
    for file in code:
        if file[0][-2:] == "py":
            directory, filename = os.path.split(file[0])
            name, ext = os.path.splitext(filename)
            test_directory = os.path.join(directory, 'tests')
            test_filename = f"test_{name}.py"
            test_file_path = os.path.join(test_directory, test_filename)

            full_path = os.path.join(sympy_dir, test_file_path)

            if os.path.exists(full_path):
                with open(full_path, 'r') as file:
                    content = file.read()
                    out.append((test_file_path, content))
    return out


def run_loop(problem_statement, relevant_code, num_loops=5):
    new_files = None
    test_files = get_test_files_from_code(relevant_code)
    test_result = None
    new_test_files = None
    for _ in range(num_loops):
        new_files, reasoning = get_new_code(problem_statement, relevant_code, new_files, test_result)
        new_files = [(n[0], remove_first_and_last_line(n[1])) for n in new_files]
        replace_new_files(sympy_dir, new_files)

        #Iterate on test files
        for _ in range(3):
            new_test_files = get_new_test_code(problem_statement, new_files, test_files, new_test_files, test_result)
            new_test_files = [(n[0], remove_first_and_last_line(n[1])) for n in new_test_files]
            replace_new_files(sympy_dir, new_test_files)
            test_result = run_specific_tests(sympy_dir, [n[0] for n in new_test_files], "python39")
            print("Test results: ", test_result)

        if test_result[:5] == "Tests":
            return new_files, new_test_files

    return new_files, new_test_files

# Load the dataset
dataset = load_dataset("princeton-nlp/SWE-bench_Lite_oracle")

# Inspect the dataset
sympy_examples = check_for_sympy(dataset)
for example in sympy_examples[3:]:
    checkout(sympy_dir, example["base_commit"])
    new_files, new_test_files = run_on_oracle_text(example)