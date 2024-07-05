import os
from collections import defaultdict
from pygments.lexers import get_lexer_for_filename
from pygments.util import ClassNotFound

def count_lines_of_code(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return sum(1 for line in file)

def detect_language(file_path):
    try:
        lexer = get_lexer_for_filename(file_path)
        return lexer.name
    except ClassNotFound:
        return None

def calculate_loc_by_language(folder_paths):
    loc_by_language = defaultdict(int)
    for folder in folder_paths:
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                language = detect_language(file_path)
                if language:
                    loc_by_language[language] += count_lines_of_code(file_path)
    return loc_by_language

def read_folder_paths(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def main(folder_paths_file):
    folder_paths = read_folder_paths(folder_paths_file)
    loc_by_language = calculate_loc_by_language(folder_paths)
    for language, loc in loc_by_language.items():
        print(f'{language}: {loc} lines of code')

if __name__ == "__main__":
    folder_paths_file = 'deploy_dirs.txt'  # Change this to the path of your text file
    main(folder_paths_file)
