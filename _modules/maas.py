# -*- coding: utf-8 -*-
'''
Module for handling maas calls.

:optdepends:    pyapi-maas Python adapter
:configuration: This module is not usable until the following are specified
                either in a pillar or in the minion's config file::

        maas.url: 'https://maas.domain.com/'
        maas.token: fdsfdsdsdsfa:fsdfae3fassd:fdsfdsfsafasdfsa

'''

from __future__ import absolute_import

import io
import logging
import collections
import os.path
import subprocess
import urllib2
import hashlib

import json

LOG = logging.getLogger(__name__)

# Import third party libs
HAS_MASS = False
try:
    from maas_client import MAASClient, MAASDispatcher, MAASOAuth
    HAS_MASS = True
except ImportError:
    LOG.debug('Missing python-oauth module. Skipping')


def __virtual__():
    '''
    Only load this module if maas-client
    is installed on this minion.
    '''
    if HAS_MASS:
        return 'maas'
    return False


APIKEY_FILE = '/var/lib/maas/.maas_credentials'


def _format_data(data):
    class Lazy:
        def __str__(self):
            return ' '.join(['{0}={1}'.format(k, v)
                            for k, v in data.iteritems()])
    return Lazy()


def _create_maas_client():
    global APIKEY_FILE
    try:
        api_token = file(APIKEY_FILE).read().splitlines()[-1].strip()\
            .split(':')
    except:
        LOG.exception('token')
    auth = MAASOAuth(*api_token)
    api_url = 'http://localhost:5240/MAAS'
    dispatcher = MAASDispatcher()
    return MAASClient(auth, dispatcher, api_url)


class MaasObject(object):
    def __init__(self):
        self._maas = _create_maas_client()
        self._extra_data_urls = {}
        self._extra_data = {}
        self._update = False
        self._element_key = 'name'
        self._update_key = 'id'

    def send(self, data):
        LOG.info('%s %s', self.__class__.__name__.lower(), _format_data(data))
        if self._update:
            return self._maas.put(
                self._update_url.format(data[self._update_key]), **data).read()
        if isinstance(self._create_url, tuple):
            return self._maas.post(self._create_url[0].format(**data),
                                   *self._create_url[1:], **data).read()
        return self._maas.post(self._create_url.format(**data),
                                None, **data).read()

    def process(self, objects_name=None):
        ret = {
            'success': [],
            'errors': {},
            'updated': [],
        }
        try:
            config = __salt__['config.get']('maas')
            for part in self._config_path.split('.'):
                config = config.get(part, {})
            extra = {}
            for name, url_call in self._extra_data_urls.iteritems():
                key = 'id'
                key_name = 'name'
                if isinstance(url_call, tuple):
                    if len(url_call) == 2:
                        url_call, key = url_call[:]
                    else:
                        url_call, key, key_name = url_call[:]
                json_res = json.loads(self._maas.get(url_call).read())
                if key:
                    extra[name] = {v[key_name]: v[key] for v in json_res}
                else:
                    extra[name] = {v[key_name]: v for v in json_res}
            if self._all_elements_url:
                all_elements = {}
                elements = self._maas.get(self._all_elements_url).read()
                res_json = json.loads(elements)
                for element in res_json:
                    if isinstance(element, (str, unicode)):
                        all_elements[element] = {}
                    else:
                        all_elements[element[self._element_key]] = element
            else:
                all_elements = {}

            def process_single(name, config_data):
                self._update = False
                try:
                    data = self.fill_data(name, config_data, **extra)
                    if data is None:
                        ret['updated'].append(name)
                        return
                    if name in all_elements:
                        self._update = True
                        data = self.update(data, all_elements[name])
                        self.send(data)
                        ret['updated'].append(name)
                    else:
                        self.send(data)
                        ret['success'].append(name)
                except urllib2.HTTPError as e:
                    etxt = e.read()
                    LOG.error('Failed for object %s reason %s', name, etxt)
                    ret['errors'][name] = str(etxt)
                except Exception as e:
                    LOG.error('Failed for object %s reason %s', name, e)
                    ret['errors'][name] = str(e)
            if objects_name is not None:
                if ',' in objects_name:
                    objects_name = objects_name.split(',')
                else:
                    objects_name = [objects_name]
                for object_name in objects_name:
                    process_single(object_name, config[object_name])
            else:
                for name, config_data in config.iteritems():
                    process_single(name, config_data)
        except Exception as e:
            LOG.exception('Error Global')
            raise
        if ret['errors']:
            raise Exception(ret)
        return ret


