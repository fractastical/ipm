import os
import shutil
import datetime
import re


# Define paths

source_js_dir = './infinitegames/js'  # Replace with the path to your source JS files
source_css_dir = './infinitegames/css'  # Replace with the path to your source CSS files


deploy_dirs_file = 'deploygames.txt'  # Replace with the path to your deploy directories text file
version_file = 'version.txt'  # Replace with the path to your version.txt file

# Get the current version timestamp
version_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
current_date = datetime.datetime.now()

# Function to find external variables referenced in the JS files
def find_external_vars(js_file_path):
    with open(js_file_path, 'r') as file:
        content = file.read()
    
    # Find all variable references in the JS file
    variables = re.findall(r'\b\w+\b', content)
    
    # Find all declared variables in the JS file
    declared_vars = set(re.findall(r'\bvar\s+(\w+)\b|\bconst\s+(\w+)\b|\blet\s+(\w+)\b', content))
    declared_vars = {var for var_tuple in declared_vars for var in var_tuple if var}
    
    # Identify external variables
    external_vars = set(variables) - declared_vars
    
    return external_vars

# Function to read target directories from the text file
def read_deploy_dirs(file_path):
    with open(file_path, 'r') as file:
        dirs = [line.strip() for line in file if line.strip()]
    return dirs

# Function to update version.txt
def update_version_file(version_file_path):
    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) >= 2:
                current_version = int(lines[0].split(':')[1].strip())
                new_version = current_version + 1
            else:
                new_version = 1
    else:
        new_version = 1

    with open(version_file_path, 'w') as file:
        file.write(f"Version: {new_version}\n")
        file.write(f"Date: {current_date}\n")

# Function to copy JS and CSS files to target directories and ensure inclusion in index.html
def copy_and_check_files():
    # Read target directories from the text file
    target_dirs = read_deploy_dirs(deploy_dirs_file)

    # Get list of JS and CSS files in the source directories
    js_files = [f for f in os.listdir(source_js_dir) if f.endswith('.js')]
    css_files = [f for f in os.listdir(source_css_dir) if f.endswith('.css')]
    
    for target_dir in target_dirs:
        infinite_js_dir = os.path.join(target_dir, 'infinite/js')
        infinite_css_dir = os.path.join(target_dir, 'infinite/css')
        
        # Create /infinite/js/ and /infinite/css/ directories if they do not exist
        if not os.path.exists(infinite_js_dir):
            os.makedirs(infinite_js_dir)
        if not os.path.exists(infinite_css_dir):
            os.makedirs(infinite_css_dir)
        
        # Copy JS files to /infinite/js/ directory
        for js_file in js_files:
            source_file = os.path.join(source_js_dir, js_file)
            base_name, ext = os.path.splitext(js_file)
            if not re.search(r'_\d{14}$', base_name):
                new_file_name = f"{base_name}_{version_timestamp}{ext}"
            else:
                new_file_name = f"{base_name}{ext}"
            target_file = os.path.join(infinite_js_dir, new_file_name)
            
            # Create a versioned copy of the JS file in the target directory
            shutil.copy2(source_file, target_file)
        
        # Copy CSS files to /infinite/css/ directory
        for css_file in css_files:
            source_file = os.path.join(source_css_dir, css_file)
            base_name, ext = os.path.splitext(css_file)
            if not re.search(r'_\d{14}$', base_name):
                new_file_name = f"{base_name}_{version_timestamp}{ext}"
            else:
                new_file_name = f"{base_name}{ext}"
            target_file = os.path.join(infinite_css_dir, new_file_name)
            
            # Create a versioned copy of the CSS file in the target directory
            shutil.copy2(source_file, target_file)
        
        # Ensure JS and CSS files are included in index.html
        index_file = os.path.join(target_dir, 'index.html')
        if os.path.exists(index_file):
            with open(index_file, 'r') as file:
                index_content = file.read()
            
            # Remove old #INFINITEGAMES entries for JS and CSS
            index_content = re.sub(r'<!-- #INFINITEGAMES JS START -->.*<!-- #INFINITEGAMES JS END -->', '', index_content, flags=re.DOTALL)
            index_content = re.sub(r'<!-- #INFINITEGAMES CSS START -->.*<!-- #INFINITEGAMES CSS END -->', '', index_content, flags=re.DOTALL)
            
            # Prepare new includes within the #INFINITEGAMES namespace
            new_js_includes = ['<!-- #INFINITEGAMES JS START -->']
            for js_file in js_files:
                base_name, ext = os.path.splitext(js_file)
                if not re.search(r'_\d{14}$', base_name):
                    new_js_include = f'<script src="infinite/js/{base_name}_{version_timestamp}{ext}"></script>'
                else:
                    new_js_include = f'<script src="infinite/js/{base_name}{ext}"></script>'
                new_js_includes.append(new_js_include)
            new_js_includes.append('<!-- #INFINITEGAMES JS END -->')
            
            new_css_includes = ['<!-- #INFINITEGAMES CSS START -->']
            for css_file in css_files:
                base_name, ext = os.path.splitext(css_file)
                if not re.search(r'_\d{14}$', base_name):
                    new_css_include = f'<link rel="stylesheet" href="infinite/css/{base_name}_{version_timestamp}{ext}">'
                else:
                    new_css_include = f'<link rel="stylesheet" href="infinite/css/{base_name}{ext}">'
                new_css_includes.append(new_css_include)
            new_css_includes.append('<!-- #INFINITEGAMES CSS END -->')
            
            # Insert new includes in the appropriate places
            head_insert_pos = index_content.find('</head>')
            if head_insert_pos != -1:
                index_content = index_content[:head_insert_pos] + '\n'.join(new_css_includes) + '\n' + index_content[head_insert_pos:]
            
            body_insert_pos = index_content.find('</body>')
            if body_insert_pos != -1:
                index_content = index_content[:body_insert_pos] + '\n'.join(new_js_includes) + '\n' + index_content[body_insert_pos:]
            
            with open(index_file, 'w') as file:
                file.write(index_content)
            
            # Check for external variable references and log them
            for js_file in js_files:
                source_file = os.path.join(source_js_dir, js_file)
                external_vars = find_external_vars(source_file)
                if external_vars:
                    print(f"External variables referenced in {js_file}: {', '.join(external_vars)}")

# Run the functions
copy_and_check_files()
update_version_file(version_file)

print(f"JavaScript and CSS files copied and versioned with timestamp {version_timestamp}.")
print(f"Version file updated.")
