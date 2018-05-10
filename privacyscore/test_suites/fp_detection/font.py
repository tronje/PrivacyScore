def analyse(site, db_conn):
    """Check for fingerprintable font use.

    Checks for how many fonts were set, how many times `measureText` was
    called, and if any know magic strings related to fingerprinting were used.

    Returns a dictionary containing the information for each of those
    aspects of font fingerprinting.
    """

    cursor = db_conn.cursor()

    fa = FontAnalyser(site, cursor)

    return {
        "fonts set": fa.fonts_set(),
        "measureText calls": fa.measure_text_calls(),
        "'mmmmmmmmmmlli' magic string": fa.mmmlli(),
        "'Cwm fjordbank glyphs vext quiz' magic string": fa.fjordbank(),
    }


class FontAnalyser(object):
    """As we need to perform multiple queries to test for font fingerprinting,
    we take an object-oriented approach with this class.
    """

    def __init__(self, site, cursor):
        """FontAnalyser takes a site (URL) and a cursor object
        to be reused by all its methods.
        """

        self.site = site
        self.cursor = cursor

    def fonts_set(self):
        """Check how many fonts were set.

        Returns a dictionary with the fonts set count and a list of URLs
        to scripts where the fonts were set, if any.
        """

        query = f"""
            SELECT javascript.script_url
            FROM javascript
              JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
            WHERE site_visits.site_url LIKE '{self.site}'
              AND javascript.symbol LIKE '%font'
              AND javascript.operation LIKE 'set';
        """
        self.cursor.execute(query)

        count = 0
        urls = set()
        for row in self.cursor.fetchall():
            count += 1
            urls.add(row[0])

        return {
            "count": count,
            "script urls": list(urls),
        }

    def measure_text_calls(self):
        """Check how many times `measureText` was called.

        Returns a dictionary with the count and the URLs of the scripts
        where they occured, if any.
        """

        query = f"""
            SELECT javascript.script_url
            FROM javascript
              JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
            WHERE site_visits.site_url LIKE '{self.site}'
              AND symbol LIKE 'CanvasRenderingContext2D.measureText';
        """
        self.cursor.execute(query)

        count = 0
        urls = set()
        for row in self.cursor.fetchall():
            count += 1
            urls.add(row[0])

        return {
            "count": count,
            "script urls": list(urls),
        }

    def mmmlli(self):
        """Check if the 'mmmmmmmmmmlli' magic string was used.

        If it was used, returns a list of URLs of the scripts where it was
        used. If it was not used, returns False.
        """

        query = f"""
            SELECT javascript.script_url
            FROM javascript
              JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
            WHERE site_visits.site_url LIKE '{self.site}'
              AND javascript.arguments LIKE '%mmmmmmmmmmlli%';
        """
        self.cursor.execute(query)

        urls = set()
        for row in self.cursor.fetchall():
            urls.add(row[0])

        if len(urls) > 0:
            return list(urls)
        else:
            return False

    def fjordbank(self):
        """Check if the 'Cwm fjordbank [...]' magic string/pangram was used.

        Returns a list of scripts' URLs where the string was used,
        or False if it was not used.
        """

        query = f"""
            SELECT javascript.script_url
            FROM javascript
              JOIN site_visits
                ON javascript.visit_id = site_visits.visit_id
            WHERE site_visits.site_url LIKE '{self.site}'
              AND javascript.arguments LIKE '%Cwm fjordbank glyphs vext quiz%';
        """
        self.cursor.execute(query)

        urls = set()
        for row in self.cursor.fetchall():
            urls.add(row[0])

        if len(urls) > 0:
            return list(urls)
        else:
            return False
