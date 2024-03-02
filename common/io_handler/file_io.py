from datetime import date
import json
import os

from .io_handler import IOHandler


class FileIO(IOHandler):
    def __init__(self, data_dir_path: str) -> None:
        self.data_dir_path = data_dir_path
        self.current_date = date.today()

    def read(self) -> dict[str, dict]:
        filename = self.get_json_file_path()
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def write(self, data: dict[str, dict]):
        filename = self.get_json_file_path()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=True, indent=4)

    def get_json_file_path(self):
        json_file_path = os.path.join(self.data_dir_path, f"{self.current_date}.json")
        return json_file_path
