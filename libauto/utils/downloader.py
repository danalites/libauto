#!/usr/bin/python3
import re
import os
import urllib.request
import signal
import json
import sys

# this ANSI code lets us erase the current line
ERASE_LINE = "\x1b[2K"


# type: (str, str, bool, any) -> None
def print_text(text, color="default", in_place=False, **kwargs):
    """
    print text to console, a wrapper to built-in print

    :param text: text to print
    :param color: can be one of "red" or "green", or "default"
    :param in_place: whether to erase previous line and print in place
    :param kwargs: other keywords passed to built-in print
    """
    if in_place:
        print("\r" + ERASE_LINE, end="")
    print(text, **kwargs)


def create_url(url):
    """
    From the given url, produce a URL that is compatible with Github's REST API. Can handle blob or tree paths.
    """
    repo_only_url = re.compile(
        r"https:\/\/github\.com\/[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}\/[a-zA-Z0-9]+$")
    re_branch = re.compile("/(tree|blob)/(.+?)/")

    # Check if the given url is a url to a GitHub repo. If it is, tell the
    # user to use 'git clone' to download it
    if re.match(repo_only_url, url):
        print_text("✘ The given url is a complete repository. Use 'git clone' to download the repository",
                   "red", in_place=True)
        sys.exit()

    # extract the branch name from the given url (e.g master)
    branch = re_branch.search(url)
    download_dirs = url[branch.end():]
    api_url = (url[:branch.start()].replace("github.com", "api.github.com/repos", 1) +
               "/contents/" + download_dirs + "?ref=" + branch.group(2))
    return api_url, download_dirs


def download(repo_url, flatten=False, output_dir="./", folder_name=None):
    """ Downloads the files and directories in repo_url. If flatten is specified, the contents of any and all
     sub-directories will be pulled upwards into the root folder. """

    if sys.platform != 'win32':
        # disable CTRL+Z
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)

    # generate the url which returns the JSON data
    api_url, download_dirs = create_url(repo_url)

    # To handle file names.
    if not flatten:
        if len(download_dirs.split(".")) == 0:
            dir_out = os.path.join(output_dir, download_dirs)
        else:
            dir_out = os.path.join(
                output_dir, "/".join(download_dirs.split("/")[:-1]))
    else:
        dir_out = output_dir

    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        response = urllib.request.urlretrieve(api_url)

    except KeyboardInterrupt:
        # when CTRL+C is pressed during the execution of this script,
        # bring the cursor to the beginning, erase the current line, and dont make a new line
        print_text("✘ Got interrupted", "red", in_place=True)
        sys.exit()
    
    except Exception as e:
        print_text(f"✘ Failure {e}", "red", in_place=True)

    if not flatten:
        # make a directory with the name which is taken from
        # the actual repo
        # os.makedirs(dir_out, exist_ok=True)
        pass

    # total files count
    total_files = 0

    with open(response[0], "r") as f:
        data = json.load(f)
        # getting the total number of files so that we
        # can use it for the output information later
        total_files += len(data)

        # If the data is a file, download it as one.
        if isinstance(data, dict) and data["type"] == "file":
            try:
                # download the file
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)

                location = os.path.join(dir_out, data["name"])
                urllib.request.urlretrieve(data["download_url"], location)
                # bring the cursor to the beginning, erase the current line, and dont make a new line
                print_text("Downloaded: " +
                           "{}".format(data["name"]) + f"to {location}", "green", in_place=True)

                return total_files
            except KeyboardInterrupt:
                # when CTRL+C is pressed during the execution of this script,
                # bring the cursor to the beginning, erase the current line, and dont make a new line
                print_text("✘ Got interrupted", 'red', in_place=False)
                sys.exit()

        for file in data:
            file_url = file["download_url"]
            file_name = file["name"]
            file_path = file["path"]

            if flatten:
                path = os.path.basename(file_path)
            else:
                path = file_path

            # Here "path" is a relative path to github repo root
            if folder_name is not None:
                rel_to_folder = path.split(folder_name + "/")[-1]
                path = os.path.join(output_dir, rel_to_folder)
            else:
                path = os.path.join(output_dir, path)
            # print("@@", "out:", output_dir, "path:", path, "folder:", folder_name)
            dirname = os.path.dirname(path)

            if dirname != '':
                os.makedirs(os.path.dirname(path), exist_ok=True)
            else:
                pass

            if file_url is not None:
                try:
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    urllib.request.install_opener(opener)
                    # download the file
                    urllib.request.urlretrieve(file_url, path)

                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print_text(f"Downloaded: \"{file_name}\" to \"{path}\"")

                except KeyboardInterrupt:
                    # when CTRL+C is pressed during the execution of this script,
                    # bring the cursor to the beginning, erase the current line, and dont make a new line
                    print_text("✘ Got interrupted", 'red', in_place=False)
                    sys.exit()
            else:
                download(file["html_url"], flatten, output_dir, folder_name)

    return total_files



