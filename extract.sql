COPY (
WITH latest_dates AS (
  WITH
    lpv AS (
      SELECT
        project AS project_name, download_count
      FROM
        'top-pypi-2024-05.json')
  SELECT
    lpv.project_name,
    ip.project_version,
    MAX(ip.uploaded_on) as uploaded_on,
    lpv.download_count, COUNT(*) AS file_count,
    ROW_NUMBER() OVER (PARTITION BY lpv.project_name ORDER BY MAX(ip.uploaded_on) DESC) AS row_num
  FROM
    'index-*.parquet' as ip
  JOIN
    lpv ON (LOWER(REPLACE(REPLACE(ip.project_name, '_', '-'), '.', '-')))=lpv.project_name
  WHERE
    regexp_matches(path, 'METADATA$') AND skip_reason == ''
  GROUP BY
    lpv.project_name, ip.project_version, lpv.download_count
  )
SELECT
  project_name, project_version, uploaded_on, download_count, file_count
FROM
  latest_dates
WHERE
  row_num = 1
) TO 'extract-filecount-latest.csv' (HEADER);

