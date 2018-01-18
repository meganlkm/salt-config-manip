import os
from collections import Mapping
from copy import deepcopy
from datetime import datetime

import yaml
from salt.exceptions import CommandExecutionError
from salt.utils import yamlloader


def __write_config(config_path, data):
    try:
        stream = file(config_path, 'w')
        yaml.dump(data, stream, default_flow_style=False)
    except Exception as e:
        raise CommandExecutionError('Error: %s' % str(e))


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
    response = {'status': 'up to date', 'changed': False}
    source_data = __get_data(source)

    if os.path.exists(origin):
        origin_data = __get_data(origin)
        new_config = deepcopy(origin_data)

        if new_config != source_data:
            new_config = __compare_and_merge(source_data, new_config)

            if origin_data != new_config:
                if backup_original:
                    response['backup_path'] = '-'.join([origin, datetime.utcnow().strftime('%Y%m%dT%H%M%S')])
                    __write_config(response['backup_path'], origin_data)
                __write_config(origin, new_config)
                response['status'] = 'updated'
                response['changed'] = True
    else:
        __write_config(origin, source_data)
        if not os.path.exists(origin):
            raise CommandExecutionError('Error: config file not created')
        response['status'] = 'created'
        response['changed'] = True

    return response
