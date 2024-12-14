from utils_python.utils_python_package.src.Apoeschllogging import *

import argparse
import requests

parser = argparse.ArgumentParser(description="copy labels from gitlab repo to gitlab repo")
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
request = gitlab_url + projects_api_url + str(source_id) + "/labels?with_counts=true"
Log_info(f"get_request is: {request}")
source_labels = requests.get(request, headers=headers)
dict_source_labels = source_labels.json()
request = gitlab_url + projects_api_url + str(destination_id) + "/labels?with_counts=true"
destination_labels = requests.get(request, headers=headers)
dict_destination_labels = destination_labels.json()
for source_label in dict_source_labels:
    already_existing = False
    for destination_label in dict_destination_labels:
        if source_label["name"] == destination_label["name"]:
            already_existing = True
            continue
    if already_existing:
        continue
    data = {
        "name":source_label["name"],
        "color":source_label["color"]
    }
    request = gitlab_url + projects_api_url + str(destination_id) + "/labels"
    Log_info(f"post_request is: {request}")
    Log_info(f"data is: {data}")
    response = requests.post(request, json=data, headers=headers)
    Log_info(response.status_code)
    Log_info(response.reason)