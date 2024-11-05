import os

# Define the directories and files to create
structure = {
    "config": ["config.json"],               # Configuration directory with a blank config file
    "data": ["historical_data.db", "updated_data.db"],  # Data directory with placeholder database files
    "scripts": ["update_database.py", "initialize_database.py"],  # Scripts directory with placeholders
    "notebooks": ["data_analysis.ipynb"],    # Notebooks directory with a placeholder notebook
}

def create_directories_and_files():
    """Create necessary directories and blank files for the project."""
    for directory, files in structure.items():
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Directory '{directory}' created or already exists.")
            
            # Create each file in the directory
            for file in files:
                file_path = os.path.join(directory, file)
                if not os.path.exists(file_path):  # Avoid overwriting existing files
                    with open(file_path, 'w') as f:
                        pass  # Create an empty file
                    print(f"File '{file_path}' created.")
                else:
                    print(f"File '{file_path}' already exists.")

        except Exception as e:
            print(f"Error creating directory or file '{directory}': {e}")

if __name__ == "__main__":
    create_directories_and_files()