class Fabric(MaasObject):
    def __init__(self):
        super(Fabric, self).__init__()
        self._all_elements_url = u'api/2.0/fabrics/'
        self._create_url = u'api/2.0/fabrics/'
        self._update_url = u'api/2.0/fabrics/{0}/'
        self._config_path = 'region.fabrics'

    def fill_data(self, name, fabric):
        data = {
            'name': name,
            'description': fabric.get('description', ''),
        }
        if 'class_type' in fabric:
            data['class_type'] = fabric.get('class_type'),
        return data

    def update(self, new, old):
        new['id'] = str(old['id'])
        return new


class Subnet(MaasObject):
    def __init__(self):
        super(Subnet, self).__init__()
        self._all_elements_url = u'api/2.0/subnets/'
        self._create_url = u'api/2.0/subnets/'
        self._update_url = u'api/2.0/subnets/{0}/'
        self._config_path = 'region.subnets'
        self._extra_data_urls = {'fabrics': u'api/2.0/fabrics/'}

    def fill_data(self, name, subnet, fabrics):
        data = {
            'name': name,
            'fabric': str(fabrics[subnet.get('fabric', '')]),
            'cidr': subnet.get('cidr'),
            'gateway_ip': subnet['gateway_ip'],
        }
        self._iprange = subnet['iprange']
        return data

    def update(self, new, old):
        new['id'] = str(old['id'])
        return new

    def send(self, data):
        response = super(Subnet, self).send(data)
        res_json = json.loads(response)
        self._process_iprange(res_json['id'])
        return response

    def _process_iprange(self, subnet_id):
        ipranges = json.loads(self._maas.get(u'api/2.0/ipranges/').read())
        LOG.warn('all %s ipranges %s', subnet_id, ipranges)
        update = False
        old_data = None
        for iprange in ipranges:
            if iprange['subnet']['id'] == subnet_id:
                update = True
                old_data = iprange
                break
        data = {
            'start_ip': self._iprange.get('start'),
            'end_ip': self._iprange.get('end'),
            'subnet': str(subnet_id),
            'type': self._iprange.get('type', 'dynamic')
        }
        LOG.warn('INFO: %s\n OLD: %s', data, old_data)
        LOG.info('iprange %s', _format_data(data))
        if update:
            LOG.warn('UPDATING %s %s', data, old_data)
            self._maas.put(u'api/2.0/ipranges/{0}/'.format(old_data['id']),
                           **data)
        else:
            self._maas.post(u'api/2.0/ipranges/', None, **data)


class DHCPSnippet(MaasObject):
    def __init__(self):
        super(DHCPSnippet, self).__init__()
        self._all_elements_url = u'api/2.0/dhcp-snippets/'
        self._create_url = u'api/2.0/dhcp-snippets/'
        self._update_url = u'api/2.0/dhcp-snippets/{0}/'
        self._config_path = 'region.dhcp_snippets'
        self._extra_data_urls = {'subnets': u'api/2.0/subnets/'}

    def fill_data(self, name, snippet, subnets):
        data = {
            'name': name,
            'value': snippet['value'],
            'description': snippet['description'],
            'enabled': str(snippet['enabled'] and 1 or 0),
            'subnet': str(subnets[snippet['subnet']]),
        }
        return data

    def update(self, new, old):
        new['id'] = str(old['id'])
        return new


class PacketRepository(MaasObject):
    def __init__(self):
        super(PacketRepository, self).__init__()
        self._all_elements_url = u'api/2.0/package-repositories/'
        self._create_url = u'api/2.0/package-repositories/'
        self._update_url = u'api/2.0/package-repositories/{0}/'
        self._config_path = 'region.package_repositories'

    def fill_data(self, name, package_repository):
        data = {
            'name': name,
            'url': package_repository['url'],
            'distributions': package_repository['distributions'],
            'components': package_repository['components'],
            'arches': package_repository['arches'],
            'key': package_repository['key'],
            'enabled': str(package_repository['enabled'] and 1 or 0),
        }
        if 'disabled_pockets' in package_repository:
            data['disabled_pockets'] = package_repository['disable_pockets'],
        return data

    def update(self, new, old):
        new['id'] = str(old['id'])
        return new


