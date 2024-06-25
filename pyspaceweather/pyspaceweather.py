"""
pyspaceweather is a Python wrapper for the Australian Bureau of Meterology's
Space Weather API.
"""

from collections import namedtuple
from datetime import datetime

import requests


class SpaceWeather:
    """The SpaceWeather API.

    A class to interact with the Space Weather API, providing methods
    to retrieve various space weather data for the Australian region.

    Attributes
    ----------
    api_key : str
        The API key for authenticating with the Space Weather API.

    Methods
    -------
    get_aurora_outlook():
        Get details of any aurora outlook current for the Australian region.
    get_aurora_watch():
        Get details of any aurora watch current for the Australian region.
    get_aurora_alert():
        Get details of any aurora alert current for the Australian region.
    get_mag_alert():
        Get details of any magnetic alert current for the Australian region.
    get_mag_warning():
        Get details of any geophysical warning currently active for the Australian region.
    get_a_index(start="", end=""):
        Get the most recent A index for the Australian region, or historical values.
    get_k_index(start="", end="", location=None):
        Get the most recent K index from a specific location, or historical values.
    get_dst_index(start="", end=""):
        Get the most recent Dst index for the Australian region, or historical values.
    """

    def __init__(self, api_key):
        self._headers = {"Content-Type": "application/json; charset=UTF-8"}
        self.api_key = self._verify_api_key(api_key)
        self._time_format = "%Y-%m-%d"
        self._time_format_with_minutes = "%Y-%m-%d %H:%M:%S"

    def _verify_api_key(self, api_key):
        """
        Verify the API key is valid.

        Parameters
        ----------
        api_key : str
            The API key to be verified.

        Returns
        -------
        str
            The validated API key.

        Raises
        ------
        ValueError
            If the API key is invalid.
        """
        request_body = {
            "api_key": api_key,
            "options": {"location": "Australian region"},
        }
        response = requests.post(
            "https://sws-data.sws.bom.gov.au/api/v1/get-k-index",
            timeout=15,
            headers=self._headers,
            json=request_body,
        )
        if response.status_code == 403:
            raise ValueError("HTTP Error 403 - please pass a valid API key.")
        response.raise_for_status()
        return api_key

    def _get_aurora(self, aurora_type):
        """
        Get aurora data based on the specified type.

        Parameters
        ----------
        aurora_type : str
            The type of aurora data to retrieve ('outlook', 'watch', or 'alert').

        Returns
        -------
        list
            A list of aurora data objects.
        """
        response = requests.post(
            f"https://sws-data.sws.bom.gov.au/api/v1/get-aurora-{aurora_type}",
            timeout=15,
            headers=self._headers,
            json={
                "api_key": self.api_key,
            },
        )
        if response.status_code != 200:
            raise requests.HTTPError(response.json())
        if data := response.json()["data"]:
            auroras = []
            for aurora in data:
                # Convert date/time strings to datetime objects.
                time_periods = {
                    "issue_time": "",
                    "start_date": "",
                    "end_date": "",
                    "start_time": "",
                    "valid_until": "",
                }
                for time_period in time_periods.keys():
                    try:
                        try:
                            time = datetime.strptime(
                                aurora[time_period], self._time_format_with_minutes
                            )
                            time_periods[time_period] = time
                        except ValueError:  # Wrong time format code.
                            time = datetime.strptime(
                                aurora[time_period], self._time_format
                            )
                            time_periods[time_period] = time
                    except KeyError:  # Time period not present in the data.
                        pass

                # Create instances of data classes.
                if aurora_type == "outlook":
                    outlook = AuroraOutlook(
                        time_periods.get("issue_time"),
                        time_periods.get("start_date"),
                        time_periods.get("end_date"),
                        aurora["cause"],
                        aurora["k_aus"],
                        aurora["lat_band"],
                        aurora["comments"],
                    )
                    auroras.append(outlook)
                elif aurora_type == "watch":
                    watch = AuroraWatch(
                        time_periods.get("issue_time"),
                        time_periods.get("start_date"),
                        time_periods.get("end_date"),
                        aurora["cause"],
                        aurora["k_aus"],
                        aurora["lat_band"],
                        aurora["comments"],
                    )
                    auroras.append(watch)
                elif aurora_type == "alert":
                    alert = AuroraAlert(
                        time_periods.get("start_time"),
                        time_periods.get("valid_until"),
                        aurora["k_aus"],
                        aurora["lat_band"],
                        aurora["description"],
                    )
                    auroras.append(alert)
            return auroras
        return []

    def get_aurora_outlook(self):
        """
        Get details of any aurora outlook current for the Australian region.
        Aurora outlooks are used to warn of likely auroral activity 3-7 days
        hence.

        Returns
        -------
        list
            A list of AuroraOutlook objects.
        """
        return self._get_aurora("outlook")

    def get_aurora_watch(self):
        """
        Get details of any aurora watch current for the Australian region.
        Aurora watches are used to warn of likely auroral activity in the next
        48 hours.

        Returns
        -------
        list
            A list of AuroraWatch objects.
        """
        return self._get_aurora("watch")

    def get_aurora_alert(self):
        """
        Get details of any aurora alert current for the Australian region.
        Aurora alerts are used to report geomagnetic activity currently in
        progress and favourable for auroras.

        Returns
        -------
        list
            A list of AuroraAlert objects.
        """
        return self._get_aurora("alert")

    def get_mag_alert(self):
        """Get details of any magnetic alert current for the Australian region.

        Returns
        -------
        list
            A list of MagAlert objects.
        """
        response: requests.Response = requests.post(
            "https://sws-data.sws.bom.gov.au/api/v1/get-mag-alert",
            timeout=15,
            headers=self._headers,
            json={"api_key": self.api_key},
        )
        if response.status_code != 200:
            raise requests.HTTPError(response.json())
        if data := response.json()["data"]:
            mag_alerts = []
            for mag_alert in data:
                # Convert date/time strings to datetime objects.
                for time_period in ("start_time", "valid_until"):
                    try:
                        time = datetime.strptime(
                            mag_alert[time_period], self._time_format_with_minutes
                        )
                        mag_alert[time_period] = time
                    except KeyError:
                        mag_alert[time_period] = None
                mag_alert = MagAlert(
                    mag_alert["start_time"],
                    mag_alert["valid_until"],
                    mag_alert["g_scale"],
                    mag_alert["description"],
                )
                mag_alerts.append(mag_alert)
            return mag_alerts
        return []

    def get_mag_warning(self):
        """Get details of any geophysical warning currently active for the
        Australian region.

        Returns
        -------
        list
            A list of MagWarning objects.

        """
        response = requests.post(
            "https://sws-data.sws.bom.gov.au/api/v1/get-mag-warning",
            timeout=15,
            headers=self._headers,
            json={"api_key": self.api_key},
        )
        if response.status_code != 200:
            raise requests.HTTPError(response.json())
        if data := response.json()["data"]:
            mag_warnings = []
            for mag_warning in data:
                # Convert date/time strings to datetime objects.
                time_periods = {
                    "issue_time": "",
                    "start_date": "",
                    "end_date": "",
                }
                for time_period in time_periods.keys():
                    try:
                        try:
                            time = datetime.strptime(
                                mag_warning[time_period], self._time_format_with_minutes
                            )
                            time_periods[time_period] = time
                        except ValueError:  # Wrong time format code.
                            time = datetime.strptime(
                                mag_warning[time_period], self._time_format
                            )
                            time_periods[time_period] = time
                    except KeyError:  # Empty value.
                        time_periods[time_period] = None

                # Create list of dictionaries for each day of the warning period.
                days = [
                    {
                        datetime.strptime(
                            day_period["date"], self._time_format
                        ): day_period["forecast"]
                    }
                    for day_period in mag_warning["activity"]
                ]
                # Create dataclasses.
                mag_warning = MagWarning(
                    time_periods.get("issue_time"),
                    time_periods.get("start_date"),
                    time_periods.get("end_date"),
                    mag_warning["cause"],
                    days,
                    mag_warning["comments"],
                )
                mag_warnings.append(mag_warning)
            return mag_warnings
        return []

    def _get_index(
        self,
        index_type,
        start,
        end,
        location,
    ):
        """
        Get index data based on the specified type.

        Parameters
        ----------
        index_type : str
            The type of index data to retrieve ('a-index', 'k-index', or 'dst-index').
        start : str or datetime
            The starting time for the data retrieval.
        end : str or datetime
            The ending time for the data retrieval.
        location : str
            The location for which the data is required.

        Returns
        -------
        list
            A list of index data objects.

        Raises
        ------
        ValueError
            If the provided start or end time format is incorrect.
        requests.HTTPError
            If the API request fails.
        """
        # Check start and end arguments.
        if isinstance(start, datetime):
            start = datetime.strftime(start, self._time_format_with_minutes)
        else:
            if start != "":
                try:
                    datetime.strptime(start, self._time_format_with_minutes)
                except ValueError as error:
                    raise ValueError(
                        """Please provide a string in the format
                            YYYY-MM-DD HH:mm:ss or a datetime object."""
                    ) from error
        if isinstance(end, datetime):
            end = datetime.strftime(end, self._time_format_with_minutes)
        else:
            if end != "":
                try:
                    datetime.strptime(end, self._time_format_with_minutes)
                except ValueError as error:
                    raise ValueError(
                        """Please provide a string in the format
                            YYYY-MM-DD HH:mm:ss or a datetime object."""
                    ) from error

        # Call the API.
        response = requests.post(
            f"https://sws-data.sws.bom.gov.au/api/v1/get-{index_type}",
            timeout=15,
            headers=self._headers,
            json={
                "api_key": self.api_key,
                "options": {
                    "location": location,
                    "start": start,
                    "end": end,
                },
            },
        )
        if response.status_code != 200:
            raise requests.HTTPError(response.json())

        # Parse response.
        if response.json()["data"]:
            if index_type in ("a-index", "dst-index"):
                data = response.json()["data"][0]
            else:
                data = response.json()["data"]
            indexes = []
            for index_data in data:
                if index_type == "k-index":
                    k_index = KIndex(
                        datetime.strptime(
                            index_data["valid_time"], self._time_format_with_minutes
                        ),
                        datetime.strptime(
                            index_data["analysis_time"], self._time_format_with_minutes
                        ),
                        index_data["index"],
                    )
                    indexes.append(k_index)
                elif index_type == "a-index":
                    a_index = AIndex(
                        datetime.strptime(
                            index_data["valid_time"], self._time_format_with_minutes
                        ),
                        index_data["index"],
                    )
                    indexes.append(a_index)
                else:
                    dst_index = DstIndex(
                        datetime.strptime(
                            index_data["valid_time"], self._time_format_with_minutes
                        ),
                        index_data["index"],
                    )
                    indexes.append(dst_index)
            return indexes
        return []

    def get_a_index(self, start="", end=""):
        """
        Get the most recent A index for the Australian region,
        or historical values.

        Parameters
        ----------
        start: str or datetime, optional
                The optional UTC starting time (YYYY-MM-DD HH:mm:ss)
                from which historical A index data is required.
        end:  str or datetime, optional
                The optional UTC ending valid_time (YYYY-MM-DD HH:mm:ss)
                before which historical A index data is required.

        Returns
        -------
        list
            A list of AIndex objects.

        """
        return self._get_index("a-index", start, end, "Australian region")

    def get_k_index(self, start="", end="", location=None):
        """
        Get the most recent K index from a specific location, or
        historical values.

        Parameters
        ----------
        start: str or datetime, optional
                The optional UTC starting time (YYYY-MM-DD HH:mm:ss)
                from which historical K index data is required.
        end: str or datetime, optional
                The optional UTC ending time (YYYY-MM-DD HH:mm:ss)
                before which historical K index data is required.
        location: str, optional
                The location for which the K index data is required.
                Australian region, or an Australian region observing site.

        Returns
        -------
        list
            A list of KIndex objects.
        """

        if location is None:
            return self._get_index("k-index", start, end, "Australian region")
        return self._get_index("k-index", start, end, location)

    def get_dst_index(self, start="", end=""):
        """
        Get the the most recent Dst index for the Australian region,
        or historical values.

        Parameters
        ----------
        start: str or datetime, optional
                The optional UTC starting time (YYYY-MM-DD HH:mm:ss)
                from which historical Dst index data is required.
        end: str or datetime, optional
                The optional UTC ending time (YYYY-MM-DD HH:mm:ss)
                before which historical Dst index data is required.

        Returns
        -------
        list
            A list of DstIndex objects.
        """
        return self._get_index("dst-index", start, end, "Australian region")


