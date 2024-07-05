import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import shutil
import datetime
from datetime import datetime
import re
import asyncio
import json
import argparse
import shutil
import hashlib

from pyppeteer import launch
from PIL import Image
from matplotlib import colormaps
import numpy as np

# Define paths
source_base_dir = './infinitegames'  # Replace with the path to your source directory
deploy_dirs_file = './deploy_dirs.txt'  # Replace with the path to your deploy directories text file
RATINGS_FILE = 'game_ratings.json'

# Subdirectories for JS and CSS files
source_js_dir = os.path.join(source_base_dir, 'js')
source_css_dir = os.path.join(source_base_dir, 'css')
version_file_path = os.path.join(source_base_dir, 'version.txt')
log_file = os.path.join(source_base_dir, 'deploy_log.txt')

# Get the current version timestamp
version_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
current_date = datetime.now()

# Key variables and functions to check
key_variables = ['score', 'gameId']
key_functions = ['startGamingSessionApi', 'handleEndGameOnServer']

# Function to compute the hash of a file
def compute_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

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
# Function to get commit history and lines of code changes for a given repository directory
def get_commit_history(repo_dir):
    try:
        # Verify if the directory is a valid Git repository
        subprocess.run(["git", "-C", repo_dir, "status"], capture_output=True, check=True, text=True)
        # Get the commit history using Git
        result = subprocess.run(
            ["git", "-C", repo_dir, "log", "--pretty=format:%H %cd", "--date=short"],
            capture_output=True,
            text=True,
            check=True
        )
        commits = result.stdout.split('\n')
        commit_data = []
        for commit in commits:
            if commit:
                commit_hash, commit_date = commit.split(' ', 1)
                commit_date = datetime.strptime(commit_date, "%Y-%m-%d")
                # Get lines of code changes for each commit
                diff_result = subprocess.run(
                    ["git", "-C", repo_dir, "diff", "--numstat", commit_hash + "^!", commit_hash],
                    capture_output=True,
                    text=True,
                    check=True
                )
                added = 0
                removed = 0
                for line in diff_result.stdout.split('\n'):
                    if line:
                        add, rem, _ = line.split('\t')
                        if add.isdigit() and rem.isdigit():
                            added += int(add)
                            removed += int(rem)
                commit_data.append((commit_date, added, removed))
        return commit_data
    except subprocess.CalledProcessError as e:
        print(f"Error processing repository {repo_dir}: {e}")
        return []

# Function to plot the activity of each repository over time and save the graph to the images folder
# Function to plot the activity of each repository over time and save the graph to the images folder
def plot_activity(deploy_dirs):
    plt.figure(figsize=(14, 8))
    cmap = colormaps.get_cmap('tab10')
    colors = cmap(np.linspace(0, 1, len(deploy_dirs) + 1))  # +1 for the local directory

    total_commits = 0
    commits_per_repo = {}

    # Include the local directory in the plot
    local_dir = os.getcwd()
    all_dirs = deploy_dirs + [local_dir]

    all_commit_data = []

    for idx, repo_dir in enumerate(all_dirs):
        dir_name = os.path.basename(repo_dir.strip('/'))
        commit_data = get_commit_history(repo_dir)
        if commit_data:
            all_commit_data.extend(commit_data)
            num_commits = len(commit_data)
            commits_per_repo[dir_name] = num_commits
            total_commits += num_commits

    for idx, repo_dir in enumerate(all_dirs):
        dir_name = os.path.basename(repo_dir.strip('/'))
        commit_data = get_commit_history(repo_dir)

        if commit_data:
            dates, added_lines, removed_lines = zip(*commit_data)
            # Sort the dates to ensure the line is drawn left to right
            sorted_dates, sorted_added, sorted_removed = zip(*sorted(zip(dates, added_lines, removed_lines)))

            # Plot the commit points
            plt.plot(sorted_dates, [i + 1 for i in range(len(sorted_dates))], label=f"{dir_name} commits", color=colors[idx])

            for date, add, rem in zip(sorted_dates, sorted_added, sorted_removed):
                # Plot the added lines on a logarithmic scale
                plt.vlines(date, 0, np.log1p(add), color='green', alpha=0.5)
                # Plot the removed lines on a logarithmic scale
                plt.vlines(date, 0, -np.log1p(rem), color='red', alpha=0.5)

    plt.title("GitHub Repository Activity Over Time")
    plt.xlabel("Date")
    plt.ylabel("Number of Commits")
    plt.legend()
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()

    # Save the graph to the images folder
    images_dir = os.path.join(os.getcwd(), 'images')
    os.makedirs(images_dir, exist_ok=True)
    plot_path = os.path.join(images_dir, 'commit_activity.png')
    plt.savefig(plot_path)
    plt.close()

    # Print the summary
    print(f"Total number of commits found: {total_commits}")
    for repo, count in commits_per_repo.items():
        print(f"Repository '{repo}' has {count} commits")

