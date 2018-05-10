# local modules
from . import audio
from . import basics
from . import canvas
from . import font
from . import names
from . import scripts
from . import webgl
from . import webrtc


def aggregate_results(site, db_conn):
    """For each fingerprintable aspect, fetch the results."""

    fp_results = {
        "basics": basics.analyse(site, db_conn),
        "audio": audio.analyse(site, db_conn),
        "canvas": canvas.analyse(site, db_conn),
        "font": font.analyse(site, db_conn),
        "suspicious function names": names.analyse(site, db_conn),
        "scripts": scripts.analyse(site, db_conn),
        "webgl": webgl.analyse(site, db_conn),
        "webrtc": webrtc.analyse(site, db_conn),
    }

    return fp_results


def rate_fingerprinting(results, rater):
    """Rate the fingerprinting results.

    Takes a dictionary with the results, and a rater.
    The rater parameter should be a privacyscore.evaluation.rating.Rating.

    Returns a dictionary with a 'description' (str), 'classification' (Rating)
    and 'details_list' (list of typles).
    """

    # in case the rating fails (because of any changes to the dictionary
    # layout, for instance), we don't want to just crash, but print the
    # exception and tell the user that it failed.
    try:
        return _rate_fingerprinting(results, rater)
    except Exception as e:
        print(f"Exception {type(e)} in rate_fingerprinting: {e}")
        return {
            'description': 'Rating failed',
            'classification': rater('neutral'),
            'details_list': None,
        }


def _rate_fingerprinting(results, rater):
    if not results['fingerprinting']['success']:
        return {
            'description': 'Fingerprinting detection failed.',
            'classification': rater('neutral'),
            'details_list': None
        }

    fp_data = results['fingerprinting']['data']

    description = []
    details_list = []
    score = 0

    apis_used = 0

    if fp_data['audio']:
        apis_used += 1
        details_list.append(("Audio API",))
    if fp_data['webgl']:
        apis_used += 1
        details_list.append(("WebGL",))
    if fp_data['webrtc']:
        apis_used += 1
        details_list.append(("WebRTC",))

    if fp_data['canvas']['toDataURL calls'] > 0 \
       or fp_data['canvas']['getImageData calls'] > 0:
        apis_used += 1

    if fp_data['font']['fonts set']['count'] > 0 \
       or fp_data['font']['measureText calls']['count'] > 0:
        apis_used += 1

    if apis_used == 0:
        description.append("No fingerprintable APIs detected.")
    else:
        description.append(
            f"Usage of {apis_used} fingerprintable APIs detected."
        )

        score += int(apis_used / 2)

    # font
    fonts_set = fp_data['font']['fonts set']['count']
    measure_text_calls = fp_data['font']['measureText calls']['count']

    # mmmli value returns False or a List, hence this if-clause
    if fp_data['font']["'mmmmmmmmmmlli' magic string"]:
        mmmli = True
    else:
        mmmli = False

    # same as mmmli
    if fp_data['font']["'Cwm fjordbank glyphs vext quiz' magic string"]:
        fjordbank = True
    else:
        fjordbank = False

    if fonts_set > 5:
        description.append(f"{fonts_set} different fonts set.")

    if measure_text_calls > 0:
        description.append(f"Text measured {measure_text_calls} times.")
        details_list.append(("fonts API",))

    if measure_text_calls > 0 and fonts_set > 5:
        score += 1

    if mmmli:
        description.append(
            "'mmmmmmmmmmlli' magic string used (telltale sign of font fingerprinting)."
        )

        # dead giveaway
        score += 100

    if fjordbank:
        description.append(
            "'Cwm fjordbank glyphs vext quiz' magic string used (telltale sign of font fingerprinting)."
        )

        # dead giveaway
        score += 100

    # canvas
    tdu_calls = fp_data['canvas']['toDataURL calls']
    gid_calls = fp_data['canvas']['getImageData calls']

    if tdu_calls > 0:
        description.append(f"'toDataURL' called {tdu_calls} times.")
        # score += 1

    if gid_calls > 0:
        description.append(f"'getImageData' called {gid_calls} times.")
        # score += 1

    if tdu_calls + gid_calls > 0:
        details_list.append(("canvas API",))

    # suspicious function names
    names = fp_data['suspicious function names']['names']

    if len(names) > 0:
        description.append(f"{len(names)} suspicious function names found.")
        for name in names:
            details_list.append((name.split('.')[-1],))

        score += 1

    # known fingerprinting scripts
    scripts = fp_data['scripts']

    if len(scripts) > 0:
        description.append(
            f"{len(scripts)} known fingerprinting script(s) found."
        )

        for script in scripts:
            details_list.append((script,))

        # dead giveaway
        score += 100

    # basic attributes
    count = 0

    attrs = [
        "language",
        "platform",
        "userAgent",
        "colorDepth",
        "doNotTrack",
        "localStorage",
        "cookieEnabled",
        "sessionStorage"
    ]

    for attr in attrs:
        if fp_data['basics'][attr]:
            details_list.append((attr,))
            count += 1

    if count > 0:
        description.append(f"{count} fingerprintable attributes used.")
        score += 1

    # if count >= 7:
    #     score += 1

    rating = None

    if score >= 5:
        rating = rater("critical")
    elif score == 4:
        rating = rater("bad")
    elif score == 3:
        rating = rater("warning")
    elif score == 2:
        rating = rater("neutral")
    elif score == 1:
        rating = rater("good")
    elif score == 0:
        rating = rater("doubleplusgood")

    return {
        'description': ' '.join(description),
        'classification': rating,
        'details_list': details_list,
    }
