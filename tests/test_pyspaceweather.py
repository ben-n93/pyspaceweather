"""
Tests for pyspaceweather.py
"""

from datetime import datetime

import requests
import pytest

from pyspaceweather.pyspaceweather import (
    SpaceWeather,
    AuroraAlert,
    AuroraWatch,
    AuroraOutlook,
    MagAlert,
    MagWarning,
    AIndex,
    KIndex,
    DstIndex,
)


@pytest.fixture
def spaceweather_api(requests_mock):
    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-k-index", status_code=200
    )
    space_weather = SpaceWeather("valid_api_key")
    return space_weather


# Testing the API.
def test_invalid_api_key(requests_mock):
    """Test that an invalid API key (HTTP error 403) raises an exception."""
    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-k-index", status_code=403
    )
    with pytest.raises(ValueError):
        space_weather = SpaceWeather("0000")


def test_exception_raised_on_http_error(requests_mock):
    """Test that an exception is raised when there is a HTTP error that
    isn't 403."""
    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-k-index", status_code=500
    )
    with pytest.raises(requests.exceptions.HTTPError):
        space_weather = SpaceWeather("000")


# Testing get_aurora methods.


def test_get_aurora_returns_outlook(spaceweather_api, requests_mock):
    """Test get_aurora_outlook returns a list which contains an
    AuroraOutlook object."""

    data = {
        "data": [
            {
                "issue_time": "2015-01-12 23:18:00",
                "start_date": "2015-01-15",
                "end_date": "2015-01-17",
                "cause": "coronal mass ejection",
                "k_aus": 7,
                "lat_band": "mid",
                "comments": "A large active solar region is rotating...",
            }
        ]
    }
    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-aurora-outlook",
        json=data,
    )
    aurora = spaceweather_api.get_aurora_outlook()
    assert isinstance(aurora, list)

    expected_data = AuroraOutlook(
        datetime(2015, 1, 12, 23, 18),
        datetime(2015, 1, 15, 0, 0),
        datetime(2015, 1, 17, 0, 0),
        data["data"][0]["cause"],
        data["data"][0]["k_aus"],
        data["data"][0]["lat_band"],
        data["data"][0]["comments"],
    )
    assert aurora == [expected_data]


def test_get_aurora_watch_returns_watch(spaceweather_api, requests_mock):
    """Test get_aurora_watch returns a list which contains an
    AuroraWatch object.
    """
    data = {
        "data": [
            {
                "issue_time": "2015-01-06 23:18:00",
                "start_date": "2015-01-07",
                "end_date": "2015-01-08",
                "cause": "coronal hole",
                "k_aus": 6,
                "lat_band": "high",
                "comments": "Effects of a coronal hole are expected to...",
            }
        ]
    }

    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-aurora-watch",
        json=data,
    )
    aurora = spaceweather_api.get_aurora_watch()
    assert isinstance(aurora, list)

    expected_data = AuroraWatch(
        datetime(2015, 1, 6, 23, 18),
        datetime(2015, 1, 7, 0, 0),
        datetime(2015, 1, 8, 0, 0),
        data["data"][0]["cause"],
        data["data"][0]["k_aus"],
        data["data"][0]["lat_band"],
        data["data"][0]["comments"],
    )
    assert aurora == [expected_data]


def test_get_aurora_returns_alert(spaceweather_api, requests_mock):
    """Test get_aurora_alert() returns a list, which contains a AuroraAlert
    object."""

    data = {
        "data": [
            {
                "start_time": "2015-02-07 08:45:00",
                "valid_until": "2015-02-07 20:45:00",
                "k_aus": 6,
                "lat_band": "high",
                "description": "Geomagnetic storm in progress.",
            }
        ]
    }

    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-aurora-alert",
        json=data,
    )
    aurora = spaceweather_api.get_aurora_alert()
    assert isinstance(aurora, list)

    expected_data = AuroraAlert(
        datetime(2015, 2, 7, 8, 45),
        datetime(2015, 2, 7, 20, 45),
        data["data"][0]["k_aus"],
        data["data"][0]["lat_band"],
        data["data"][0]["description"],
    )
    assert aurora == [expected_data]


