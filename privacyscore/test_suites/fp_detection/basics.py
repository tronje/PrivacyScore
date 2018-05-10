def analyse(site, db_conn):
    """Check for the use of basic fingerprintable attributes.

    These are:
        userAgent
        colorDepth
        localStorage
        sessionStorage
        platform
        cookieEnabled
        doNotTrack
        oscpu

    Return a dictionary which, for each attribute, indicates whether
    it is used or not.
    """

    cursor = db_conn.cursor()

    query = f"""
        SELECT DISTINCT symbol
        FROM javascript
            JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
        WHERE site_visits.site_url LIKE '{site}'
            AND (symbol LIKE '%userAgent%'
                 OR symbol LIKE '%language%'
                 OR symbol LIKE '%colorDepth%'
                 OR symbol LIKE '%localStorage%'
                 OR symbol LIKE '%sessionStorage%'
                 OR symbol LIKE '%platform%'
                 OR symbol LIKE '%cookieEnabled%'
                 OR symbol LIKE '%doNotTrack%'
                 OR symbol LIKE '%oscpu%');
    """

    cursor.execute(query)

    results = {
        'userAgent': False,
        'language': False,
        'colorDepth': False,
        'localStorage': False,
        'sessionStorage': False,
        'platform': False,
        'cookieEnabled': False,
        'doNotTrack': False,
        'oscpu': False,
    }

    for row in cursor.fetchall():
        for key in results.keys():
            if key in row[0]:
                results[key] = True

    return results
