import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import shutil
import datetime
from datetime import datetime
import re

# Define paths
source_dir = './infinitegames'  # Replace with the path to your source directory
deploy_dirs_file = './deploy_dirs.txt'  # Replace with the path to your deploy directories text file

# Subdirectories for JS and CSS files
source_js_dir = os.path.join(source_dir, 'js')
source_css_dir = os.path.join(source_dir, 'css')
version_file = os.path.join(source_dir, 'version.txt')
log_file = os.path.join(source_dir, 'deploy_log.txt')

# Get the current version timestamp
version_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
current_date = datetime.now()

# Key variables and functions to check
key_variables = ['score', 'gameId']
key_functions = ['startGamingSessionApi', 'handleEndGameOnServer']

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


# Function to get commit history for a given repository directory
def get_commit_history(repo_dir):
    try:
        # Verify if the directory is a valid Git repository
        subprocess.run(["git", "-C", repo_dir, "status"], capture_output=True, check=True, text=True)
        # Get the commit history using Git
        result = subprocess.run(
            ["git", "-C", repo_dir, "log", "--pretty=format:%cd", "--date=short"],
            capture_output=True,
            text=True,
            check=True
        )
        commit_dates = result.stdout.split('\n')
        return [datetime.strptime(date, "%Y-%m-%d") for date in commit_dates if date]
    except subprocess.CalledProcessError as e:
        print(f"Error processing repository {repo_dir}: {e}")
        return []

# Function to plot the activity of each repository over time
def plot_activity(deploy_dirs):
    plt.figure(figsize=(14, 8))
    colors = plt.cm.get_cmap('tab10', len(deploy_dirs))

    total_commits = 0
    commits_per_repo = {}

    for idx, repo_dir in enumerate(deploy_dirs):
        dir_name = os.path.basename(repo_dir.strip('/'))
        commit_dates = get_commit_history(repo_dir)
        num_commits = len(commit_dates)
        commits_per_repo[dir_name] = num_commits
        total_commits += num_commits
        
        if commit_dates:
            dates, counts = zip(*[(date, commit_dates.count(date)) for date in set(commit_dates)])
            # Sort the dates to ensure the line is drawn left to right
            sorted_dates, sorted_counts = zip(*sorted(zip(dates, counts)))
            plt.plot(sorted_dates, sorted_counts, label=dir_name, color=colors(idx))
            plt.scatter(sorted_dates, sorted_counts, color=colors(idx))

    plt.title("GitHub Repository Activity Over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Commits")
    plt.legend()
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()

    # Print the summary
    print(f"Total number of commits found: {total_commits}")
    for repo, count in commits_per_repo.items():
        print(f"Repository '{repo}' has {count} commits")

# Function to update version.txt
def update_version_file(version_file_path):
    new_version = 1
    version_history = []

    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as file:
            lines = file.readlines()
            if lines:
                for line in lines:
                    if line.startswith('Version:'):
                        current_version = int(line.split(':')[1].strip())
                        new_version = current_version + 1
                    version_history.append(line.strip())

    # Append the new version and date to the history
    version_history.append(f"Version: {new_version}")
    version_history.append(f"Date: {current_date}")

    # Write the updated history back to the file
    with open(version_file_path, 'w') as file:
        file.write('\n'.join(version_history) + '\n')


# Function to check for key variables and functions in the content
def check_key_elements(content, elements, element_type):
    missing_elements = []
    for element in elements:
        if not re.search(rf'\b{element}\b', content):
            missing_elements.append(element)
    return missing_elements

# Function to add the leaderboard container HTML if it does not exist
def ensure_leaderboard_container(index_content):
    leaderboard_html = '''
    <div id="leaderboard-container" style="display:none;">
      <div id="leaderboard">
        <h2>Leaderboard</h2>
        <ol id="leaderboard-list"></ol>
      </div>
    </div>
    '''

    # Check if the leaderboard container already exists
    if not re.search(r'<div\s+id="leaderboard-container"', index_content, re.IGNORECASE):
        # Insert the leaderboard container before the closing </body> tag
        body_close_tag = '</body>'
        insert_pos = index_content.find(body_close_tag)
        if insert_pos != -1:
            index_content = index_content[:insert_pos] + leaderboard_html + '\n' + index_content[insert_pos:]
        else:
            # If </body> tag is not found, append the HTML at the end
            index_content += leaderboard_html

    return index_content

