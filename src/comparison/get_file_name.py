import os

def get_files_in_data_folder():
    # Specify the path to your data folder
    data_folder = "data"
    
    # Get list of all files in the data folder
    files = []
    
    # Check if the folder exists
    if os.path.exists(data_folder):
        # Walk through the directory
        for file_name in os.listdir(data_folder):
            # Get the full path
            file_path = os.path.join(data_folder, file_name)
            # Only append files (not directories)
            if os.path.isfile(file_path):
                # Get name without extension using os.path.splitext
                name_without_extension = os.path.splitext(file_name)[0]
                files.append(name_without_extension)
    
    return files

# Example usage
if __name__ == "__main__":
    file_list = get_files_in_data_folder()
    print("Files in data folder:")
    for file in file_list:
        print(f"- {file}")

