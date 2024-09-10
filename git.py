import os
import subprocess


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
        subprocess.run(["git", "checkout", commit], check=True)
        print(f"Checked out {commit} successfully.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred during checkout: {e}")

def patch(repo_path, fix):
    """
    Applies the patch (provided as a string) to the specified local Git repository.

    :param repo_path: The path to the local Git repository.
    :param fix: The string content of the patch file.
    :return: None
    """

    # Navigate to the local Git repository
    os.chdir(repo_path)

    # Write the patch string to a temporary patch file
    patch_file_path = os.path.join(repo_path, "temp_patch.diff")
    with open(patch_file_path, 'w') as patch_file:
        patch_file.write(fix)

    # Apply the patch using `git apply`
    try:
        # Apply the patch
        subprocess.run(["git", "apply", patch_file_path], check=True)
        print("Patch applied successfully.")

        # Optionally clean up the patch file after applying
        os.remove(patch_file_path)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while applying the patch: {e}")