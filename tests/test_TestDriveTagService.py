import csv
import os
import pandas as pd
import pytest

from app.models.tag import Tag
from app.models.testDriveTagInfo import TestDriveTagInfo
from app.services.testDriveTagService import TestDriveTagService


# --- Helper Fixtures ---

@pytest.fixture
def tmp_csv(tmp_path):
    """Provides a temporary CSV file path."""
    return tmp_path / "tags.csv"


@pytest.fixture
def tag_service():
    """Provides an instance of TestDriveTagService."""
    return TestDriveTagService()


@pytest.fixture
def test_drive_info(tmp_csv):
    """
    Provides a TestDriveTagInfo instance with the tag_file_full_path
    set to the temporary CSV file.
    """
    # Assuming TestDriveTagInfo accepts tag_file_full_path as a parameter.
    return TestDriveTagInfo(tag_file_full_path=str(tmp_csv))


def create_csv_with_tags(file_path: str, tags: list):
    """
    Helper function to create a CSV file from a list of Tag instances.
    """
    df = pd.DataFrame([tag.model_dump() for tag in tags])
    df.to_csv(file_path, index=False, quoting=csv.QUOTE_NONNUMERIC)


# --- Tests ---

def test_get_all_tags_empty(tmp_csv, tag_service, test_drive_info):
    """
    When the CSV file exists but contains only headers, get_all_tags should return an empty list.
    """
    # Create CSV with header row (simulate a file with no data).
    columns = ["id", "guid", "timestamp_start_s", "timestamp_end_s", "category", "notes"]
    pd.DataFrame(columns=columns).to_csv(tmp_csv, index=False, quoting=csv.QUOTE_NONNUMERIC)

    tags = tag_service.get_all_tags(test_drive_info)
    assert tags == []


def test_get_next_id_no_file(tmp_csv, tag_service):
    """
    When the file does not exist, _get_next_id should return 1.
    """
    if tmp_csv.exists():
        os.remove(tmp_csv)
    next_id = tag_service._get_next_id(str(tmp_csv))
    assert next_id == 1


def test_add_tag_creates_file(tmp_csv, tag_service, test_drive_info):
    """
    add_tag should create the CSV file if it doesn't exist and assign id 1.
    """
    if tmp_csv.exists():
        os.remove(tmp_csv)
    # Create a dummy tag (id value will be overwritten by add_tag)
    tag = Tag(id=0, timestamp_start_s=0.0, timestamp_end_s=0.0, category="test", notes="test")
    added_tag = tag_service.add_tag(test_drive_info, tag)
    assert added_tag.id == 1
    assert tmp_csv.exists()

    df = pd.read_csv(tmp_csv)
    assert len(df) == 1
    # Check that the id in the CSV is 1
    assert int(df.loc[0, "id"]) == 1


def test_add_tag_increment_id(tmp_csv, tag_service, test_drive_info):
    """
    If a tag already exists in the CSV, add_tag should assign the new tag an id equal to max(existing id) + 1.
    """
    # Create a CSV with one tag already (id=1)
    tag1 = Tag(id=1, timestamp_start_s=0.0, timestamp_end_s=0.0, category="first", notes="first tag")
    create_csv_with_tags(str(tmp_csv), [tag1])

    tag2 = Tag(id=0, timestamp_start_s=1.0, timestamp_end_s=1.0, category="second", notes="second tag")
    added_tag2 = tag_service.add_tag(test_drive_info, tag2)
    assert added_tag2.id == 2

    df = pd.read_csv(tmp_csv)
    assert len(df) == 2
    assert 2 in df["id"].values


def test_get_by_id(tmp_csv, tag_service, test_drive_info):
    """
    get_by_id should return the Tag with the requested id if it exists.
    """
    tag1 = Tag(id=1, timestamp_start_s=0.0, timestamp_end_s=0.0, category="first", notes="first tag")
    tag2 = Tag(id=2, timestamp_start_s=1.0, timestamp_end_s=1.0, category="second", notes="second tag")
    create_csv_with_tags(str(tmp_csv), [tag1, tag2])

    retrieved_tag = tag_service.get_by_id(test_drive_info, 2)
    assert retrieved_tag is not None
    assert retrieved_tag.id == 2
    assert retrieved_tag.category == "second"


def test_update_tag(tmp_csv, tag_service, test_drive_info):
    """
    update_tag should update an existing tag in the CSV.
    """
    tag1 = Tag(id=1, timestamp_start_s=0.0, timestamp_end_s=0.0, category="first", notes="first tag")
    create_csv_with_tags(str(tmp_csv), [tag1])

    # Create an updated tag with different data and a mismatched id.
    updated_tag = Tag(id=999, timestamp_start_s=2.0, timestamp_end_s=2.0, category="updated",
                      notes="updated tag")
    result = tag_service.update_tag(test_drive_info, 1, updated_tag)
    # update_tag should enforce the id to be 1.
    assert result.id == 1

    df = pd.read_csv(tmp_csv)
    row = df[df['id'] == 1].iloc[0]
    assert row['category'] == "updated"
    assert float(row['timestamp_start_s']) == 2.0


def test_delete_tag(tmp_csv, tag_service, test_drive_info):
    """
    delete_tag should remove the tag with the specified id from the CSV.
    """
    tag1 = Tag(id=1, timestamp_start_s=0.0, timestamp_end_s=0.0, category="first", notes="first tag")
    create_csv_with_tags(str(tmp_csv), [tag1])

    result = tag_service.delete_tag(test_drive_info, 1)
    assert result is True

    df = pd.read_csv(tmp_csv)
    # The CSV should have no record with id 1.
    assert 1 not in df["id"].values


def test_delete_tag_not_found(tmp_csv, tag_service, test_drive_info):
    """
    delete_tag should return False when trying to delete a non-existent tag.
    """
    tag1 = Tag(id=1, timestamp_start_s=0.0, timestamp_end_s=0.0, category="first", notes="first tag")
    create_csv_with_tags(str(tmp_csv), [tag1])

    result = tag_service.delete_tag(test_drive_info, 999)
    assert result is False