class Device(MaasObject):
    def __init__(self):
        super(Device, self).__init__()
        self._all_elements_url = u'api/2.0/devices/'
        self._create_url = u'api/2.0/devices/'
        self._update_url = u'api/2.0/devices/{0}/'
        self._config_path = 'region.devices'
        self._element_key = 'hostname'
        self._update_key = 'system_id'

    def fill_data(self, name, device_data):
        data = {
            'mac_addresses': device_data['mac'],
            'hostname': name,
        }
        self._interface = device_data['interface']
        return data

    def update(self, new, old):
        old_macs = set(v['mac_address'].lower() for v in old['interface_set'])
        if new['mac_addresses'].lower() not in old_macs:
            self._update = False
            LOG.info('Mac changed deleting old device %s', old['system_id'])
            self._maas.delete(u'api/2.0/devices/{0}/'.format(old['system_id']))
        else:
            new[self._update_key] = str(old[self._update_key])
        return new

    def send(self, data):
        response = super(Device, self).send(data)
        resp_json = json.loads(response)
        system_id = resp_json['system_id']
        iface_id = resp_json['interface_set'][0]['id']
        self._link_interface(system_id, iface_id)
        return response

    def _link_interface(self, system_id, interface_id):
        data = {
            'mode': self._interface.get('mode', 'STATIC'),
            'subnet': self._interface['subnet'],
            'ip_address': self._interface['ip_address'],
        }
        if 'default_gateway' in self._interface:
            data['default_gateway'] = self._interface.get('default_gateway')
        if self._update:
            data['force'] = '1'
        LOG.info('interfaces link_subnet %s %s %s', system_id, interface_id,
                 _format_data(data))
        self._maas.post(u'/api/2.0/nodes/{0}/interfaces/{1}/'
                        .format(system_id, interface_id), 'link_subnet',
                        **data)


class Machine(MaasObject):
    def __init__(self):
        super(Machine, self).__init__()
        self._all_elements_url = u'api/2.0/machines/'
        self._create_url = u'api/2.0/machines/'
        self._update_url = u'api/2.0/machines/{0}/'
        self._config_path = 'region.machines'
        self._element_key = 'hostname'
        self._update_key = 'system_id'

    def fill_data(self, name, machine_data):
        power_data = machine_data['power_parameters']
        data = {
            'hostname': name,
            'architecture': machine_data.get('architecture', 'amd64/generic'),
            'mac_addresses': machine_data['interface']['mac'],
            'power_type': machine_data.get('power_type', 'ipmi'),
            'power_parameters_power_address': power_data['power_address'],
        }
        if 'power_driver' in power_data:
            data['power_parameters_power_driver'] = power_data['power_driver']
        if 'power_user' in power_data:
            data['power_parameters_power_user'] = power_data['power_user']
        if 'power_password' in power_data:
            data['power_parameters_power_pass'] = \
                power_data['power_password']
        return data

    def update(self, new, old):
        old_macs = set(v['mac_address'].lower() for v in old['interface_set'])
        if new['mac_addresses'].lower() not in old_macs:
            self._update = False
            LOG.info('Mac changed deleting old machine %s', old['system_id'])
            self._maas.delete(u'api/2.0/machines/{0}/'
                              .format(old['system_id']))
        else:
            new[self._update_key] = str(old[self._update_key])
        return new


class AssignMachinesIP(MaasObject):
    READY = 4
    DEPLOYED = 6

    def __init__(self):
        super(AssignMachinesIP, self).__init__()
        self._all_elements_url = None
        self._create_url = \
            (u'/api/2.0/nodes/{system_id}/interfaces/{interface_id}/',
             'link_subnet')
        self._config_path = 'region.machines'
        self._element_key = 'hostname'
        self._update_key = 'system_id'
        self._extra_data_urls = {'machines': (u'api/2.0/machines/',
                                              None, 'hostname')}

    def fill_data(self, name, data, machines):
        interface = data['interface']
        machine = machines[name]
        if machine['status'] == self.DEPLOYED:
            return
        if machine['status'] != self.READY:
            raise Exception('Not in ready state')
        if 'ip' not in interface:
            return
        data = {
            'mode': 'STATIC',
            'subnet': str(interface.get('subnet')),
            'ip_address': str(interface.get('ip')),
        }
        if 'default_gateway' in interface:
            data['default_gateway'] = interface.get('gateway')
        data['force'] = '1'
        data['system_id'] = str(machine['system_id'])
        data['interface_id'] = str(machine['interface_set'][0]['id'])
        return data


