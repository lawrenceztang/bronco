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