# Data classes.
AuroraOutlook = namedtuple(
    "AuroraOutlook",
    ["issue_time", "start_time", "end_date", "cause", "k_aus", "lat_band", "comments"],
)
AuroraOutlook.__doc__ = """
An aurora outlook current for the Australian region.
Aurora outlooks are used to warn of likely auroral activity 3-7 days hence.

Attributes
----------
issue_time : datetime
    The time (UTC) at which the outlook was issued.
start_date : datetime
    The first day (UTC) to which the outlook applies.
end_date : datetime
    The last day (UTC) to which the outlook applies.
cause : str
    The dominant cause of the likely auroral activity. One of: coronal
    hole, coronal mass ejection.
k_aus : int
    If available, the expected level of the auroral activity, according
    to the Australian region K index (0-9).
lat_band : str
    If available, the latitude band from which auroral activity is likely
    to be visible, based on the value of k_aus.
    One of: high, mid, low, equatorial.
comments : str
    Comments provided by the duty forecaster.
"""

AuroraWatch = namedtuple(
    "AuroraWatch",
    ["issue_time", "start_date", "end_date", "cause", "k_aus", "lat_band", "comments"],
)
AuroraWatch.__doc__ = """
An aurora watch current for the Australian region. Aurora watches are used
to warn of likely auroral activity in the next 48 hours.

Attributes
----------
issue_time : datetime
    The time (UTC) at which the watch was issued.
start_date : datetime
    The first day (UTC) to which the watch applies.
end_date : str
    The last day (UTC) to which the watch applies.
cause : str
    The dominant cause of the likely auroral activity. One of: coronal
    hole, coronal mass ejection.
k_aus : int
    The expected level of the auroral activity, according to the
    Australian region K index (0-9).
lat_band : str
    The latitude band from which auroral activity is likely to be
    visible, based on the value of k_aus.
    One of: high, mid, low, equatorial.
comments : str
    Comments provided by the duty forecaster.
"""

