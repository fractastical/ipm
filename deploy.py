import os
import shutil
import re
import datetime

def get_js_files(src_dir):
    return [f for f in os.listdir(src_dir) if f.endswith('.js')]

def ensure_js_in_index(target_dir, js_files):
    index_path = os.path.join(target_dir, 'index.html')
    if not os.path.exists(index_path):
        return

    with open(index_path, 'r') as file:
        content = file.read()

    for js_file in js_files:
        if js_file not in content:
            # If the JS file is not in the index.html, add it
            content += f'\n<script src="/infinite/{js_file}"></script>'

    with open(index_path, 'w') as file:
        file.write(content)

def copy_js_files_to_target(src_dir, target_dir, version):
    js_files = get_js_files(src_dir)
    target_infinite_dir = os.path.join(target_dir, 'infinite')
    os.makedirs(target_infinite_dir, exist_ok=True)

    for js_file in js_files:
        base_name, ext = os.path.splitext(js_file)
        new_js_file = f"{base_name}_v{version}{ext}"
        shutil.copy(os.path.join(src_dir, js_file), os.path.join(target_infinite_dir, new_js_file))

    ensure_js_in_index(target_dir, [f"{base_name}_v{version}{ext}" for js_file in js_files])

def create_version_file(src_dir, version):
    version_file = os.path.join(src_dir, 'version.txt')
    with open(version_file, 'w') as file:
        file.write(f"Version: {version}\nDate: {datetime.datetime.now()}")

def main():
    src_dir = './infinitegames'
    target_dirs = ['/Users/jd/Documents/Github/infinitepong', '/Users/jd/Documents/Github/nachoblaster', '/Users/jd/Documents/Github/nachoblaster3d', '/Users/jd/Documents/Github/infiniteflap']
    

    # Determine the new version
    version_file = os.path.join(src_dir, 'version.txt')
    if os.path.exists(version_file):
        with open(version_file, 'r') as file:
            content = file.read()
            match = re.search(r'Version:\s*(\d+)', content)
            version = int(match.group(1)) + 1 if match else 1
    else:
        version = 1

    # Create a new version file
    create_version_file(src_dir, version)

    for target_dir in target_dirs:
        copy_js_files_to_target(src_dir, target_dir, version)

if __name__ == '__main__':
    main()
