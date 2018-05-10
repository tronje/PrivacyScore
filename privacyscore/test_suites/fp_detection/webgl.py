def analyse(site, db_conn):
    """Check for use of the WebGL API.

    Returns a list of scripts' URLs where the use occured, or False if
    WebGL was not used.
    """

    cursor = db_conn.cursor()

    uses_webgl = f"""
        SELECT DISTINCT javascript.script_url
        FROM javascript
            JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
        WHERE site_visits.site_url LIKE '{site}'
            AND javascript.symbol LIKE '%getcontext%'
            AND javascript.arguments LIKE '%webgl%';
    """

    cursor.execute(uses_webgl)

    urls = set()

    for row in cursor.fetchall():
        urls.add(row[0])

    if len(urls) > 0:
        return list(urls)
    else:
        return False
