"""
Factory function for creating netdev classes
"""
from .cisco import CiscoASA
from .cisco import CiscoIOS
from .cisco import CiscoNXOS
from .fujitsu import FujitsuSwitch
from .hp import HPComware
from .mikrotik import MikrotikRouterOS

# @formatter:off
# The keys of this dictionary are the supported device_types
CLASS_MAPPER = {
    'cisco_ios': CiscoIOS,
    'cisco_xe': CiscoIOS,
    'cisco_asa': CiscoASA,
    'cisco_nxos': CiscoNXOS,
    'hp_comware': HPComware,
    'fujitsu_switch': FujitsuSwitch,
    'mikrotik_routeros': MikrotikRouterOS,
}

# @formatter:on

platforms = list(CLASS_MAPPER.keys())
platforms.sort()
platforms_str = u"\n".join(platforms)


def create(*args, **kwargs):
    """Factory function selects the proper class and creates object based on device_type"""
    if kwargs['device_type'] not in platforms:
        raise ValueError('Unsupported device_type: '
                         'currently supported platforms are: {0}'.format(platforms_str))
    connection_class = CLASS_MAPPER[kwargs['device_type']]
    return connection_class(*args, **kwargs)
