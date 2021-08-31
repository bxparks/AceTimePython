# Copyright 2018 Brian T. Park
#
# MIT License
"""
Generate the internal versions of zone_infos.py and zone_policies.py directly
instead of creating files. These maps can be used for further processing.
"""

import logging
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
from typing_extensions import TypedDict

from acetimetools.data_types.at_types import ZonesMap
from acetimetools.data_types.at_types import PoliciesMap
from acetimetools.transformer.transformer import normalize_name

# These are the data structures written out to 'zone_policies.py' and
# 'zone_infos.py' by pygenerator.py.

ZoneRule = TypedDict(
    'ZoneRule', {
        'from_year': int,
        'to_year': int,
        'in_month': int,
        'on_day_of_week': int,
        'on_day_of_month': int,
        'at_seconds': int,
        'at_time_suffix': str,
        'delta_seconds': int,
        'letter': str,
    })

ZonePolicy = TypedDict(
    'ZonePolicy', {
        'name': str,
        'rules': List[ZoneRule],
    })

ZonePolicyMap = Dict[str, ZonePolicy]

ZoneEra = TypedDict(
    'ZoneEra', {
        'offset_seconds': int,
        'zone_policy': Union[ZonePolicy, str],  # '-', ':', or ZonePolicy
        'rules_delta_seconds': int,
        'format': str,
        'until_year': int,
        'until_month': int,
        'until_day': int,
        'until_seconds': int,
        'until_time_suffix': str,
    })

ZoneInfo = TypedDict(
    'ZoneInfo', {
        'name': str,
        'eras': List[ZoneEra],
    })

ZoneInfoMap = Dict[str, ZoneInfo]


class InlineZoneInfo:
    """Generate Python zone infos and policies maps inlined (instead of files).
    """

    def __init__(self, zones_map: ZonesMap, policies_map: PoliciesMap):
        """
        Args:
            zones_map (dict): {full_name -> ZoneEra[]}
            policies_map (dict): {policy_name -> ZoneRules[]}
        """
        self.zones_map = zones_map
        self.policies_map = policies_map

        self.zone_infos: ZoneInfoMap = {}
        self.zone_policies: ZonePolicyMap = {}

    def generate_zonedb(self) -> Tuple[ZoneInfoMap, ZonePolicyMap]:
        """Return the zone_infos and zone_policies maps which look identical
        to the zone_infos.py and zone_policies.py generated by PythonGenerator.
        """
        logging.info('Generating inlined zone_policies and zone_infos')
        self._generate_policies()
        self._generate_infos()
        return (self.zone_infos, self.zone_policies)

    def _generate_policies(self) -> None:
        for name, rules in self.policies_map.items():
            policy_rules: List[ZoneRule] = []
            for rule in rules:
                # yapf: disable
                policy_rules.append({
                    'from_year': rule['from_year'],
                    'to_year': rule['to_year'],
                    'in_month': rule['in_month'],
                    'on_day_of_week': rule['on_day_of_week'],
                    'on_day_of_month': rule['on_day_of_month'],
                    'at_seconds': rule['at_seconds_truncated'],
                    'at_time_suffix': rule['at_time_suffix'],
                    'delta_seconds': rule['delta_seconds_truncated'],
                    'letter': rule['letter']
                })
                # yapf: enable

            normalized_name = normalize_name(name)
            self.zone_policies[normalized_name] = {
                'name': name,  # policy name
                'rules': policy_rules
            }

    def _generate_infos(self) -> None:
        for zone_name, eras in self.zones_map.items():
            zone_eras: List[ZoneEra] = []
            for era in eras:
                policy_name = era['rules']
                zone_policy: Union[ZonePolicy, str]
                if policy_name in ['-', ':']:
                    zone_policy = policy_name
                else:
                    policy_name = normalize_name(policy_name)
                    zone_policy = self.zone_policies[policy_name]

                # yapf: disable
                zone_eras.append({
                    'offset_seconds': era['offset_seconds_truncated'],
                    'zone_policy': zone_policy,
                    'rules_delta_seconds': era['rules_delta_seconds_truncated'],
                    'format': era['format'],
                    'until_year': era['until_year'],
                    'until_month': era['until_month'],
                    'until_day': era['until_day'],
                    'until_seconds': era['until_seconds_truncated'],
                    'until_time_suffix': era['until_time_suffix'],
                })
                # yapf: enable
            self.zone_infos[zone_name] = {'name': zone_name, 'eras': zone_eras}
