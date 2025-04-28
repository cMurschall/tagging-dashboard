import csv
import logging
from typing import List, Optional
import pandas as pd
import re

from app.models.tag import Tag
from app.models.testDriveTagInfo import TestDriveTagInfo
from app.settings import Settings


class TestDriveTagService:
    def __init__(self, settings: Settings):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.settings = settings

    def _get_next_id(self, file_path: str, id_prefix="id_"):
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return f"{id_prefix}1"

            # Only keep IDs that match the pattern and are strings
            def extract_numeric_id(x):
                try:
                    match = re.search(r'\d+$', str(x))
                    return int(match.group()) if match else None
                except Exception as e:
                    self.logger.warning(f"Invalid ID format: {x} ({e})")
                    return None

            df['numeric_id'] = df['id'].apply(extract_numeric_id)
            df = df.dropna(subset=['numeric_id'])

            if df.empty:
                return f"{id_prefix}1"

            max_numeric_id = int(df['numeric_id'].max())
            next_numeric_id = max_numeric_id + 1
            return f"{id_prefix}{next_numeric_id}"

        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.logger.info("CSV file not found or empty; starting IDs at 1.")
            return f"{id_prefix}1"
        except Exception as e:
            self.logger.exception("Unexpected error when determining next ID: %s", e)
            raise

    # def _get_next_id(self, file_path: str) -> int:
    #     """
    #     Reads the CSV file and returns the next available integer ID (max id + 1).
    #     If the file does not exist or is empty, returns 1.
    #     """
    #     try:
    #         df = pd.read_csv(file_path)
    #         if df.empty or 'id' not in df.columns:
    #             self.logger.debug("CSV file is empty or missing 'id' column; starting IDs at 1.")
    #             return "id_1"
    #         next_id = int(df['id'].max()) + 1
    #         self.logger.debug("Current max ID is %d. Next ID will be %d.", int(df['id'].max()), next_id)
    #         return next_id
    #     except (FileNotFoundError, pd.errors.EmptyDataError):
    #         self.logger.info("CSV file not found or empty; starting IDs at 1.")
    #         return 1
    #     except Exception as e:
    #         self.logger.exception("Unexpected error when determining next ID: %s", e)
    #         raise

    def get_all_tags(self, info: TestDriveTagInfo) -> List[Tag]:
        file_path = info.tag_file_full_path
        self.logger.info("Retrieving all tags from file: %s", file_path)
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return []
            df["notes"] = df["notes"].fillna("")
            tags = [Tag(**row.to_dict()) for _, row in df.iterrows()]
            self.logger.debug("Retrieved %d tags.", len(tags))
            return tags
        except Exception as e:
            self.logger.exception("Error retrieving tags from %s", file_path)
            raise

    def get_by_id(self, info: TestDriveTagInfo, id: int) -> Optional[Tag]:
        file_path = info.tag_file_full_path
        self.logger.info("Retrieving tag with GUID %d from file: %s", id, file_path)
        try:
            df = pd.read_csv(file_path)
            tag_row = df[df['id'] == id]
            if not tag_row.empty:
                tag_obj = Tag(**tag_row.iloc[0].to_dict())
                self.logger.debug("Found tag: %s", tag_obj)
                return tag_obj
            self.logger.warning("Tag with Id %d not found.", id)
            return None
        except Exception as e:
            self.logger.exception("Error retrieving tag by ID %d", id)
            raise

    def add_tag(self, info: TestDriveTagInfo, tag: Tag) -> Tag:
        file_path = info.tag_file_full_path
        # Get the next integer id
        tag.id = self._get_next_id(file_path)
        self.logger.info("Assigning new tag ID %d", tag.id)

        # Optionally, you can still maintain a GUID if needed for other purposes
        # tag.guid = str(uuid.uuid4())

        self.logger.info("Adding new tag with ID %d to file: %s", tag.id, file_path)
        try:
            existing_df = pd.read_csv(file_path)
            self.logger.debug("Found existing CSV with %d records.", len(existing_df))
            new_df = pd.DataFrame([tag.model_dump()])
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.logger.info("CSV file not found or empty; creating a new CSV file.")
            combined_df = pd.DataFrame([tag.model_dump()])
        except Exception as e:
            self.logger.exception("Error reading CSV file %s", file_path)
            raise

        try:
            combined_df.to_csv(file_path, index=False, quoting=csv.QUOTE_NONNUMERIC)
            self.logger.info("Tag with ID %d successfully added.", tag.id)
        except Exception as e:
            self.logger.exception("Error writing to CSV file %s", file_path)
            raise

        return tag

    def update_tag(self, info: TestDriveTagInfo, id: str, updated_tag: Tag) -> Optional[Tag]:
        file_path = info.tag_file_full_path
        self.logger.info("Updating tag with Id %s in file: %s", id, file_path)
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            self.logger.exception("Error reading file %s", file_path)
            raise

        mask = df['id'] == id
        if mask.any():
            if updated_tag.id != id:
                self.logger.warning(
                    "Id mismatch: parameter '%d' does not match updated_tag.id '%d'. Enforcing parameter Id.",
                    id, updated_tag.id)
                updated_tag.id = id

            # df.loc[mask, :] = updated_tag.model_dump()
            df.loc[mask, :] = pd.DataFrame([updated_tag.model_dump()], index=df.index[mask])
            try:
                df.to_csv(file_path, index=False, header=True, quoting=csv.QUOTE_NONNUMERIC)
                self.logger.info("Tag with Id %d updated successfully.", id)
            except Exception as e:
                self.logger.exception("Error writing updated tag to CSV file %s", file_path)
                raise
            return updated_tag
        else:
            self.logger.error("Tag with Id %d not found for update.", id)
            raise ValueError(f"Tag with Id '{id}' not found in the CSV file.")

    def delete_tag(self, info: TestDriveTagInfo, id: str) -> bool:
        file_path = info.tag_file_full_path
        self.logger.info("Deleting tag with ID %d from file: %s", id, file_path)
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            self.logger.exception("Error reading file %s", file_path)
            raise

        initial_len = len(df)
        df = df[df['id'] != id]
        if len(df) < initial_len:
            try:
                df.to_csv(file_path, index=False, header=True, quoting=csv.QUOTE_NONNUMERIC)
                self.logger.info("Tag with Id %d deleted successfully.", id)
            except Exception as e:
                self.logger.exception("Error writing CSV file %s after deletion", file_path)
                raise
            return True
        else:
            self.logger.warning("Tag with Id %d not found. No deletion performed.", id)
            return False
