def analyse(site, db_conn):
    """Check for the use of the Audio API.

    Returns a list of URLs where the API is used,
    or False if it is not used.
    """

    cursor = db_conn.cursor()

    query = f"""
        SELECT DISTINCT javascript.script_url
        FROM javascript
            JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
        WHERE site_visits.site_url LIKE '{site}'
            AND (javascript.symbol LIKE '%audio%'
                 OR javascript.symbol LIKE 'AnalyserNode%'
                 OR javascript.symbol LIKE 'GainNode%'
                 OR javascript.symbol LIKE 'OscillatorNode%'
                 OR javascript.symbol LIKE 'ScriptProcessorNode%');
    """

    cursor.execute(query)

    urls = set()

    for row in cursor.fetchall():
        urls.add(row[0])

    if len(urls) > 0:
        return list(urls)
    else:
        return False