def test_get_aurora_returns_empty_dictionary(spaceweather_api, requests_mock):
    """Test _get_aurora returns an empty list if the web
    API returns an empty data array."""
    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-aurora-outlook", json={"data": []}
    )
    aurora = spaceweather_api.get_aurora_outlook()
    assert aurora == []


def test_get_aurora_exception(spaceweather_api, requests_mock):
    """Test _get_aurora raises an exception when a HTTP
    error is encountered.."""
    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-aurora-outlook",
        status_code=400,
        json={"message": "Unsupported option value: location=fantasy-land"},
    )
    with pytest.raises(requests.exceptions.HTTPError):
        spaceweather_api.get_aurora_outlook()


# Testing get_mag functions.
def test_get_mag_alert_returns_mag_alert(spaceweather_api, requests_mock):
    """
    Test that get_mag_alert() returns a list, which contains a MagAlert object.
    """
    data = {
        "data": [
            {
                "start_time": "2015-02-07 08:45:00",
                "valid_until": "2015-02-07 20:45:00",
                "g_scale": 1,
                "description": "minor",
            }
        ]
    }
    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-mag-alert", json=data
    )
    mag_alert = spaceweather_api.get_mag_alert()
    assert isinstance(mag_alert, list)

    expected_data = MagAlert(
        datetime(2015, 2, 7, 8, 45),
        datetime(2015, 2, 7, 20, 45),
        data["data"][0]["g_scale"],
        data["data"][0]["description"],
    )
    assert mag_alert == [expected_data]


def test_get_mag_warning_returns_mag_warning(spaceweather_api, requests_mock):
    """
    Test that get_mag_warning() returns a list, which contains a MagWarning object.
    """
    data = {
        "data": [
            {
                "issue_time": "2015-03-01 23:18:00",
                "start_date": "2015-03-02",
                "end_date": "2015-03-03",
                "cause": "coronal hole",
                "activity": [
                    {"date": "2015-03-02", "forecast": "Unsettled to minor storm"},
                    {"date": "2015-03-03", "forecast": "Unsettled to minor storm"},
                ],
                "comments": "The effect of the high speed solar wind stream from a...",
            }
        ]
    }

    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-mag-warning", json=data
    )
    mag_warning = spaceweather_api.get_mag_warning()
    assert isinstance(mag_warning, list)

    expected_data = MagWarning(
        datetime(2015, 3, 1, 23, 18),
        datetime(2015, 3, 2),
        datetime(2015, 3, 3),
        data["data"][0]["cause"],
        [
            {datetime(2015, 3, 2): "Unsettled to minor storm"},
            {datetime(2015, 3, 3): "Unsettled to minor storm"},
        ],
        data["data"][0]["comments"],
    )
    assert mag_warning == [expected_data]


# Testing _get_index.


def test_get_index_works_with_missing_date_parameter(spaceweather_api, requests_mock):
    """Test _get_index works if only the start or end parameters is passed a date."""
    data = {
        "data": [
            [
                {"index": 5, "valid_time": "2021-12-04 00:00:00"},
                {"index": 6, "valid_time": "2021-12-05 00:00:00"},
                {"index": 6, "valid_time": "2021-12-06 00:00:00"},
            ]
        ]
    }

    expected_data = [
        AIndex(datetime(2021, 12, 4), 5),
        AIndex(datetime(2021, 12, 5), 6),
        AIndex(datetime(2021, 12, 6), 6),
    ]

    requests_mock.post("https://sws-data.sws.bom.gov.au/api/v1/get-a-index", json=data)
    a_indexes = spaceweather_api.get_a_index(start="2021-12-04 00:00:00")
    assert isinstance(a_indexes, list)
    assert a_indexes == expected_data

    requests_mock.post("https://sws-data.sws.bom.gov.au/api/v1/get-a-index", json=data)
    a_indexes = spaceweather_api.get_a_index(end="2021-12-06 00:00:00")
    assert isinstance(a_indexes, list)
    assert a_indexes == expected_data