# Function to update version.txt
def update_version_file(version_file_path):
    new_version = 1
    version_history = []

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    version_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as file:
            lines = file.readlines()
            if lines:
                for line in lines:
                    if line.startswith('Version:'):
                        current_version = int(line.split(':')[1].strip())
                        new_version = current_version + 1
                    version_history.append(line.strip())

    with open(version_file_path, 'w') as file:
        file.write(f"Version: {new_version}\n")
        file.write(f"Date: {current_date}\n")
        file.write(f"Timestamp: {version_timestamp}\n")
        file.write('\n'.join(version_history) + '\n')

    return new_version, version_timestamp

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


# Function to update the index.html file
def update_index_html(target_dir, js_files, css_files, new_version, version_timestamp):
    index_file = os.path.join(target_dir, 'index.html')
    if not os.path.exists(index_file):
        print(f"index.html not found in {target_dir}")
        return

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
        new_file_name = f"{new_version}_{base_name}_{version_timestamp}{ext}"
        new_js_include = f'<script src="infinite/js/{new_file_name}"></script>'
        new_js_includes.append(new_js_include)
    new_js_includes.append('<!-- #INFINITEGAMES JS END -->')

    new_css_includes = ['<!-- #INFINITEGAMES CSS START -->']
    for css_file in css_files:
        base_name, ext = os.path.splitext(css_file)
        new_file_name = f"{new_version}_{base_name}_{version_timestamp}{ext}"
        new_css_include = f'<link rel="stylesheet" href="infinite/css/{new_file_name}">'
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
    # for js_file in js_files:
    #     source_file = os.path.join(source_js_dir, js_file)
    #     external_vars = find_external_vars(source_file)
    #     if external_vars:
    #         print(f"External variables referenced in {js_file}: {', '.join(external_vars)}")

    # Copy version.txt to the target directory
    target_version_file = os.path.join(target_dir, 'version.txt')
    shutil.copy2(version_file_path, target_version_file)


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


# Main function to copy JS and CSS files to target directories and ensure inclusion in index.html
def copy_and_check_files():
    # Read target directories from the text file
    target_dirs = read_deploy_dirs(deploy_dirs_file)

    # Ensure the source directories are correctly set
    source_js_dir = os.path.join(source_base_dir, 'js')
    source_css_dir = os.path.join(source_base_dir, 'css')

    # Deploy files to the target directories
    deploy_files(source_js_dir, source_css_dir, target_dirs, version_file_path)