class DeployMachines(MaasObject):
    READY = 4
    DEPLOYED = 6

    def __init__(self):
        super(DeployMachines, self).__init__()
        self._all_elements_url = None
        self._create_url = (u'api/2.0/machines/{system_id}/', 'deploy')
        self._config_path = 'region.machines'
        self._element_key = 'hostname'
        self._extra_data_urls = {'machines': (u'api/2.0/machines/',
                                              None, 'hostname')}

    def fill_data(self, name, machine_data, machines):
        machine = machines[name]
        if machine['status'] == self.DEPLOYED:
            return
        if machine['status'] != self.READY:
            raise Exception('Not in ready state')
        data = {
            'system_id': machine['system_id'],
        }
        if 'distro_series' in machine_data:
            data['distro_series'] = machine_data['distro_series']
        if 'hwe_kernel' in machine_data:
            data['hwe_kernel'] = machine_data['hwe_kernel']
        return data

    def send(self, data):
        LOG.info('%s %s', self.__class__.__name__.lower(), _format_data(data))
        self._maas.post(u'api/2.0/machines/', 'allocate', system_id=data['system_id']).read()
        return self._maas.post(self._create_url[0].format(**data),
                                *self._create_url[1:], **data).read()

class BootResource(MaasObject):
    def __init__(self):
        super(BootResource, self).__init__()
        self._all_elements_url = u'api/2.0/boot-resources/'
        self._create_url = u'api/2.0/boot-resources/'
        self._update_url = u'api/2.0/boot-resources/{0}/'
        self._config_path = 'region.boot_resources'

    def fill_data(self, name, boot_data):
        sha256 = hashlib.sha256()
        sha256.update(file(boot_data['content']).read())
        data = {
            'name': name,
            'title': boot_data['title'],
            'architecture': boot_data['architecture'],
            'filetype': boot_data['filetype'],
            'size': str(os.path.getsize(boot_data['content'])),
            'sha256': sha256.hexdigest(),
            'content': io.open(boot_data['content']),
        }
        return data

    def update(self, new, old):
        self._update = False
        return new


class CommissioningScripts(MaasObject):
    def __init__(self):
        super(CommissioningScripts, self).__init__()
        self._all_elements_url = u'api/2.0/commissioning-scripts/'
        self._create_url = u'api/2.0/commissioning-scripts/'
        self._config_path = 'region.commissioning_scripts'
        self._update_url = u'api/2.0/commissioning-scripts/{0}'
        self._update_key = 'name'

    def fill_data(self, name, file_path):
        data = {
            'name': name,
            'content': io.open(file_path),
        }
        return data

    def update(self, new, old):
        return new


class MaasConfig(MaasObject):
    def __init__(self):
        super(MaasConfig, self).__init__()
        self._all_elements_url = None
        self._create_url = (u'api/2.0/maas/', u'set_config')
        self._config_path = 'region.maas_config'

    def fill_data(self, name, value):
        data = {
            'name': name,
            'value': str(value),
        }
        return data

    def update(self, new, old):
        self._update = False
        return new


class SSHPrefs(MaasObject):
    def __init__(self):
        super(SSHPrefs, self).__init__()
        self._all_elements_url = None
        self._create_url = u'api/2.0/account/prefs/sshkeys/'
        self._config_path = 'region.sshprefs'
        self._element_key = 'hostname'
        self._update_key = 'system_id'

    def fill_data(self, value):
        data = {
            'key': value,
        }
        return data

    def process(self):
        config = __salt__['config.get']('maas')
        for part in self._config_path.split('.'):
            config = config.get(part, {})
        extra = {}
        for name, url_call in self._extra_data_urls.iteritems():
            key = 'id'
            if isinstance(url_call, tuple):
                url_call, key = url_call[:]
            json_res = json.loads(self._maas.get(url_call).read())
            extra[name] = {v['name']: v[key] for v in json_res}
        if self._all_elements_url:
            all_elements = {}
            elements = self._maas.get(self._all_elements_url).read()
            res_json = json.loads(elements)
            for element in res_json:
                if isinstance(element, (str, unicode)):
                    all_elements[element] = {}
                else:
                    all_elements[element[self._element_key]] = element
        else:
            all_elements = {}
        ret = {
            'success': [],
            'errors': {},
            'updated': [],
        }
        for config_data in config:
            name = config_data[:10]
            try:
                data = self.fill_data(config_data, **extra)
                self.send(data)
                ret['success'].append(name)
            except urllib2.HTTPError as e:
                etxt = e.read()
                LOG.exception('Failed for object %s reason %s', name, etxt)
                ret['errors'][name] = str(etxt)
            except Exception as e:
                LOG.exception('Failed for object %s reason %s', name, e)
                ret['errors'][name] = str(e)
        if ret['errors']:
            raise Exception(ret)
        return ret


