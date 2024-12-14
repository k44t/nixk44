from utils_python.utils_python_package.src.Apoeschllogging import *

import argparse
import requests

raise NotImplementedError

parser = argparse.ArgumentParser(description="copy issue boards from gitlab repo to gitlab repo")
parser.add_argument("--gitlab_url", type=str, required=True, help="the url of your gitlab server, e.g. https://etzchaim.k44")
parser.add_argument("--source", type=str, required=True, help="the name of the source repository")
parser.add_argument("--destination", type=str, required=True, help="the name of the destination repository")
parser.add_argument("--private_token", type=str, required=True, help="your privatetoken from http://yourgitlabserver:port/-/user_settings/personal_access_tokens, e.g. https://etzchaim.k44/-/user_settings/personal_access_tokens")
args = parser.parse_args()
gitlab_url = args.gitlab_url
source = args.source
destination = args.destination
projects_api_url = "/api/v4/projects/"
headers = {
    "PRIVATE-TOKEN":args.private_token,
    'Content-Type': 'application/json'
}
projects = requests.get(gitlab_url + projects_api_url, headers=headers)
dict_projects = projects.json()
for project in dict_projects:
    if source == project["name"]:
        Log_info(f"source_project is: " + project["name"])
        source_id = project["id"]
    if destination == project["name"]:
        Log_info(f"destination_project is: " + project["name"])
        destination_id = project["id"]
request = gitlab_url + projects_api_url + str(source_id) + "/boards"
Log_info(f"get_request is: {request}")
source_boards = requests.get(request, headers=headers)
dict_source_boards = source_boards.json()
request = gitlab_url + projects_api_url + str(destination_id) + "/boards"
destination_boards = requests.get(request, headers=headers)
dict_destination_boards = destination_boards.json()
for source_board in dict_source_boards:
    already_existing = False
    source_lists = source_board["lists"]
    for destination_board in dict_destination_boards:
        destination_lists = destination_board["lists"]
        for source_list in source_lists:
            for destination_list in destination_lists:
                if source_board["name"] == destination_board["name"] and source_list == destination_list:
                    already_existing = True
                    Log_info(f"list {source_list} already exists in {destination}")
                    continue
                else:
                    data = {
                        "lists":"" #alexTODO: hier gehts weiter-119,02
                    }
                    request = gitlab_url + projects_api_url + str(destination_id) + "/boards" + board_id + "/lists"
                    response = requests.post(request, json=data, headers=headers)

            if already_existing:
                continue
        if already_existing:
            continue
    if already_existing:
        continue
    request = gitlab_url + projects_api_url + str(destination_id) + "/boards"
    Log_info(f"post_request is: {request}")
    Log_info(f"data is: {data}")
    response = requests.post(request, json=data, headers=headers)
    Log_info(response.status_code)
    Log_info(response.reason)