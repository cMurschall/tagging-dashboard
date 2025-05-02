import os.path

from app.models.testDriveTagInfo import TestDriveTagInfo


def analyze_tags(tag_info: TestDriveTagInfo) -> bool:
    file_path = tag_info.tag_file_full_path
    # check if file exists
    file_exists = os.path.isfile(file_path)
    if not file_exists:
        # create empty tag file
        with open(file_path, 'a') as f:
            pass

    return False  # no update needed
