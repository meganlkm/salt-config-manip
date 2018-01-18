"""
example sls:

merge_reactor_config:
  module.run:
    - name: config_manip.merge
    - origin: /etc/salt/master.d/reactor.conf
    - source: /srv/salt/mystate/files/reactor.conf
"""
import filecmp
import os
import yaml
from collections import Mapping
from shutil import copyfile


def __update_list(src, base, changed=False):
    for val in src:
        if val not in base:
            base.append(val)
            changed = True
    return base, changed


def merge(origin, source):
    response = {}
    if os.path.exists(origin):
        if not filecmp.cmp(origin, source):
            origin_data = yaml.load(open(origin))
            source_data = yaml.load(open(source))

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
                stream = file(origin, 'w')
                yaml.dump(origin_data, stream, default_flow_style=False)
            response['updated'] = changed
    else:
        copyfile(source, origin)
        response['created'] = os.path.exists(origin)

    return response
