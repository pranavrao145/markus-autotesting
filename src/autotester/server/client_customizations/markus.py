import os
import json
import markusapi
from typing import Dict
from autotester.server.client_customizations.client import Client
from autotester.server.utils.file_management import extract_zip_stream
from autotester.exceptions import TestScriptFilesError


class MarkUs(Client):
    client_type = 'markus'

    def __init__(self, **kwargs):
        self.url = kwargs.get("url")
        self.api_key = kwargs.get("api_key")
        self.assignment_id = kwargs.get("assignment_id")
        self.group_id = kwargs.get("group_id")
        self.run_id = kwargs.get("run_id")
        self.user_type = kwargs.get("user_type")
        self._api = markusapi.Markus(self.api_key, self.url)

    def write_test_files(self, destination: str) -> None:
        zip_content = self._api.get_test_files(self.assignment_id)
        if zip_content is None:
            raise TestScriptFilesError('No test files found')
        extract_zip_stream(zip_content, destination, ignore_root_dir=True)

    def get_test_specs(self) -> Dict:
        return self._api.get_test_specs(self.assignment_id)

    def write_student_files(self, destination: str) -> None:
        collected = self.user_type == "Admin"
        zip_content = self._api.get_files_from_repo(self.assignment_id, self.group_id, collected=collected)
        if zip_content is None:
            raise TestScriptFilesError('No test files found')
        extract_zip_stream(zip_content, destination, ignore_root_dir=True)

    def send_test_results(self, results_data: Dict) -> None:
        self._api.upload_test_group_results(
            self.assignment_id, self.group_id, self.run_id, json.dumps(results_data)
        )

    def unique_script_str(self) -> str:
        return "_".join([self.client_type, self.url, str(self.assignment_id)])

    def unique_run_str(self) -> str:
        return "_".join([self.unique_script_str(), str(self.run_id)])

    def upload_feedback_to_repo(self, feedback_file: str) -> None:
        """
        Upload the feedback file to the group's repo.
        """
        if os.path.isfile(feedback_file):
            with open(feedback_file) as feedback_open:
                self._api.upload_file_to_repo(
                    self.assignment_id, self.group_id, os.path.basename(feedback_file), feedback_open.read()
                )

    def upload_feedback_file(self, feedback_file: str) -> None:
        """
        Upload the feedback file using MarkUs' api.
        """
        if os.path.isfile(feedback_file):
            with open(feedback_file) as feedback_open:
                self._api.upload_feedback_file(
                    self.assignment_id, self.group_id, os.path.basename(feedback_file), feedback_open.read()
                )

    def upload_annotations(self, annotation_file: str) -> None:
        """
        Upload annotations using MarkUs' api.
        """
        if os.path.isfile(annotation_file):
            with open(annotation_file) as annotations_open:
                self._api.upload_annotations(self.assignment_id, self.group_id, json.load(annotations_open))