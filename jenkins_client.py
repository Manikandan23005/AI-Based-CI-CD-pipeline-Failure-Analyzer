import os
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import json
import logging

class JenkinsClient:
    def __init__(self):
        self.url = os.environ.get('JENKINS_URL', 'http://localhost:8080')
        self.user = os.environ.get('JENKINS_USER', '')
        self.token = os.environ.get('JENKINS_TOKEN', '')
        self.auth = HTTPBasicAuth(self.user, self.token) if self.user and self.token else None

    def get_all_jobs(self):
        res = requests.get(f"{self.url}/api/json?tree=jobs[name,url]", auth=self.auth)
        res.raise_for_status()
        return res.json().get('jobs', [])

    def get_job_info(self, job_name):
        res = requests.get(f"{self.url}/job/{job_name}/api/json", auth=self.auth)
        res.raise_for_status()
        return res.json()

    def get_build_info(self, job_name, build_number):
        res = requests.get(f"{self.url}/job/{job_name}/{build_number}/api/json", auth=self.auth)
        res.raise_for_status()
        return res.json()

    def get_build_console_log(self, job_name, build_number):
        res = requests.get(f"{self.url}/job/{job_name}/{build_number}/consoleText", auth=self.auth)
        res.raise_for_status()
        return res.text

jenkins_client = JenkinsClient()
