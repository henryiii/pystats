# /// script
# dependencies = ["aiohttp", "packaging"]
# ///

"""
Downloads all pyproject.toml files and puts them in a database. Doesn't talk to
GitHub if the file already is in the input CSV.

You need an input CSV to work on. To prepare one, you can use
pyproject-latest-to-csv.py.
"""

import asyncio
import contextlib
import csv
import itertools
import logging
import sqlite3
import sys
import time
from collections.abc import Iterator

import aiohttp

LOG = logging.getLogger(__name__)

PYPROJECT_CREATE = """CREATE TABLE IF NOT EXISTS
pyproject(project_name TEXT, project_version TEXT, contents TEXT,
          PRIMARY KEY (project_name, project_version))
"""

INSERT_CONTENTS = """INSERT INTO pyproject
VALUES (:project_name, :project_version, :contents)
"""

GET_CONTENTS = """SELECT project_version FROM pyproject WHERE project_name=?
"""
DELETE_CONTENTS = """DELETE FROM pyproject WHERE project_name=?
"""

csv.field_size_limit(sys.maxsize)


async def get_data(
    session: aiohttp.ClientSession, path: str, repo: int, name: str
) -> str | None:
    if path.count("/") != 4 or not path.endswith("/pyproject.toml"):
        LOG.warning("Project %s has non-top-level path %s", name, path)
        return None

    url = f"https://raw.githubusercontent.com/pypi-data/pypi-mirror-{repo}/code/{path}"
    try:
        async with session.get(url) as response:
            if response.status == 429:
                LOG.error("Rate limited when accessing %s", name)
                raise RuntimeError("Rate limited")
            if response.status != 200:
                LOG.error("pycodeorg.get_data failed to retrieve %s", name)
                return None
            try:
                data = await response.text()
            except UnicodeDecodeError:
                LOG.exception("Unicode decode error on %s", name)
                return None
            return data
    except (
        aiohttp.http_exceptions.BadHttpMessage,
        aiohttp.client_exceptions.ClientResponseError,
    ):
        LOG.exception("Failed reading %s", name)
        return None


async def worker(
    iterator: Iterator[str],
    session: aiohttp.ClientSession,
    cursor: sqlite3.Cursor,
    thread: int,
) -> None:
    with contextlib.suppress(StopIteration):
        for i in itertools.count(0):
            if i and i % 200 == 0:
                LOG.info("PROGRESS %d: %d", thread, i)
            line = next(iterator)
            with cursor.connection:
                result = cursor.execute(GET_CONTENTS, (line["project_name"],))
                if any(v[0] == line["project_version"] for v in result.fetchall()):
                    continue

            data = await get_data(
                session, line["path"], line["repository"], line["project_name"]
            )
            if not data:
                continue

            with cursor.connection:
                try:
                    cursor.execute(
                        INSERT_CONTENTS,
                        {
                            "project_name": line["project_name"],
                            "project_version": line["project_version"],
                            "contents": data,
                        },
                    )
                except Exception as e:
                    e.add_note(
                        f"{thread}:{i} {line['project_name']}=={line['project_version']} failed"
                    )
                    raise


async def main() -> None:
    with contextlib.closing(sqlite3.connect("pyproject_contents.db")) as cnx_backend:
        cur_backend = cnx_backend.cursor()
        cur_backend.execute(PYPROJECT_CREATE)

        with open("extract-pyproject-all-versions.csv", newline="") as f:
            reader = csv.DictReader(f)
            total = len(list(reader))

        print(f"Processing {total} projects")

        with open("extract-pyproject-latest.csv", newline="") as f:
            reader = csv.DictReader(f)
            iterator = iter(list(reader))
            async with aiohttp.ClientSession() as session, asyncio.TaskGroup() as tg:
                for i in range(16):
                    tg.create_task(worker(iterator, session, cur_backend, i))


if __name__ == "__main__":
    start_time = time.time()
    logging.basicConfig(filename="pyproject_contents.log", level=logging.INFO)

    asyncio.run(main())

    end_time = time.time()
    duration_msg = f"Getting files took: {end_time - start_time:0.3} seconds."

    LOG.info(duration_msg)
    print(duration_msg)