def load_ratings(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                ratings = json.load(file)
            except json.JSONDecodeError:
                ratings = {}
    else:
        ratings = {}
    return ratings

def save_ratings(file_path, ratings):
    with open(file_path, 'w') as file:
        json.dump(ratings, file, indent=4)

async def generate_game_content(deploy_dirs, ratings, log_file):
    game_content = ''
    log_entries = []
    for directory in sorted(deploy_dirs, key=lambda d: ratings.get(os.path.basename(d.strip('/')), 0), reverse=True):
        dir_name = os.path.basename(directory.strip('/'))
        rating = ratings.get(dir_name, 0)
        url = f'https://fractastical.github.io/{dir_name}/'
        snapshot_path = f'images/{dir_name}.png'
        
        success = await capture_snapshot(url, snapshot_path)
        if success:
            game_content += f'''
            <div class="game-item">
                <img src="{snapshot_path}" alt="{dir_name}">
                <a href="{url}">{dir_name} (Rating: {rating + 2})</a>
            </div>
            '''
        else:
            game_content += f'''
            <!--
            <div class="game-item">
                <img src="{snapshot_path}" alt="{dir_name}">
                <a href="{url}">{dir_name}</a>
            </div>
            -->
            '''
            log_entries.append(f'404 error for {url}')

    with open(log_file, 'a') as log:
        for entry in log_entries:
            log.write(entry + '\n')
    
    return game_content


# Function to generate a single index.html file in the current directory
def generate_index_html(deploy_dirs, template_file):
    with open(template_file, 'r') as file:
        template_content = file.read()

    game_content = ''
    for directory in deploy_dirs:
        dir_name = os.path.basename(directory.strip('/'))
        # Add a link for each game directory
        game_content += f'''
        <div class="grid-container">
            <div class="grid-item">
                <a href="https://fractastical.github.io/{dir_name}/">{dir_name}</a>
            </div>
        </div>
        '''

    # Replace the {game_content} placeholder in the template with the generated game content
    index_content = template_content.replace("{game_content}", game_content)

    # Write the modified content to index.html in the current directory
    output_file = os.path.join(os.getcwd(), 'index.html')
    with open(output_file, 'w') as file:
        file.write(index_content)

    print(f"Generated index.html in the current directory")


# Function to capture a snapshot of the index.html page
async def capture_snapshot(url, save_path):
    browser = await launch(headless=True)
    page = await browser.newPage()
    response = await page.goto(url)

    if response.status == 404:
        await browser.close()
        return False

    await page.screenshot({'path': save_path})
    await browser.close()
    return True

async def generate_index_html_with_snapshots(deploy_dirs, template_file, log_file, source_dir, build_content):
    # Load or initialize ratings
    ratings = load_ratings(RATINGS_FILE)
    
    # Initialize ratings to 0 for new games
    for directory in deploy_dirs:
        dir_name = os.path.basename(directory.strip('/'))
        if dir_name not in ratings:
            ratings[dir_name] = 6
    
    # Save the ratings to the file
    save_ratings(RATINGS_FILE, ratings)
    
    # Conditionally generate game content
    if build_content:
        game_content = await generate_game_content(deploy_dirs, ratings, log_file)
    else:
        game_content = ''
    
    with open(template_file, 'r') as file:
        template_content = file.read()

    index_content = template_content.replace("{game_content}", game_content)

    # Always create index.html in the source directory
    output_file = os.path.join(source_dir, 'index.html')
    with open(output_file, 'w') as file:
        file.write(index_content)
    print(f"Generated index.html in the source directory with snapshots")
    
    # Process other directories
    log_entries = []
    for directory in deploy_dirs:
        if directory == source_dir:
            continue
        
        game_content_path = os.path.join(directory, 'game_content.html')
        if os.path.exists(game_content_path):
            with open(game_content_path, 'r') as file:
                additional_content = file.read()
            
            index_content_with_merge = template_content.replace("{game_content}", additional_content)
            output_file = os.path.join(directory, 'index.html')
            with open(output_file, 'w') as file:
                file.write(index_content_with_merge)
            
            log_entries.append(f"MERGING GAME_CONTENT for {directory}")
            print(f"Generated index.html with merged game_content in {directory}")

    with open(log_file, 'a') as log:
        for entry in log_entries:
            log.write(entry + '\n')



# Function to deploy files to target directories
# Function to deploy files to target directories
def deploy_files(source_js_dir, source_css_dir, target_dirs, version_file_path):
    new_version, version_timestamp = update_version_file(version_file_path)

    js_files = [f for f in os.listdir(source_js_dir) if f.endswith('.js')]
    css_files = [f for f in os.listdir(source_css_dir) if f.endswith('.css')]

    for target_dir in target_dirs:
        js_target_dir = os.path.join(target_dir, 'infinite', 'js')
        css_target_dir = os.path.join(target_dir, 'infinite', 'css')
        os.makedirs(js_target_dir, exist_ok=True)
        os.makedirs(css_target_dir, exist_ok=True)

        for js_file in js_files:
            base_name, ext = os.path.splitext(js_file)
            new_file_name = f"{new_version}_{base_name}_{version_timestamp}{ext}"
            source_path = os.path.join(source_js_dir, js_file)
            target_path = os.path.join(js_target_dir, new_file_name)
            
            # Compare the hash of the source and target files
            source_hash = compute_file_hash(source_path)
            target_file_exists = os.path.exists(target_path)
            target_hash = compute_file_hash(target_path) if target_file_exists else None

            if not target_file_exists or source_hash != target_hash:
                shutil.copy2(source_path, target_path)

        for css_file in css_files:
            base_name, ext = os.path.splitext(css_file)
            new_file_name = f"{new_version}_{base_name}_{version_timestamp}{ext}"
            source_path = os.path.join(source_css_dir, css_file)
            target_path = os.path.join(css_target_dir, new_file_name)
            
            # Compare the hash of the source and target files
            source_hash = compute_file_hash(source_path)
            target_file_exists = os.path.exists(target_path)
            target_hash = compute_file_hash(target_path) if target_file_exists else None

            if not target_file_exists or source_hash != target_hash:
                shutil.copy2(source_path, target_path)

        update_index_html(target_dir, js_files, css_files, new_version, version_timestamp)


# def generate_game_index_html(deploy_dirs, template_file):
#     with open(template_file, 'r') as file:
#         template_content = file.read()

#     for directory in deploy_dirs:
#         dir_name = os.path.basename(directory.strip('/'))
#         # Define the game-specific content (this is an example, you can modify as needed)
#         game_content = f'''
#         <div class="grid-container">
#             <div class="grid-item">
#                 <a href="https://fractastical.github.io/{dir_name}/">{dir_name}</a>
#             </div>
#         </div>
#         '''

#         # Replace the {game_content} placeholder in the template with the actual game content
#         index_content = template_content.replace("{game_content}", game_content)

#         # Write the modified content to index.html in the current game directory
#         output_file = os.path.join(directory, 'index.html')
#         with open(output_file, 'w') as file:
#             file.write(index_content)

#         print(f"Generated index.html for {directory}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate index.html for directories")
    parser.add_argument("-b", "--build-content", action="store_true", help="Generate game content snapshots")
    args = parser.parse_args()

# Run the functions
current_directory = os.getcwd()
template_file = './index_template.html'  # Replace with the path to your template file
copy_and_check_files()
update_version_file(version_file_path)
deploy_dirs = read_deploy_dirs(deploy_dirs_file)

asyncio.get_event_loop().run_until_complete(generate_index_html_with_snapshots(deploy_dirs, template_file, log_file, current_directory, args.build_content))
if args.build_content :
    plot_activity(deploy_dirs)

print(f"JavaScript and CSS files copied and versioned with timestamp {version_timestamp}.")
print(f"Version file updated.")
