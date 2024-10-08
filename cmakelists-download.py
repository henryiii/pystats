# /// script
# dependencies = ["aiohttp", "packaging"]
# ///

"""
Downloads all CMakeLists.txt files and puts them in a database. Doesn't talk to
GitHub if the file already is in the input CSV.

You need an input CSV to work on. To prepare one, you can use
cmakelists-latest-to-csv.py.
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

CMAKELISTS_CREATE = """CREATE TABLE IF NOT EXISTS
cmakelists(project_name TEXT, project_version TEXT, path TEXT, contents TEXT,
          PRIMARY KEY (project_name, project_version, path))
"""

INSERT_CONTENTS = """INSERT INTO cmakelists
VALUES (:project_name, :project_version, :path, :contents)
"""

GET_CONTENTS = """SELECT project_version FROM cmakelists WHERE project_name=? AND path=?
"""
DELETE_CONTENTS = """DELETE FROM cmakelists WHERE project_name=?
"""

csv.field_size_limit(sys.maxsize)


async def get_data(
    session: aiohttp.ClientSession, path: str, repo: int, name: str
) -> str | None:
    if not path.endswith("/CMakeLists.txt"):
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
                data = await response.text(encoding="utf-8-sig")
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
                result = cursor.execute(
                    GET_CONTENTS, (line["project_name"], line["path"])
                )
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
                            "path": line["path"],
                            "contents": data,
                        },
                    )
                except sqlite3.IntegrityError as err:
                    err.add_notes(line)
                    raise


async def main() -> None:
    with contextlib.closing(sqlite3.connect("cmakelists_contents.db")) as cnx_backend:
        cur_backend = cnx_backend.cursor()
        cur_backend.execute(CMAKELISTS_CREATE)

        with open("extract-cmakelists-all-versions.csv", newline="") as f:
            reader = csv.DictReader(f)
            total = len(list(reader))

        print(f"Processing {total} projects")

        with open("extract-cmakelists-latest.csv", newline="") as f:
            reader = csv.DictReader(f)
            iterator = iter(list(reader))
            async with aiohttp.ClientSession() as session, asyncio.TaskGroup() as tg:
                for i in range(16):
                    tg.create_task(worker(iterator, session, cur_backend, i))


if __name__ == "__main__":
    start_time = time.time()
    logging.basicConfig(filename="cmakelists_contents.log", level=logging.INFO)

    asyncio.run(main())

    end_time = time.time()
    duration_msg = f"Getting files took: {end_time - start_time:0.3} seconds."

    LOG.info(duration_msg)
    print(duration_msg)
