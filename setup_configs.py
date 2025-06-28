import json
import string
import subprocess
import os
import shutil

# Load config tool data from JSON file
with open("tools.json", "r") as f:
    tools = json.load(f)

# Convert dict to list of tuples for ordering
tool_list = list(tools.items())

# Create alphabet labels: a, b, c, ...
labels = list(string.ascii_lowercase[:len(tool_list)])

# Display menu
print("Available tool configs:\n")
for label, (tool_name, _) in zip(labels, tool_list):
    print(f"  {label}) {tool_name}")

print("\nSelect which configs to set up (e.g., 'ab' for first two, 'z' for all):")
selection = input("> ").strip().lower()

# Handle full selection
if selection == 'z':
    selected_tools = tool_list
else:
    selected_tools = []
    for char in selection:
        if char in labels:
            index = labels.index(char)
            selected_tools.append(tool_list[index])
        else:
            print(f"Invalid option: '{char}'")

# Prepare for setup
log_file = "config_setup_errors.log"
log_dir = os.path.dirname(log_file)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)

print("\nSetting up selected tool configs...\n")

with open(log_file, "w") as log:
    for tool_name, cmd in selected_tools:
        print(f"Setting up config for {tool_name}...")
        
        # Try to detect config destination path from the last part of the command
        if "~/.config" in cmd:
            split_cmd = cmd.split()
            try:
                target_path = split_cmd[-1].replace("~", os.path.expanduser("~"))
                if os.path.exists(target_path):
                    choice = input(f"  Config at '{target_path}' already exists. [s]kip / [r]eplace? ").strip().lower()
                    if choice == 's':
                        print("  Skipped.\n")
                        continue
                    elif choice == 'r':
                        shutil.rmtree(target_path)
                        print("  Removed existing config.")
                    else:
                        print("  Invalid choice. Skipping.\n")
                        continue
            except Exception as e:
                log.write(f"[{tool_name} - PATH DETECTION FAILED]\nCommand: {cmd}\nError: {str(e)}\n\n")

        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"  Config for {tool_name} set up successfully.\n")
        except subprocess.CalledProcessError as e:
            print(f"  Failed to set up {tool_name}.\n")
            log.write(f"[{tool_name}]\nCommand: {cmd}\nError Code: {e.returncode}\n\n")

print("Config setup process complete.")
print(f"Any errors were logged to '{log_file}'.")
