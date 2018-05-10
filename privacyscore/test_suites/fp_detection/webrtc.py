def analyse(site, db_conn):
    """Check for use of the WebRTC API.

    Returns a dictionary with usage details or False if WebRTC was not used."""

    cursor = db_conn.cursor()

    uses_webgl = f"""
        SELECT DISTINCT javascript.symbol, javascript.script_url
        FROM javascript
            JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
        WHERE site_visits.site_url LIKE '{site}'
            AND javascript.symbol LIKE 'RTCPeerConnection%';
    """

    cursor.execute(uses_webgl)
    onicecandidate = False
    urls = set()

    for row in cursor.fetchall():
        if "onicecandidate" in row[0]:
            onicecandidate = True

        urls.add(row[1])

    if len(urls) > 0:
        return {
            "uses WebRTC": True,
            "uses onicecandidate": onicecandidate,
            "script urls": list(urls),
        }
    else:
        return False
