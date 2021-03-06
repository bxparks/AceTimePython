import sys
import unittest
import logging
from datetime import datetime, timedelta, timezone

from acetime.common import SECONDS_SINCE_UNIX_EPOCH
from acetime.acetz import acetz, ZoneManager
from acetime.zonedb.zone_registry import ZONE_REGISTRY
from acetime.zonedb.zone_infos import ZONE_INFO_America_Los_Angeles
from acetime.zonedb.zone_infos import ZONE_INFO_US_Pacific


# Enable logging during unittests.
# https://stackoverflow.com/questions/7472863
logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


def print_zp_at_dt(tz: acetz, dt: datetime) -> None:
    zp = tz.zone_processor()
    zp.init_for_year(dt.year)
    zp.print_matches_and_transitions()
    unix_seconds = int(dt.timestamp())
    epoch_seconds = unix_seconds - SECONDS_SINCE_UNIX_EPOCH
    info = zp.get_timezone_info_for_seconds(epoch_seconds)
    if info:
        print(
            f"print_zp_at_dt(): epoch_seconds={epoch_seconds} "
            f"total_offset={info.total_offset} "
            f"utc_offset={info.utc_offset} "
            f"dst_offset={info.dst_offset} "
            f"abbrev={info.abbrev} "
            f"fold={info.fold}"
        )
    else:
        print(
            f"print_zp_at_dt(): epoch_seconds={epoch_seconds} "
            " transition not found"
        )


zone_manager = ZoneManager(ZONE_REGISTRY)


