import os


def create_project_dir(directory):
    """Creates the project directory if it doesn't exist and confirms creation."""
    try:
        if not os.path.exists(directory):
            print('Creating project directory at ' + directory)
            os.makedirs(directory)
        return True  # Return True to indicate successful creation
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False  # Return False to indicate failure


def create_data_files(project_name, base_url):
    """Creates the necessary files for the project and checks for successful creation."""
    waiting_path = os.path.join(project_name, 'waiting.txt')
    crawled_path = os.path.join(project_name, 'crawled.txt')
    success = True

    if not os.path.isfile(waiting_path):
        if not write_file(waiting_path, base_url):
            print(f"Failed to create file: {waiting_path}")
            success = False

    if not os.path.isfile(crawled_path):
        if not write_file(crawled_path, ''):
            print(f"Failed to create file: {crawled_path}")
            success = False

    return success  # Return overall success status


# Create a new file
def write_file(path, data):
    with open(path, 'w') as file:
        file.write(data)
        file.close()


# add data onto an existing file
def append_to_file(path, data):
    with open(path, 'a') as file:
        file.write(data + '\n')
        file.close()


# Delete the contents of a file
def delete_file_contents(path):
    with open(path, 'w'):
        pass  # Do nothing (clear the file)


# Read a file and convert each line to set items
def file_to_set(file_name):
    results = set()
    try:
        with open(file_name, 'rt') as f:
            for line in f:
                results.add(line.replace('\n', ''))
    except Exception as e:
        print("Error: can't read the file", e)
    return results


# Iterate through a set, each item will be a new line in the file
def set_to_file(urls, file):
    delete_file_contents(file)
    # Sort the links before writing them to the file to make it easier to work with data later.
    sorted_url = sorted(urls)
    for url in sorted_url:
        append_to_file(file, url)
