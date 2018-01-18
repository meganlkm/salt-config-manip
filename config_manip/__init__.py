"""
example sls:

merge_reactor_config:
  module.run:
    - name: config_manip.merge
    - origin: /etc/salt/master.d/reactor.conf
    - source: /srv/salt/mystate/files/reactor.conf
"""
import os
from collections import Mapping
from copy import deepcopy
from datetime import datetime

import yaml
from salt.utils import yamlloader


def __write_config(config_path, data):
    stream = file(config_path, 'w')
    yaml.dump(data, stream, default_flow_style=False)


def __get_data(source):
    data = __salt__['cp.get_file_str'](source)
    return yamlloader.SaltYamlSafeLoader(data).get_data()


def __update_list(src, base):
    for val in src:
        if val not in base:
            base.append(val)
    return base


def __compare_and_merge(src, dest):
    for key, value in src.iteritems():
        if value != dest.get(key):
            if isinstance(value, list):
                dest[key] = __update_list(value, dest[key])
            elif isinstance(value, Mapping):
                dest[key].update(value)
            else:
                dest[key] = value
    return dest


def merge(origin, source, backup_original=False):
    response = {}
    source_data = __get_data(source)

    if os.path.exists(origin):
        origin_data = __get_data(origin)
        new_config = deepcopy(origin_data)

        if new_config != source_data:
            new_config = __compare_and_merge(source_data, new_config)

            changed = origin_data != new_config
            if changed:
                if backup_original:
                    response['backup_path'] = '-'.join([origin, datetime.utcnow().strftime('%Y%m%dT%H%M%S')])
                    __write_config(response['backup_path'], origin_data)
                __write_config(origin, new_config)
            response['updated'] = changed
    else:
        __write_config(origin, source_data)
        response['created'] = os.path.exists(origin)

    return response