AuroraAlert = namedtuple(
    "AuroraAlert",
    ["start_time", "valid_until", "k_aus", "lat_band", "description"],
)

AuroraAlert.__doc__ = """
A aurora alert current for the Australian region.
Aurora alerts are used to report geomagnetic activity currently in
progress and favourable for auroras.

Attributes
----------
start_time : datetime
    The time (UTC) at which the alert became active.
valid_until : datetime
    The time (UTC) until which the alert is valid.
k_aus : int
    The level of the alert, according to the Australian region K index
    (0-9).
lat_band : str
    The latitude band from which auroral activity is likely to be visible,
    based on the value of k_aus.
    One of: high, mid, low, equatorial.
description : str
    A description of the alert, based on the value of k_aus.
"""

MagAlert = namedtuple(
    "MagAlert", ["start_time", "valid_until", "g_scale", "description"]
)
"""
A magnetic alert current for the Australian region.

Attributes
----------
start_time: datetime
    The time (UTC) at which the alert became active.
valid_until: datetime
    The time (UTC) until which the alert is valid.
g_scale: int
    The level of the alert, according to the NOAA Geomagnetic Storm scale (G1-G5).
description:
    The level of the alert. One of: minor, major, severe.
"""

MagWarning = namedtuple(
    "MagWarning",
    ["issue_time", "start_date", "end_date", "cause", "activity", "comments"],
)
MagWarning.__doc__ = """
A geophysical warning currently active for the Australian region.

Attributes
----------
issue_time : datetime
    The time (UTC) at which the warning was issued.
start_date : datetime
    The first day (UTC) to which the warning applies.
end_date : datetime
    The last day (UTC) to which the warning applies.
cause: str
    The cause, if known, of the expected geomagnetic activity. 
    One of: coronal hole, coronal mass ejection, disappearing filament, flare.
activity: list of dictionaries
        Forecast geomagnetic activity levels for each day of the warning period.
comments : str
    Comments, if any, provided by the duty forecaster.
"""

AIndex = namedtuple("AIndex", ["valid_time", "index"])
AIndex.__doc__ = """
An A-index.

Attributes
----------
valid_time: datetime
        The start of the day (UTC) to which the A index pertains.
index: datetime
        The A index value: an integer from 0 to 400.
"""

KIndex = namedtuple("KIndex", ["valid_time", "analysis_time", "index"])
KIndex.__doc__ = """
A K-index.

Attributes
----------
valid_time: datetime
        The start of the 3-hour period (UTC) to which the K index pertains
analysis_time: datetime
        The time (UTC) when the K index calculation was made.
index: datetime
        The K index value: an integer from 0 to 9.
"""

DstIndex = namedtuple("DstIndex", ["valid_time", "index"])
DstIndex.__doc__ = """
A Dst-index.

Attributes
----------
valid_time: datetime
        The start of the 3-hour period (UTC) to which the K index pertains.
index: int
        The Dst index value: an unbounded signed integer (likely range is -2000
        to 300).
    
"""
