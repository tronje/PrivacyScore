def analyse(site, db_conn):
    """Check for fingerprintable use of the Canvas API.

    Fingerprintable function calls are `toDataURL` and `getImageData`.

    Returns a dictionary with the number of calls to each function
    and the URLs of the scripts where they occur, if any.
    """

    cursor = db_conn.cursor()

    query = f"""
        SELECT javascript.symbol, javascript.script_url
        FROM javascript
            JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
        WHERE site_visits.site_url LIKE '{site}'
            AND (javascript.symbol LIKE 'CanvasRenderingContext2D.getImageData'
                OR javascript.symbol LIKE 'HTMLCanvasElement.toDataURL');
    """

    cursor.execute(query)

    todataurl_calls = 0
    getimagedata_calls = 0

    urls = set()

    for row in cursor.fetchall():
        symbol = row[0]
        url = row[1]

        urls.add(url)

        if symbol == 'HTMLCanvasElement.toDataURL':
            todataurl_calls += 1

        if symbol == 'CanvasRenderingContext2D.getImageData':
            getimagedata_calls += 1

    return {
        'toDataURL calls': todataurl_calls,
        'getImageData calls': getimagedata_calls,
        'script urls': list(urls),
    }