# Function to log warnings
def log_warning(log_file_path, target_dir, missing_variables, missing_functions):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Directory: {target_dir}\n")
        if missing_variables:
            log_file.write(f"  Missing variables: {', '.join(missing_variables)}\n")
        if missing_functions:
            log_file.write(f"  Missing functions: {', '.join(missing_functions)}\n")

# Function to generate index.html with links to all games
def generate_main_index_html(deploy_dirs, output_file):
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Infinite Games</title>
        <style>
            .grid-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 10px;
            }
            .grid-item {
                background-color: #f2f2f2;
                padding: 10px;
                text-align: center;
                border: 1px solid #ccc;
            }
        </style>
    </head>
    <body>
        <h1>Infinite Games</h1>
        <div class="grid-container">
    '''

    base_url = "https://fractastical.github.io/"

    for directory in deploy_dirs:
        dir_name = os.path.basename(directory.strip('/'))
        html_content += f'''
            <div class="grid-item">
                <a href="{base_url}{dir_name}/">{dir_name}</a>
            </div>
        '''

    html_content += '''
        </div>
    </body>
    </html>
    '''

    with open(output_file, 'w') as file:
        file.write(html_content)


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

            # Initialize lists to store missing elements
            missing_variables = []
            missing_functions = []

            # Check for key variables and functions
            for js_file in js_files:
                js_file_path = os.path.join(source_js_dir, js_file)
                with open(js_file_path, 'r') as js_content_file:
                    js_content = js_content_file.read()
                    missing_variables += check_key_elements(js_content, key_variables, "variable")
                    missing_functions += check_key_elements(js_content, key_functions, "function")
            
            missing_variables += check_key_elements(index_content, key_variables, "variable")
            missing_functions += check_key_elements(index_content, key_functions, "function")
            
            # Log warnings for missing elements
            if missing_variables or missing_functions:
                log_warning(log_file, target_dir, missing_variables, missing_functions)
            
            # Remove old #INFINITEGAMES entries for JS and CSS
            index_content = re.sub(r'<!-- #INFINITEGAMES JS START -->.*<!-- #INFINITEGAMES JS END -->', '', index_content, flags=re.DOTALL)
            index_content = re.sub(r'<!-- #INFINITEGAMES CSS START -->.*<!-- #INFINITEGAMES CSS END -->', '', index_content, flags=re.DOTALL)
           
            # Ensure the leaderboard container is present
            index_content = ensure_leaderboard_container(index_content)

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

        # Copy version.txt to the target directory
        target_version_file = os.path.join(target_dir, 'version.txt')
        shutil.copy2(version_file, target_version_file)


def generate_game_index_html(deploy_dirs, template_file):
    with open(template_file, 'r') as file:
        template_content = file.read()

    for directory in deploy_dirs:
        dir_name = os.path.basename(directory.strip('/'))
        # Define the game-specific content (this is an example, you can modify as needed)
        game_content = f'''
        <div class="grid-container">
            <div class="grid-item">
                <a href="https://fractastical.github.io/{dir_name}/">{dir_name}</a>
            </div>
        </div>
        '''

        # Replace the {game_content} placeholder in the template with the actual game content
        index_content = template_content.replace("{game_content}", game_content)

        # Write the modified content to index.html in the current game directory
        output_file = os.path.join(directory, 'index.html')
        with open(output_file, 'w') as file:
            file.write(index_content)

        print(f"Generated index.html for {directory}")

# Run the functions
template_file = './index_template.html'  # Replace with the path to your template file
copy_and_check_files()
update_version_file(version_file)
deploy_dirs = read_deploy_dirs(deploy_dirs_file)
generate_game_index_html(deploy_dirs, template_file)

plot_activity(deploy_dirs)

print(f"JavaScript and CSS files copied and versioned with timestamp {version_timestamp}.")
print(f"Version file updated.")
