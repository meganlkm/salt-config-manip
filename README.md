# salt-config-manip


## Usage

```yaml
merge_reactor_config:
  module.run:
    - name: config_manip.merge
    - origin: /etc/salt/master.d/reactor.conf
    - source: salt://mystate/files/reactor.conf
    - backup_original: True
```
