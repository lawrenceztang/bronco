import os
import subprocess
import tempfile

def checkout(dir, commit):
    """
    Checks out a specific commit or branch in the given local Git repository.

    :param dir: The path to the local Git repository.
    :param commit: The commit hash or branch name to check out.
    :return: None
    """

    # Change the working directory to the repository
    os.chdir(dir)

    try:
        # Run git checkout with the specified commit or branch
        subprocess.run(["git", "checkout", "-f", commit], check=True)
        print(f"Checked out {commit} successfully.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during checkout: {e}")


def run_patch(repo_path, fix):
    if not os.path.isdir(repo_path):
        return "Error: The specified repository path is not valid."

    try:
        os.chdir(repo_path)
    except OSError as e:
        return f"Error: Failed to change directory to {repo_path}. {e}"

    try:
        with tempfile.NamedTemporaryFile('w+', delete=False) as temp_patch_file:
            temp_patch_file.write(fix)
            temp_patch_file.flush()  # Make sure all content is written

            # Store the temporary file path
            temp_patch_file_path = temp_patch_file.name
    except Exception as e:
        return f"Error: Failed to create temporary patch file. {e}"

    try:
        result = subprocess.run(['patch', '-p1', '-i', temp_patch_file_path], capture_output=True, text=True)

        if result.returncode == 0:
            return "Patch applied successfully:\n" + result.stdout
        else:
            return "Error applying patch:\n" + result.stderr
    except Exception as e:
        return f"Error: {e}"
    finally:
        # Clean up the temporary patch file
        os.remove(temp_patch_file_path)


def replace_new_files(sympy_dir, new_files):
    """
    Replaces or creates files in the sympy_dir with the content from new_files.

    Args:
    sympy_dir (str): The directory where the files should be replaced or created.
    new_files (list of tuples): Each tuple contains (file_name, file_text).
                                - file_name: Relative file path (str)
                                - file_text: Text content of the file (str)

    Returns:
    None
    """
    # Ensure the sympy_dir exists
    if not os.path.isdir(sympy_dir):
        raise ValueError(f"The directory {sympy_dir} does not exist.")

    for file_name, file_text in new_files:
        # Get the full path to the file
        file_path = os.path.join(sympy_dir, file_name)

        # Ensure the directory for the file exists
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir, exist_ok=True)  # Create directories if they don't exist

        # Write the file content
        with open(file_path, 'w') as file:
            file.write(file_text)

        print(f"Replaced/Created file: {file_path}")
