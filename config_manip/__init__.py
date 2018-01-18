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
from datetime import datetime

import yaml
from salt.utils import yamlloader


def __write_config(config_path, data):
    stream = file(config_path, 'w')
    yaml.dump(data, stream, default_flow_style=False)


def __get_data(source):
    data = __salt__['cp.get_file_str'](source)
    return yamlloader.SaltYamlSafeLoader(data).get_data()


def __update_list(src, base, changed=False):
    for val in src:
        if val not in base:
            base.append(val)
            changed = True
    return base, changed


def merge(origin, source, backup_original=False):
    response = {}
    source_data = __get_data(source)

    if os.path.exists(origin):
        origin_data = __get_data(origin)

        if backup_original:
            response['backup_path'] = '-'.join([origin, datetime.utcnow().strftime('%Y%m%dT%H%M%S')])
            __write_config(response['backup_path'], origin_data)

        if origin_data != source_data:
            changed = False
            for key, value in source_data.iteritems():
                if value != origin_data.get(key):
                    if isinstance(value, list):
                        origin_data[key], changed = __update_list(value, origin_data[key], changed)
                    elif isinstance(value, Mapping):
                        origin_data[key].update(value)
                        changed = True
                    else:
                        origin_data[key] = value
                        changed = True

            if changed:
                __write_config(origin, origin_data)
            response['updated'] = changed
    else:
        __write_config(origin, source_data)
        response['created'] = os.path.exists(origin)

    return response
