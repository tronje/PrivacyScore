# suspicious function names
# all lower case because SQLite's `LIKE` is not case sensitive
suspicious_names = [
    '%fingerprint%',
    '%fingerprint%',
    '%getfingerprint%',
    '%getfp%',
    '%getcanvasfp%',
    '%getcanvasprint%',
    '%getcanvasfingerprint%',
    '%getaudioprint%',
    '%getaudiofingerprint%',
    '%gethaslied%',  # Fingerprintjs2
]


def analyse(site, db_conn):
    """Check for any suspicious function names, such as `getFingerprint`.

    Returns a dictionary with the names found and the script URLs where
    they were found.
    """

    cursor = db_conn.cursor()

    query = """
        SELECT javascript.func_name, javascript.script_url
        FROM javascript
            JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
        WHERE site_visits.site_url LIKE '{site}'
            AND javascript.func_name LIKE '{name}';
    """

    found_names = set()
    urls = set()

    for name in suspicious_names:
        cursor.execute(query.format(site=site, name=name))

        for row in cursor.fetchall():
            found_names.add(row[0])
            urls.add(row[1])

    return {
        'names': list(found_names),
        'script urls': list(urls),
    }