class TestLosAngeles(unittest.TestCase):

    def test_constructor(self) -> None:
        """Create date from AceTime epoch seconds using the constructor
        that specifies the timezone directly.
        """

        tz = zone_manager.gettz('America/Los_Angeles')

        dtc = datetime(2000, 1, 2, 3, 4, 5, tzinfo=tz)
        self.assertEqual(2000, dtc.year)
        self.assertEqual(1, dtc.month)
        self.assertEqual(2, dtc.day)
        self.assertEqual(3, dtc.hour)
        self.assertEqual(4, dtc.minute)
        self.assertEqual(5, dtc.second)

        # date +%s -d '2000-01-02T03:04:05-08:00'
        self.assertEqual(946811045, int(dtc.timestamp()))

        dtc_utcoffset = dtc.utcoffset()
        assert(dtc_utcoffset is not None)
        self.assertEqual(-8 * 3600, dtc_utcoffset.total_seconds())

        assert(dtc.tzinfo is not None)
        self.assertEqual("PST", tz.tzname(dtc))
        self.assertEqual("America/Los_Angeles", tz.tzfullname())
        self.assertEqual("America/Los_Angeles", tz.tzfullname(follow_link=True))

    def test_fromtimestamp(self) -> None:
        """Create date from AceTime epoch seconds using fromtimestamp()."""

        tz = zone_manager.gettz('America/Los_Angeles')

        unix_seconds = 946811045
        dte = datetime.fromtimestamp(unix_seconds, tz=tz)

        expected = datetime(2000, 1, 2, 3, 4, 5, tzinfo=tz)
        self.assertEqual(dte, expected)

        dte_utcoffset = dte.utcoffset()
        assert(dte_utcoffset is not None)
        self.assertEqual(-8 * 3600, dte_utcoffset.total_seconds())

        assert(dte.tzinfo is not None)
        self.assertEqual("PST", tz.tzname(dte))
        self.assertEqual("America/Los_Angeles", tz.tzfullname())
        self.assertEqual("America/Los_Angeles", tz.tzfullname(follow_link=True))

    def test_before_spring_forward(self) -> None:
        tz = zone_manager.gettz('America/Los_Angeles')

        # One second before DST shift, 01:59:59 UTC-8
        epoch_seconds = 7984799
        unix_seconds = epoch_seconds + SECONDS_SINCE_UNIX_EPOCH
        dtu = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)

        # print_zp_at_dt(tz, dtu)

        # Date from epoch seconds.
        dtt = dtu.astimezone(tz)
        self.assertEqual(
            epoch_seconds,
            int(dtt.timestamp()) - SECONDS_SINCE_UNIX_EPOCH
        )
        self.assertEqual(2000, dtt.year)
        self.assertEqual(4, dtt.month)
        self.assertEqual(2, dtt.day)
        self.assertEqual(1, dtt.hour)
        self.assertEqual(59, dtt.minute)
        self.assertEqual(59, dtt.second)
        self.assertEqual("PST", dtt.tzname())
        self.assertEqual(timedelta(hours=-8), dtt.utcoffset())
        self.assertEqual(timedelta(hours=0), dtt.dst())

        # Date from component
        dtc = datetime(2000, 4, 2, 1, 59, 59, tzinfo=tz)
        self.assertEqual(unix_seconds, int(dtc.timestamp()))
        self.assertEqual(2000, dtc.year)
        self.assertEqual(4, dtc.month)
        self.assertEqual(2, dtc.day)
        self.assertEqual(1, dtc.hour)
        self.assertEqual(59, dtc.minute)
        self.assertEqual(59, dtc.second)
        self.assertEqual("PST", dtc.tzname())
        self.assertEqual(timedelta(hours=-8), dtc.utcoffset())
        self.assertEqual(timedelta(hours=0), dtc.dst())

        self.assertEqual(dtc, dtt)

    def test_after_spring_forward(self) -> None:
        tz = zone_manager.gettz('America/Los_Angeles')

        # Right after DST forward shift, 03:00:00 UTC-7
        epoch_seconds = 7984800
        unix_seconds = epoch_seconds + SECONDS_SINCE_UNIX_EPOCH
        dtu = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)

        # Date from epoch seconds
        dtt = dtu.astimezone(tz)
        self.assertEqual(unix_seconds, int(dtt.timestamp()))
        self.assertEqual(2000, dtt.year)
        self.assertEqual(4, dtt.month)
        self.assertEqual(2, dtt.day)
        self.assertEqual(3, dtt.hour)
        self.assertEqual(0, dtt.minute)
        self.assertEqual(0, dtt.second)
        self.assertEqual("PDT", dtt.tzname())
        self.assertEqual(timedelta(hours=-7), dtt.utcoffset())
        self.assertEqual(timedelta(hours=1), dtt.dst())

        # Date from component
        dtc = datetime(2000, 4, 2, 3, 0, 0, tzinfo=tz)
        self.assertEqual(unix_seconds, int(dtc.timestamp()))
        self.assertEqual(2000, dtc.year)
        self.assertEqual(4, dtc.month)
        self.assertEqual(2, dtc.day)
        self.assertEqual(3, dtc.hour)
        self.assertEqual(0, dtc.minute)
        self.assertEqual(0, dtc.second)
        self.assertEqual("PDT", dtc.tzname())
        self.assertEqual(timedelta(hours=-7), dtc.utcoffset())
        self.assertEqual(timedelta(hours=1), dtc.dst())

        self.assertEqual(dtc, dtt)

    def test_before_fall_back(self) -> None:
        tz = zone_manager.gettz('America/Los_Angeles')

        # One second before DST shift, 01:59:59 UTC-7
        epoch_seconds = 26125199
        unix_seconds = epoch_seconds + SECONDS_SINCE_UNIX_EPOCH
        dtu = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)

        # Date from epoch seconds. By default, should match the 1st transition.
        dtt = dtu.astimezone(tz)
        self.assertEqual(
            epoch_seconds,
            int(dtt.timestamp()) - SECONDS_SINCE_UNIX_EPOCH
        )
        self.assertEqual(2000, dtt.year)
        self.assertEqual(10, dtt.month)
        self.assertEqual(29, dtt.day)
        self.assertEqual(1, dtt.hour)
        self.assertEqual(59, dtt.minute)
        self.assertEqual(59, dtt.second)
        self.assertEqual("PDT", dtt.tzname())
        self.assertEqual(timedelta(hours=-7), dtt.utcoffset())
        self.assertEqual(timedelta(hours=1), dtt.dst())

        # Date from component. With fold=0, should match the 1st transition.
        dtc = datetime(2000, 10, 29, 1, 59, 59, tzinfo=tz)
        self.assertEqual(unix_seconds, int(dtc.timestamp()))
        self.assertEqual(2000, dtc.year)
        self.assertEqual(10, dtc.month)
        self.assertEqual(29, dtc.day)
        self.assertEqual(1, dtc.hour)
        self.assertEqual(59, dtc.minute)
        self.assertEqual(59, dtc.second)
        self.assertEqual("PDT", dtc.tzname())
        self.assertEqual(timedelta(hours=-7), dtc.utcoffset())
        self.assertEqual(timedelta(hours=1), dtc.dst())

        # Test the second transition with fold=1
        dtc = datetime(2000, 10, 29, 1, 59, 59, tzinfo=tz, fold=1)
        self.assertEqual(unix_seconds + 3600, int(dtc.timestamp()))
        self.assertEqual(2000, dtc.year)
        self.assertEqual(10, dtc.month)
        self.assertEqual(29, dtc.day)
        self.assertEqual(1, dtc.hour)
        self.assertEqual(59, dtc.minute)
        self.assertEqual(59, dtc.second)
        self.assertEqual("PST", dtc.tzname())
        self.assertEqual(timedelta(hours=-8), dtc.utcoffset())
        self.assertEqual(timedelta(hours=0), dtc.dst())

    def test_after_fall_back(self) -> None:
        tz = zone_manager.gettz('America/Los_Angeles')

        # Just after DST fall back 01:00:00 UTC-8
        epoch_seconds = 26125200
        unix_seconds = epoch_seconds + SECONDS_SINCE_UNIX_EPOCH
        dtu = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)

        # Date from epoch seconds.
        dtt = dtu.astimezone(tz)
        self.assertEqual(
            epoch_seconds,
            int(dtt.timestamp()) - SECONDS_SINCE_UNIX_EPOCH
        )
        self.assertEqual(2000, dtt.year)
        self.assertEqual(10, dtt.month)
        self.assertEqual(29, dtt.day)
        self.assertEqual(1, dtt.hour)
        self.assertEqual(0, dtt.minute)
        self.assertEqual(0, dtt.second)
        self.assertEqual("PST", dtt.tzname())
        self.assertEqual(timedelta(hours=-8), dtt.utcoffset())
        self.assertEqual(timedelta(hours=0), dtt.dst())

        # Date from component
        dtc = datetime(2000, 10, 29, 1, 0, 0, tzinfo=tz, fold=1)
        self.assertEqual(unix_seconds, int(dtc.timestamp()))
        self.assertEqual(2000, dtc.year)
        self.assertEqual(10, dtc.month)
        self.assertEqual(29, dtc.day)
        self.assertEqual(1, dtc.hour)
        self.assertEqual(0, dtc.minute)
        self.assertEqual(0, dtc.second)
        self.assertEqual("PST", dtc.tzname())
        self.assertEqual(timedelta(hours=-8), dtc.utcoffset())
        self.assertEqual(timedelta(hours=0), dtc.dst())

        self.assertEqual(dtc, dtt)

    def test_way_after_fall_back(self) -> None:
        tz = zone_manager.gettz('America/Los_Angeles')

        # Just after DST fall back 02:00:00 UTC-8
        epoch_seconds = 26125200 + 3600
        unix_seconds = epoch_seconds + SECONDS_SINCE_UNIX_EPOCH
        dtu = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)

        # Date from epoch seconds.
        dtt = dtu.astimezone(tz)
        self.assertEqual(unix_seconds, int(dtt.timestamp()))
        self.assertEqual(2000, dtt.year)
        self.assertEqual(10, dtt.month)
        self.assertEqual(29, dtt.day)
        self.assertEqual(2, dtt.hour)
        self.assertEqual(0, dtt.minute)
        self.assertEqual(0, dtt.second)
        self.assertEqual("PST", dtt.tzname())
        self.assertEqual(timedelta(hours=-8), dtt.utcoffset())
        self.assertEqual(timedelta(hours=0), dtt.dst())

        # Date from component
        dtc = datetime(2000, 10, 29, 2, 0, 0, tzinfo=tz)
        self.assertEqual(unix_seconds, int(dtc.timestamp()))
        self.assertEqual(2000, dtc.year)
        self.assertEqual(10, dtc.month)
        self.assertEqual(29, dtc.day)
        self.assertEqual(2, dtc.hour)
        self.assertEqual(0, dtc.minute)
        self.assertEqual(0, dtc.second)
        self.assertEqual("PST", dtc.tzname())
        self.assertEqual(timedelta(hours=-8), dtc.utcoffset())
        self.assertEqual(timedelta(hours=0), dtc.dst())

        self.assertEqual(dtc, dtt)

    def test_zone_info(self) -> None:
        """Test creation of acetz object using a ZoneInfo database entry,
        instead of going through the ZoneManager.
        """
        tz = acetz(ZONE_INFO_America_Los_Angeles)
        self.assertFalse(tz.islink())

        epoch_seconds = 7984800
        unix_seconds = epoch_seconds + SECONDS_SINCE_UNIX_EPOCH
        dtu = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)

        dtc = datetime(2000, 4, 2, 3, 0, 0, tzinfo=tz)
        self.assertEqual(unix_seconds, int(dtc.timestamp()))
        self.assertEqual(2000, dtc.year)
        self.assertEqual(4, dtc.month)
        self.assertEqual(2, dtc.day)
        self.assertEqual(3, dtc.hour)
        self.assertEqual(0, dtc.minute)
        self.assertEqual(0, dtc.second)
        self.assertEqual("PDT", dtc.tzname())
        self.assertEqual(timedelta(hours=-7), dtc.utcoffset())
        self.assertEqual(timedelta(hours=1), dtc.dst())

        self.assertEqual(dtu, dtc)


