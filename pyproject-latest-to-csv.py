# /// script
# dependencies = ["duckdb"]
# ///

"""

Originally from https://framapiaf.org/@fcodvpt/111540079686191842
https://gitlab.liris.cnrs.fr/fconil-small-programs/packaging/get-pypi-packages-backends
https://sethmlarson.dev/security-developer-in-residence-weekly-report-18
https://gist.github.com/sethmlarson/852341a9b7899eda7d22d8c362c0a095

    curl -L --remote-name-all $(curl -L "https://github.com/pypi-data/data/raw/main/links/dataset.txt")

MIT licensed.
"""

import duckdb

ALL_VERSIONS_QUERY = """SELECT project_name, COUNT(project_name) AS nb_uploads,
  MAX(project_version) AS max_version, 
  LIST(DISTINCT project_version) AS all_versions,
  MAX(uploaded_on) AS max_uploaded_on, 
  LIST(DISTINCT uploaded_on) AS all_uploaded_on,
  LIST(DISTINCT repository) AS all_repository,
  LIST(DISTINCT path) AS all_path
  FROM 'index-*.parquet'
  WHERE (date_part('year', uploaded_on) >= '2018') AND regexp_matches(path, 'pyproject.toml$') AND skip_reason == ''
  GROUP BY project_name;
"""

res = duckdb.sql(ALL_VERSIONS_QUERY)
res.to_csv("extract-pyproject-all-versions.csv", header=True)

LATEST_QUERY = """WITH lpv AS (SELECT project_name, COUNT(project_name) AS nb_uploads,
  MAX(uploaded_on) AS max_uploaded_on, 
  LIST(DISTINCT uploaded_on) AS all_uploaded_on
  FROM 'index-*.parquet'
  WHERE (date_part('year', uploaded_on) >= '2018') AND regexp_matches(path, 'pyproject.toml$') AND skip_reason == ''
  GROUP BY project_name)
SELECT ip.repository, ip.project_name, ip.project_version, lpv.nb_uploads, 
  ip.uploaded_on, date_part('year', ip.uploaded_on) AS year, ip.path
  FROM 'index-*.parquet' as ip
    JOIN lpv ON ip.project_name=lpv.project_name AND ip.uploaded_on=lpv.max_uploaded_on
  WHERE regexp_matches(path, 'pyproject.toml$') AND skip_reason == '';
"""

# res = duckdb.sql(LATEST_QUERY).show()

res = duckdb.sql(LATEST_QUERY)
res.to_csv("extract-pyproject-latest.csv", header=True)