class Domain(MaasObject):
    def __init__(self):
        super(Domain, self).__init__()
        self._all_elements_url = u'/api/2.0/domains/'
        self._create_url = u'/api/2.0/domains/'
        self._config_path = 'region.domain'
        self._update_url = u'/api/2.0/domains/{0}/'

    def fill_data(self, value):
        data = {
            'name': value,
        }
        self._update = True
        return data

    def update(self, new, old):
        new['id'] = str(old['id'])
        new['authoritative'] = str(old['authoritative'])
        return new

    def process(self):
        ret = {
            'success': [],
            'errors': {},
            'updated': [],
        }
        config = __salt__['config.get']('maas')
        for part in self._config_path.split('.'):
            config = config.get(part, {})
        extra = {}
        for name, url_call in self._extra_data_urls.iteritems():
            key = 'id'
            if isinstance(url_call, tuple):
                url_call, key = url_call[:]
            json_res = json.loads(self._maas.get(url_call).read())
            extra[name] = {v['name']: v[key] for v in json_res}
        if self._all_elements_url:
            all_elements = {}
            elements = self._maas.get(self._all_elements_url).read()
            res_json = json.loads(elements)
            for element in res_json:
                if isinstance(element, (str, unicode)):
                    all_elements[element] = {}
                else:
                    all_elements[element[self._element_key]] = element
        else:
            all_elements = {}
        try:
            data = self.fill_data(config, **extra)
            data = self.update(data, all_elements.values()[0])
            self.send(data)
            ret['success'].append('domain')
        except urllib2.HTTPError as e:
            etxt = e.read()
            LOG.exception('Failed for object %s reason %s', 'domain', etxt)
            ret['errors']['domain'] = str(etxt)
        except Exception as e:
            LOG.exception('Failed for object %s reason %s', 'domain', e)
            ret['errors']['domain'] = str(e)
        if ret['errors']:
            raise Exception(ret)
        return ret


class MachinesStatus(MaasObject):
    @classmethod
    def execute(cls, objects_name=None):
        cls._maas = _create_maas_client()
        result = cls._maas.get(u'api/2.0/machines/')
        json_result = json.loads(result.read())
        res = []
        status_name_dict = dict([
            (0, 'New'), (1, 'Commissioning'), (2, 'Failed commissioning'),
            (3, 'Missing'), (4, 'Ready'), (5, 'Reserved'), (10, 'Allocated'),
            (9, 'Deploying'), (6, 'Deployed'), (7, 'Retired'), (8, 'Broken'),
            (11, 'Failed deployment'), (12, 'Releasing'),
            (13, 'Releasing failed'), (14, 'Disk erasing'),
            (15, 'Failed disk erasing')])
        summary = collections.Counter()
        if objects_name:
            if ',' in objects_name:
                objects_name = set(objects_name.split(','))
            else:
                objects_name = set([objects_name])
        for machine in json_result:
            if objects_name and machine['hostname'] not in objects_name:
                continue
            status = status_name_dict[machine['status']]
            summary[status] += 1
            res.append('hostname:{},system_id:{},status:{}'
                       .format(machine['hostname'], machine['system_id'],
                               status))
        return {'machines': res, 'summary': summary}


def process_fabrics():
    return Fabric().process()


def process_subnets():
    return Subnet().process()


def process_dhcp_snippets():
    return DHCPSnippet().process()


def process_package_repositories():
    return PacketRepository().process()


def process_devices(*args):
    return Device().process(*args)


def process_machines(*args):
    return Machine().process(*args)


def process_assign_machines_ip(*args):
    return AssignMachinesIP().process(*args)


def machines_status(*args):
    return MachinesStatus.execute(*args)


def deploy_machines(*args):
    return DeployMachines().process(*args)


def process_boot_resources():
    return BootResource().process()


def process_maas_config():
    return MaasConfig().process()


def process_commissioning_scripts():
    return CommissioningScripts().process()


def process_domain():
    return Domain().process()


def process_sshprefs():
    return SSHPrefs().process()