def test_get_index_wrong_date_format(spaceweather_api):
    """Test that a ValueError is raised when the start or end parameter
    is passed a string with the incorrect format.
    """

    # Start date in wrong date format.
    with pytest.raises(ValueError):
        spaceweather_api._get_index(
            "a-index",
            start="2024",
            end="2024-01-01 00:00:00",
            location="Australian region",
        )

    # End date in wrong date format.
    with pytest.raises(ValueError):
        spaceweather_api._get_index(
            "a-index",
            start="2024-01-01 00:00:00",
            end="2024",
            location="Australian region",
        )


def test_get_index_returns_empty_dictionary(spaceweather_api, requests_mock):
    """Test _get_index returns an empty list if the web API returns an empty
    data array."""
    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-k-index", json={"data": []}
    )
    indexes = spaceweather_api.get_k_index()
    assert indexes == []


def test_get_a_index_returns_AIndex(spaceweather_api, requests_mock):
    """Test that get_a_index() returns a list of AIndex objects."""

    data = {
        "data": [
            [
                {"index": 5, "valid_time": "2021-12-04 00:00:00"},
                {"index": 6, "valid_time": "2021-12-05 00:00:00"},
                {"index": 6, "valid_time": "2021-12-06 00:00:00"},
            ]
        ]
    }

    expected_data = [
        AIndex(datetime(2021, 12, 4), 5),
        AIndex(datetime(2021, 12, 5), 6),
        AIndex(datetime(2021, 12, 6), 6),
    ]

    requests_mock.post("https://sws-data.sws.bom.gov.au/api/v1/get-a-index", json=data)
    a_indexes = spaceweather_api.get_a_index()
    assert isinstance(a_indexes, list)
    assert a_indexes == expected_data


def test_get_dst_index_returns_DstIndex(spaceweather_api, requests_mock):
    """Test that get_dst_index() returns a list of DstIndex objects."""

    data = {
        "data": [
            [
                {"index": 6, "valid_time": "2021-11-21 00:05:00"},
                {"index": 3, "valid_time": "2021-11-21 00:15:00"},
                {"index": 4, "valid_time": "2021-11-21 00:25:00"},
            ]
        ]
    }

    expected_data = [
        DstIndex(datetime(2021, 11, 21, 0, 5), 6),
        DstIndex(datetime(2021, 11, 21, 0, 15), 3),
        DstIndex(datetime(2021, 11, 21, 0, 25), 4),
    ]

    requests_mock.post(
        "https://sws-data.sws.bom.gov.au/api/v1/get-dst-index", json=data
    )
    dst_indexes = spaceweather_api.get_dst_index()
    assert isinstance(dst_indexes, list)
    assert dst_indexes == expected_data


def test_get_kst_index_returns_KIndex(spaceweather_api, requests_mock):
    """Test that get_kst_index() returns a list of DstIndex objects."""

    data = {
        "data": [
            {
                "index": 2,
                "valid_time": "2021-11-21 00:00:00",
                "analysis_time": "2021-11-22 00:07:36",
            },
            {
                "index": 2,
                "valid_time": "2021-11-21 03:00:00",
                "analysis_time": "2021-11-22 00:07:36",
            },
        ]
    }

    expected_data = [
        KIndex(datetime(2021, 11, 21), datetime(2021, 11, 22, 0, 7, 36), 2),
        KIndex(datetime(2021, 11, 21, 3), datetime(2021, 11, 22, 0, 7, 36), 2),
    ]

    requests_mock.post("https://sws-data.sws.bom.gov.au/api/v1/get-k-index", json=data)
    k_indexes = spaceweather_api.get_k_index()
    assert isinstance(k_indexes, list)
    assert k_indexes == expected_data
