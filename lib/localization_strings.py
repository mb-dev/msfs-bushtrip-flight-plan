import json

class LocalizationStrings:
    def __init__(self, file_path: str):
        with open(file_path, "r", encoding='utf-8') as file_contents:
            locPak = json.load(file_contents)
        self.strings = locPak['LocalisationPackage']['Strings']

    def translation_for(self, string_id):
        return self.strings[string_id]

    def is_translation_exists(self, string_id):
        return string_id in self.strings