class TestUSPacific(unittest.TestCase):

    def test_zone_info(self) -> None:
        """Test creation of acetz object using the US/Pacific ZoneInfo database
        entry, instead of going through the ZoneManager. This should follow the
        'link_to' entry in ZoneInfo and use the America/Los_Angeles ZoneEras.
        """
        tz = acetz(ZONE_INFO_US_Pacific)
        self.assertTrue(tz.islink())

        epoch_seconds = 7984800
        unix_seconds = epoch_seconds + SECONDS_SINCE_UNIX_EPOCH
        dtu = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)

        dtc = datetime(2000, 4, 2, 3, 0, 0, tzinfo=tz)
        self.assertEqual(unix_seconds, int(dtc.timestamp()))
        self.assertEqual(2000, dtc.year)
        self.assertEqual(4, dtc.month)
        self.assertEqual(2, dtc.day)
        self.assertEqual(3, dtc.hour)
        self.assertEqual(0, dtc.minute)
        self.assertEqual(0, dtc.second)
        self.assertEqual("PDT", dtc.tzname())
        self.assertEqual(timedelta(hours=-7), dtc.utcoffset())
        self.assertEqual(timedelta(hours=1), dtc.dst())

        self.assertEqual(dtu, dtc)

        assert(dtc.tzinfo is not None)
        self.assertEqual("PDT", tz.tzname(dtc))
        self.assertEqual("US/Pacific", tz.tzfullname())
        self.assertEqual("America/Los_Angeles", tz.tzfullname(follow_link=True))


