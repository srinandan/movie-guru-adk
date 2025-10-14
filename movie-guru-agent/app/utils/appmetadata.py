# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pg8000.dbapi
from app.utils import envvars


def select_app_metadata(app_version: str) -> dict | None:
    """
    Retrieves app metadata from the database for a given app version.

    Args:
        app_version: The version of the app to retrieve metadata for.

    Returns:
        A dictionary representing the fetched row from the database, or None.
    """
    try:
        conn = pg8000.dbapi.connect(
            user="postgres",
            password=envvars.DB_PASSWORD,
            host=envvars.DB_HOST,
            database=envvars.DB_NAME,
            port=5432
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM app_metadata WHERE app_version = %s LIMIT 1", (
                app_version,)
        )
        row = cursor.fetchone()
        if row and cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            results = dict(zip(column_names, row))
        else:
            results = None
        conn.close()
        return results
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
