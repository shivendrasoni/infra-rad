import requests
from requests.auth import HTTPBasicAuth
import os
import json
import streamlit as st

@st.cache_data(ttl=500)
def get_jira_data(jql):
    # Replace with your Jira credentials
    email = os.getenv("JIRA_EMAIL")
    key = os.getenv("JIRA_API_KEY")
    url = "https://amberhq.atlassian.net/rest/api/3/search?expand=changelog"
    auth = HTTPBasicAuth(email, key)
    headers = {"Accept": "application/json"}

    results = []
    starts_at = 0
    max_results = 1000  # Use a reasonable limit like 1000; 10000 is too large and might be rejected by the server.

    while True:
        query = {
            'jql': jql,
            'startAt': starts_at,
            'maxResults': max_results
        }

        response = requests.get(
            url,
            headers=headers,
            params=query,
            auth=auth
        )
        max_results_in_response = response.json()['maxResults']
        data = response.json()
        results.extend(data['issues'])  # Assume 'issues' is the key containing the results

        # Check if there are more results to fetch
        if starts_at + max_results_in_response >= data['total']:
            break
        else:
            starts_at += max_results_in_response

    return results

#TODO: Find better way to utilize list of users
def get_jira_users():
    email = os.getenv("JIRA_EMAIL")
    key = os.getenv("JIRA_API_KEY")
    url = "https://amberhq.atlassian.net/rest/api/3/users/search"

    auth = HTTPBasicAuth(email, key)

    headers = {
        "Accept": "application/json"
    }

    results = []
    starts_at = 0
    max_results = 1000

    query = {
        'startAt': starts_at,
        'maxResults': max_results
    }
    response = requests.get(
        url,
        headers=headers,
        params=query,
        auth=auth
    )
    results = response.json()
    # return where result ['active'] == True and accountType = 'atlassian'
    results = [result for result in results if result['active'] == True and result['accountType'] == 'atlassian']
    return results

@st.cache_data(ttl=500)
def get_jira_sprints(boardId):

    url = f"https://amberhq.atlassian.net/rest/agile/1.0/board/{boardId}/sprint"

    email = os.getenv("JIRA_EMAIL")
    key = os.getenv("JIRA_API_KEY")

    auth = HTTPBasicAuth(email, key)
    headers = {"Accept": "application/json"}
    starts_at = 0
    max_results = 100

    results = []

    while True:
        query = {
            'startAt': starts_at,
            'maxResults': max_results
        }

        response = requests.get(
            url,
            headers=headers,
            params=query,
            auth=auth
        )
        max_results_in_response = response.json()['maxResults']
        data = response.json()
        results.extend(data['values'])  # Assume 'issues' is the key containing the results


        if max_results < data['total'] and (starts_at + max_results_in_response >= max_results):
            break
        # Check if there are more results to fetch
        if starts_at + max_results_in_response >= data['total']:
            break
        else:
            starts_at += max_results_in_response
    return results

@st.cache_data(ttl=500)
def get_issues_in_sprint(sprint_id):

    email = os.getenv("JIRA_EMAIL")
    key = os.getenv("JIRA_API_KEY")
    url = f"https://amberhq.atlassian.net/rest/agile/1.0/sprint/{sprint_id}/issue?expand=changelog&names"

    auth = HTTPBasicAuth(email, key)

    headers = {
        "Accept": "application/json"
    }

    starts_at = 0
    max_results = 1000

    query = {
        'startAt': starts_at,
        'maxResults': max_results
    }
    response = requests.get(
        url,
        headers=headers,
        params=query,
        auth=auth
    )
    return response.json()