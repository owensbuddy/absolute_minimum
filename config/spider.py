import os

def generate_tree(path, file, max_files=20, prefix='', ignore_list=None):
    # Define the ignore list for irrelevant files and directories
    if ignore_list is None:
        ignore_list = ['.venv', '.git', '.DS_Store', '__pycache__']  # Add more as needed
    
    items = os.listdir(path)
    
    # Filter out ignored items
    items = [item for item in items if item not in ignore_list]
    
    # Separate directories and files
    directories = sorted([item for item in items if os.path.isdir(os.path.join(path, item))])
    files = sorted([item for item in items if os.path.isfile(os.path.join(path, item))])
    
    # Write and print directories first
    for directory in directories:
        line = f"{prefix}{directory}\n"
        file.write(line)
        print(line, end='')  # Print to terminal without an extra newline
        # Recursively call for subdirectory, increase prefix with a tab
        generate_tree(os.path.join(path, directory), file, max_files, prefix + '\t', ignore_list)
    
    # Limit number of files and write/print them
    for file_name in files[:max_files]:
        line = f"{prefix}{file_name}\n"
        file.write(line)
        print(line, end='')  # Print to terminal without an extra newline

if __name__ == "__main__":
    # Starting directory path
    base_path = "/Users/buddy/Desktop/School/effective-adventure/effective-adventure"
    output_file_path = "/Users/buddy/Desktop/School/effective-adventure/effective-adventure/data/dir_tree.txt"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    # Open the output file in write mode
    with open(output_file_path, 'w') as file:
        root_line = f"{base_path}\n"
        file.write(root_line)
        print(root_line, end='')  # Print the root directory to terminal
        generate_tree(base_path, file)