class TestTunis(unittest.TestCase):

    def test_2006_01_01(self) -> None:
        tz = zone_manager.gettz('Africa/Tunis')

        epoch_seconds = 189385200
        unix_seconds = epoch_seconds + SECONDS_SINCE_UNIX_EPOCH
        dtu = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)

        # print_zp_at_dt(tz, dtu)

        # Date from epoch seconds.
        dtt = dtu.astimezone(tz)
        self.assertEqual(
            epoch_seconds,
            int(dtt.timestamp()) - SECONDS_SINCE_UNIX_EPOCH
        )
        self.assertEqual(2006, dtt.year)
        self.assertEqual(1, dtt.month)
        self.assertEqual(1, dtt.day)
        self.assertEqual(0, dtt.hour)
        self.assertEqual(0, dtt.minute)
        self.assertEqual(0, dtt.second)
        self.assertEqual("CET", dtt.tzname())
        self.assertEqual(timedelta(hours=1), dtt.utcoffset())
        self.assertEqual(timedelta(hours=0), dtt.dst())

        # Date from component
        dtc = datetime(2006, 1, 1, 0, 0, 0, tzinfo=tz)
        self.assertEqual(unix_seconds, int(dtc.timestamp()))
        self.assertEqual(2006, dtc.year)
        self.assertEqual(1, dtc.month)
        self.assertEqual(1, dtc.day)
        self.assertEqual(0, dtc.hour)
        self.assertEqual(0, dtc.minute)
        self.assertEqual(0, dtc.second)
        self.assertEqual("CET", dtc.tzname())
        self.assertEqual(timedelta(hours=1), dtc.utcoffset())
        self.assertEqual(timedelta(hours=0), dtc.dst())

        self.assertEqual(dtc, dtt)


class TestSydney(unittest.TestCase):

    def test_2000_03_26_after_fall_back(self) -> None:
        tz = zone_manager.gettz('Australia/Sydney')

        epoch_seconds = 7315200
        unix_seconds = epoch_seconds + SECONDS_SINCE_UNIX_EPOCH
        dtu = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)

        # print_zp_at_dt(tz, dtu)

        # Date from epoch seconds.
        dtt = dtu.astimezone(tz)
        self.assertEqual(
            epoch_seconds,
            int(dtt.timestamp()) - SECONDS_SINCE_UNIX_EPOCH
        )
        self.assertEqual(2000, dtt.year)
        self.assertEqual(3, dtt.month)
        self.assertEqual(26, dtt.day)
        self.assertEqual(2, dtt.hour)
        self.assertEqual(0, dtt.minute)
        self.assertEqual(0, dtt.second)
        self.assertEqual("AEST", dtt.tzname())
        self.assertEqual(timedelta(hours=10), dtt.utcoffset())
        self.assertEqual(timedelta(hours=0), dtt.dst())

        # Date from component
        dtc = datetime(2000, 3, 26, 2, 0, 0, tzinfo=tz, fold=1)
        self.assertEqual(unix_seconds, int(dtc.timestamp()))
        self.assertEqual(2000, dtc.year)
        self.assertEqual(3, dtc.month)
        self.assertEqual(26, dtc.day)
        self.assertEqual(2, dtc.hour)
        self.assertEqual(0, dtc.minute)
        self.assertEqual(0, dtc.second)
        self.assertEqual("AEST", dtc.tzname())
        self.assertEqual(timedelta(hours=10), dtc.utcoffset())
        self.assertEqual(timedelta(hours=0), dtc.dst())

        self.assertEqual(dtc, dtt)
