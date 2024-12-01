import os
import sys
import requests
import subprocess
from github import Github
import shutil
import json

# ANSI escape codes for colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
GREY = "\033[90m"

# Initialize GitHub API
g = Github()

# Repository and folder configuration
REPO_NAME = "The-Asterisk-Co/toast"
DATABASE_FOLDER = "database"
SETUPS_FOLDER = "setups"

def download_file(url, local_path):
    """Download a file from a raw URL."""
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors
    with open(local_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"{GREEN}[✓]: Downloaded {BOLD}{os.path.basename(local_path)}{RESET}")

def download_folder(repo, folder_path, local_path):
    """Downloads only `.exe` files from a GitHub repository folder."""
    contents = repo.get_contents(folder_path)
    os.makedirs(local_path, exist_ok=True)

    for content_file in contents:
        if content_file.type == "dir":
            # Recursively search within subdirectories
            download_folder(repo, content_file.path, os.path.join(local_path, content_file.name))
        elif content_file.name.endswith(".exe"):  # Only download .exe files
            file_path = os.path.join(local_path, content_file.name)
            print(f"{BLUE}[>]: Downloading {BOLD}{content_file.path}{RESET}{BLUE}...{RESET}")
            # Use raw URL for binary file download
            download_url = content_file.download_url
            download_file(download_url, file_path)
            
            # Execute the downloaded .exe file
            try:
                print(f"{CYAN}[i]: Executing {BOLD}{file_path}{RESET}")
                subprocess.run([file_path], check=True)
                print(f"{GREEN}[✓]: Successfully executed {BOLD}{file_path}{RESET}")
            except subprocess.CalledProcessError as e:
                print(f"{RED}[X]: Error while executing {BOLD}{file_path}{RESET}: {e}")
        else:
            print(f"{CYAN}[i]: Skipping non-.exe file {BOLD}{content_file.name}{RESET}")

    print(f"{GREEN}[✓]: Successfully installed {BOLD}'{file_path}'{RESET}")


def get_about(repo, folder_path):
    """Download about.json from the given folder_path of the GitHub repo and extract variables."""
    try:
        # Look for about.json in the specified folder
        contents = repo.get_contents(folder_path)
        for content_file in contents:
            if content_file.name == "about.json":
                temp_file_path = "about.json"
                download_file(content_file.download_url, temp_file_path)

                # Load and extract data from about.json
                with open(temp_file_path) as file:
                    data = json.load(file)

                name = data.get("name", "Unknown")
                id = data.get("id", "Unknown")
                publisher = f"by {data.get("publisher", "Unknown")}"
                description = data.get("description", "")

                des_arr = description.split("\n")
                max_line_length = max(
                    [len(line) for line in [name, id, publisher] + des_arr]
                )
                box_width = max_line_length + 4

                # Create the yellow outlined box for the about page
                box_border_up = f"{YELLOW}╭{'─' * box_width}╮{RESET}"
                box_border_down = f"{YELLOW}╰{'─' * box_width}╯{RESET}"
                print(f"\n{box_border_up}")
                print(
                    f"{YELLOW}│{RESET}  {CYAN}{BOLD}{name}{RESET}{' ' * (box_width - len(name) - 2)}{YELLOW}│{RESET}"
                )
                print(
                    f"{YELLOW}│{RESET}  {YELLOW}{id}{RESET}{' ' * (box_width - len(id) - 2)}{YELLOW}│{RESET}"
                )
                print(
                    f"{YELLOW}│{RESET}  {GREY}{publisher}{RESET}{' ' * (box_width - len(publisher) - 2)}{YELLOW}│{RESET}"
                )
                print(f"{YELLOW}│{RESET}{' ' * (box_width)}{YELLOW}│{RESET}")

                for line in des_arr:
                    print(
                        f"{YELLOW}│{RESET}  {GREY}{line}{RESET}{' ' * (box_width - len(line) - 2)}{YELLOW}│{RESET}"
                    )

                print(f"{box_border_down}\n")

                # Remove the temporary about.json file after use
                os.remove(temp_file_path)
                return

        print(f"{RED}[X]: about.json not found in {folder_path}{RESET}")
    except Exception as e:
        print(f"{RED}[X]: Error `{e}`{RESET}")


def main():
    """Main function to parse arguments and execute the installer."""
    if len(sys.argv) == 1:
        max_line_length = max(
            [len(line) for line in ["toast", "v1.0", "by The Asterisk Co.", "A CLI app store for Windows"]]
        )
        box_width = max_line_length + 4
        box_border_up = f"{YELLOW}╭{'─' * box_width}╮{RESET}"
        box_border_down = f"{YELLOW}╰{'─' * box_width}╯{RESET}"
        print(f"\n{box_border_up}")
        print(
            f"{YELLOW}│{RESET}  {CYAN}{BOLD}{"toast"}{RESET}{' ' * (box_width - len("toast") - 2)}{YELLOW}│{RESET}"
        )
        print(
            f"{YELLOW}│{RESET}  {YELLOW}{"v1.0"}{RESET}{' ' * (box_width - len("v1.0") - 2)}{YELLOW}│{RESET}"
        )
        print(
            f"{YELLOW}│{RESET}  {GREY}{"by The Asterisk Co."}{RESET}{' ' * (box_width - len("by The Asterisk Co.") - 2)}{YELLOW}│{RESET}"
        )
        print(f"{YELLOW}│{RESET}{' ' * (box_width)}{YELLOW}│{RESET}")
        print(
            f"{YELLOW}│{RESET}  {GREY}{"A CLI app store for Windows"}{RESET}{' ' * (box_width - len("A CLI app store for Windows") - 2)}{YELLOW}│{RESET}"
        )

        print(f"{box_border_down}\n")
    elif sys.argv[1] == "install":
        folder_name = sys.argv[2]
    
        try:
            repo = g.get_repo(REPO_NAME)
            folder_path = f"{DATABASE_FOLDER}/{folder_name}"

            local_path = os.path.join(SETUPS_FOLDER, folder_name)
            download_folder(repo, folder_path, local_path)

        except Exception as e:
            print(f"{RED}[X]: Error `{e}`{RESET}")
    elif sys.argv[1] == "clear-setups":
        confirm = input(f"{YELLOW}[?]: Are you sure you want to delete all setup files?{GREY} [Y/N]: {RESET}")
        if confirm == "y" or confirm == "Y":
            shutil.rmtree(SETUPS_FOLDER)
            os.mkdir(SETUPS_FOLDER)
        else:
            pass
    elif sys.argv[1] == "search":
        query = sys.argv[2]
        try:
            repo = g.get_repo(REPO_NAME)
            contents = repo.get_contents(DATABASE_FOLDER)
            matches = [content.name for content in contents if query.lower() in content.name.lower()]
            if matches:
                print(f"{GREEN}[✓]: Found matches: {', '.join(matches)}{RESET}")
            else:
                print(f"{RED}[X]: No matches found for {query}{RESET}")
        except Exception as e:
            print(f"{RED}[X]: Error `{e}`{RESET}")
    elif sys.argv[1] == "about":
        folder_name = sys.argv[2]
        try:
            repo = g.get_repo(REPO_NAME)
            folder_path = f"{DATABASE_FOLDER}/{folder_name}"

            # Call the get_about function to download and extract about.json
            get_about(repo, folder_path)

        except Exception as e:
            print(f"{RED}[X]: Error `{e}`{RESET}")
    else:
        print(f"{RED}[X]: Error no such command {BOLD}`{sys.argv[1]}`{RESET}")

if __name__ == "__main__":
    main()
