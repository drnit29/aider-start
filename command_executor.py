import shutil
import subprocess

def check_aider_path():
    """
    Checks if the 'aider' command is available in the system's PATH.

    Returns:
        str: The path to the 'aider' executable if found, None otherwise.
    """
    return shutil.which("aider")

def execute_aider_command(parameters_string):
    """
    Constructs and executes the 'aider' command with the given parameters.

    Args:
        parameters_string (str): A string of parameters to pass to aider.

    Returns:
        None
    """
    aider_path = check_aider_path()
    if not aider_path:
        print("Error: aider executable not found in PATH. Cannot execute command.")
        return

    command = f"{aider_path} {parameters_string}"
    print(f"Executing command: {command}")

    try:
        # Using subprocess.run with shell=True for direct execution in the user's terminal context.
        # This allows for interactive use as specified.
        # For more controlled execution, especially if parameters_string could be untrusted,
        # shell=False and passing command as a list (e.g., [aider_path] + parameters_string.split())
        # would be safer, but might behave differently regarding shell features.
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Stream output for interactive feel
        for stdout_line in iter(process.stdout.readline, ""):
            print(stdout_line, end="")
        process.stdout.close()

        # Wait for command to complete and capture return code
        return_code = process.wait()

        if return_code != 0:
            print(f"\naider command exited with error code: {return_code}")
            # Print any stderr output
            for stderr_line in iter(process.stderr.readline, ""):
                print(f"Error: {stderr_line}", end="")
            process.stderr.close()
        else:
            print("\naider command executed successfully.")

    except FileNotFoundError:
        # This case should ideally be caught by check_aider_path, but as a fallback.
        print(f"Error: The command '{aider_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while trying to execute the aider command: {e}")

if __name__ == '__main__':
    aider_path = check_aider_path()
    if aider_path:
        print(f"aider executable found at: {aider_path}")
        # Example usage of execute_aider_command:
        print("\n--- Example: Executing 'aider --help' ---")
        execute_aider_command("--help")
        # print("\n--- Example: Executing 'aider --model gpt-4o --message \"Test message\"' ---")
        # execute_aider_command("--model gpt-4o --message 'Test message from command_executor'")
    else:
        print("aider executable not found in PATH. Cannot run examples.")