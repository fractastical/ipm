import os
import shutil
import datetime
import re


# Define paths
source_dir = './infinitegames'  # Replace with the path to your source JS files
target_dirs = ['/Users/jd/Documents/Github/infinitepong', '/Users/jd/Documents/Github/nachoblaster', '/Users/jd/Documents/Github/nachoblaster3d', '/Users/jd/Documents/Github/infiniteflap']

# Get the current version timestamp
version_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

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

# Function to copy JS files to target directories and ensure inclusion in index.html
def copy_and_check_js_files():
    # Get list of JS files in the source directory
    js_files = [f for f in os.listdir(source_dir) if f.endswith('.js')]
    
    for target_dir in target_dirs:
        infinite_dir = os.path.join(target_dir, 'infinite')
        
        # Create /infinite/ directory if it does not exist
        if not os.path.exists(infinite_dir):
            os.makedirs(infinite_dir)
        
        # Copy JS files to /infinite/ directory
        for js_file in js_files:
            source_file = os.path.join(source_dir, js_file)
            target_file = os.path.join(infinite_dir, js_file)
            shutil.copy2(source_file, target_file)
            
            # Create a versioned copy of the JS file in the source directory
            versioned_file = os.path.join(source_dir, f"{os.path.splitext(js_file)[0]}_{version_timestamp}.js")
            shutil.copy2(source_file, versioned_file)
        
        # Ensure JS files are included in index.html
        index_file = os.path.join(target_dir, 'index.html')
        if os.path.exists(index_file):
            with open(index_file, 'r') as file:
                index_content = file.read()
            
            for js_file in js_files:
                new_js_include = f'<script src="infinite/{js_file}?v={version_timestamp}"></script>'
                js_pattern = re.compile(rf'<script src="infinite/{js_file}.*"></script>')
                
                if js_pattern.search(index_content):
                    index_content = js_pattern.sub(new_js_include, index_content)
                else:
                    index_content += f'\n{new_js_include}'
            
            with open(index_file, 'w') as file:
                file.write(index_content)
            
            # Check for external variable references and log them
            for js_file in js_files:
                source_file = os.path.join(source_dir, js_file)
                external_vars = find_external_vars(source_file)
                if external_vars:
                    print(f"External variables referenced in {js_file}: {', '.join(external_vars)}")

# Run the function
copy_and_check_js_files()

print(f"JavaScript files copied and versioned with timestamp {version_timestamp}.")

    