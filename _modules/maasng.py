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

import collections
import copy
import hashlib
import io
import json
import logging
import os.path
import time
import urllib2
# Salt utils
from salt.exceptions import CommandExecutionError, SaltInvocationError

LOG = logging.getLogger(__name__)

SIZE = {
    "M": 1000000,
    "G": 1000000000,
    "T": 1000000000000,
}

RAID = {
    0: "raid-0",
    1: "raid-1",
    5: "raid-5",
    10: "raid-10",
}

# Import third party libs
HAS_MASS = False
try:
    from maas_client import MAASClient, MAASDispatcher, MAASOAuth
    HAS_MASS = True
except ImportError:
    LOG.debug('Missing MaaS client module is Missing. Skipping')


def __virtual__():
    '''
    Only load this module if maas-client
    is installed on this minion.
    '''
    if HAS_MASS:
        return 'maasng'
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


def _get_blockdevice_id_by_name(hostname, device):

    # TODO validation
    return list_blockdevices(hostname)[device]["id"]


def _get_volume_group_id_by_name(hostname, device):

    # TODO validation
    return list_volume_groups(hostname)[device]["id"]


def _get_partition_id_by_name(hostname, device, partition):

    # TODO validation
    return list_partitions(hostname, device)[partition]["id"]

# MACHINE SECTION


def get_machine(hostname):
    '''
    Get information aboout specified machine

    CLI Example:

    .. code-block:: bash

        salt-call maasng.get_machine server_hostname
    '''
    try:
        return list_machines()[hostname]
    except KeyError:
        return {"error": "Machine not found on MaaS server"}


def list_machines():
    '''
    Get list of all machines from maas server

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.list_machines
    '''
    machines = {}
    maas = _create_maas_client()
    json_res = json.loads(maas.get(u'api/2.0/machines/').read())
    for item in json_res:
        machines[item["hostname"]] = item
    return machines


def create_machine():
    # TODO

    return False


def update_machine():
    # TODO

    return False

# MACHINE OPERATIONS
# TODO

# RAID SECTION


def create_raid(hostname, name, level, disks=[], partitions=[], **kwargs):
    '''
    Create new raid on machine.

    CLI Example:

    .. code-block:: bash

        salt-call maasng.create_raid hostname=kvm03 name=md0 level=1 disks=[vdb,vdc] partitions=[vdd-part1,vde-part1]
    '''

    result = {}

    if len(disks) == 0 and len(partitions) == 0:
        result["error"] = "Disks or partitions need to be provided"

    disk_ids = []
    partition_ids = []

    for disk in disks:
        try:
            disk_ids.append(str(_get_blockdevice_id_by_name(hostname, disk)))
        except KeyError:
            result["error"] = "Device {0} does not exists on machine {1}".format(
                disk, hostname)
            return result

    for partition in partitions:
        try:
            device = partition.split("-")[0]
            device_part = list_partitions(hostname, device)
            partition_ids.append(str(device_part[partition]["id"]))
        except KeyError:
            result["error"] = "Partition {0} does not exists on machine {1}".format(
                partition, hostname)
            return result

    data = {
        "name": name,
        "level": RAID[int(level)],
        "block_devices": disk_ids,
        "partitions": partition_ids,
    }

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    # TODO validation
    LOG.info(data)
    json_res = json.loads(
        maas.post(u"api/2.0/nodes/{0}/raids/".format(system_id), None, **data).read())
    LOG.info(json_res)
    result["new"] = "Raid {0} created".format(name)

    return result


def list_raids(hostname):
    '''
    Get list all raids on machine

    CLI Example:

    .. code-block:: bash

        salt-call maasng.list_raids server_hostname
    '''

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)
    # TODO validation
    json_res = json.loads(
        maas.get(u"api/2.0/nodes/{0}/raids/".format(system_id)).read())
    LOG.info(json_res)

    # TODO return list of raid devices
    return True


def get_raid(hostname, name):
    '''
    Get information about specific raid on machine

    CLI Example:

    .. code-block:: bash

        salt-call maasng.get_raids server_hostname md0
    '''

    return list_raids(hostname)[name]


# BLOCKDEVICES SECTION

def list_blockdevices(hostname):
    '''
    Get list of all blockdevices (disks) on machine

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.list_blockdevices server_hostname
        salt-call maasng.list_blockdevices server_hostname
    '''
    ret = {}

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    # TODO validation if exists

    json_res = json.loads(
        maas.get(u"api/2.0/nodes/{0}/blockdevices/".format(system_id)).read())
    LOG.info(json_res)
    for item in json_res:
        ret[item["name"]] = item

    return ret


def get_blockdevice(hostname, name):
    '''
    Get information about blockdevice (disk) on machine

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.get_blockdevice server_hostname sda
        salt-call maasng.get_blockdevice server_hostname sda
    '''

    return list_blockdevices(hostname)[name]


# PARTITIONS

def list_partitions(hostname, device):
    '''
    Get list of all partitions on specific device located on specific machine

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.list_partitions server_hostname sda
        salt-call maasng.list_partitions server_hostname sda
    '''
    ret = {}
    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    partitions = get_blockdevice(hostname, device)["partitions"]
    LOG.info(partitions)

    #json_res = json.loads(maas.get(u"api/2.0/nodes/{0}/blockdevices/{1}/partitions/".format(system_id, device_id)).read())
    # LOG.info(json_res)

    if len(device) > 0:
        for item in partitions:
            name = item["path"].split('/')[-1]
            ret[name] = item

    return ret


def get_partition(hostname, device, partition):
    '''
    Get information about specific parition on device located on machine

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.get_partition server_hostname disk_name partition
        salt-call maasng.get_partition server_hostname disk_name partition

        root_size = size in GB
    '''

    return list_partitions(partition)[name]


def create_partition(hostname, disk, size, fs_type=None, mount=None):
    '''
    Create new partition on device.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.create_partition server_hostname disk_name 10 ext4 "/"
        salt-call maasng.create_partition server_hostname disk_name 10 ext4 "/"
    '''
    # TODO validation
    result = {}
    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    device_id = _get_blockdevice_id_by_name(hostname, disk)
    LOG.info(device_id)

    value, unit = size[:-1], size[-1]
    calc_size = str(int(value) * SIZE[unit])
    LOG.info(calc_size)

    data = {
        "size": calc_size
    }

    # TODO validation
    partition = json.loads(maas.post(
        u"api/2.0/nodes/{0}/blockdevices/{1}/partitions/".format(system_id, device_id), None, **data).read())
    LOG.info(partition)
    result["partition"] = "Partition created on {0}".format(disk)

    if fs_type != None:
        data_fs_type = {
            "fstype": fs_type
        }
        partition_id = str(partition["id"])
        LOG.info("Partition id: " + partition_id)
        # TODO validation
        json_res = json.loads(maas.post(u"api/2.0/nodes/{0}/blockdevices/{1}/partition/{2}".format(
            system_id, device_id, partition_id), "format", **data_fs_type).read())
        LOG.info(json_res)
        result["filesystem"] = "Filesystem {0} created".format(fs_type)

    if mount != None:
        data = {
            "mount_point": mount
        }

        # TODO validation
        json_res = json.loads(maas.post(u"api/2.0/nodes/{0}/blockdevices/{1}/partition/{2}".format(
            system_id, device_id, str(partition['id'])), "mount", **data).read())
        LOG.info(json_res)
        result["mount"] = "Mount point {0} created".format(mount)

    return result


def delete_partition(hostname, disk, partition_name):
    '''
    Delete partition on device.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.delete_partition server_hostname disk_name partition_name
        salt-call maasng.delete_partition server_hostname disk_name partition_name

        root_size = size in GB
    '''
    result = {}
    data = {}
    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    device_id = _get_blockdevice_id_by_name(hostname, disk)
    LOG.info(device_id)

    partition_id = _get_partition_id_by_name(hostname, disk, partition_name)

    maas.delete(u"api/2.0/nodes/{0}/blockdevices/{1}/partition/{2}".format(
        system_id, device_id, partition_id)).read()
    result["new"] = "Partition {0} deleted".format(partition_name)
    return result


def delete_partition_by_id(hostname, disk, partition_id):
    '''
    Delete partition on device. Partition spefified by id of parition

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.delete_partition_by_id server_hostname disk_name partition_id
        salt-call maasng.delete_partition_by_id server_hostname disk_name partition_id

        root_size = size in GB
    '''
    result = {}
    data = {}
    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    device_id = _get_blockdevice_id_by_name(hostname, disk)
    LOG.info(device_id)

    maas.delete(u"api/2.0/nodes/{0}/blockdevices/{1}/partition/{2}".format(
        system_id, device_id, partition_id)).read()
    result["new"] = "Partition {0} deleted".format(partition_id)
    return result

# CREATE DISK LAYOUT
# TODO


def update_disk_layout(hostname, layout, root_size=None, root_device=None, volume_group=None, volume_name=None, volume_size=None):
    '''
    Update disk layout. Flat or LVM layout supported.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.update_disk_layout server_hostname lvm root_size=None, root_device=None, volume_group=None, volume_name=None, volume_size=None
        salt-call maasng.update_disk_layout server_hostname lvm root_size=None, root_device=None, volume_group=None, volume_name=None, volume_size=None

        root_size = size in GB
    '''
    result = {}
    data = {
        "storage_layout": layout,
    }

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    if root_size != None:
        bit_size = str(root_size * 1073741824)
        LOG.info(bit_size)
        data["root_size"] = bit_size

    if root_device != None:
        LOG.info(root_device)
        data["root_device"] = str(
            _get_blockdevice_id_by_name(hostname, root_device))

    if layout == 'lvm':
        if volume_group != None:
            LOG.info(volume_group)
            data["vg_name"] = volume_group
        if volume_name != None:
            LOG.info(volume_name)
            data["lv_name"] = volume_name
        if volume_size != None:
            vol_size = str(volume_size * 1073741824)
            LOG.info(vol_size)
            data["lv_size"] = vol_size

    # TODO validation
    json_res = json.loads(maas.post(
        u"api/2.0/machines/{0}/".format(system_id), "set_storage_layout", **data).read())
    LOG.info(json_res)
    result["new"] = {
        "storage_layout": layout,
    }

    return result


# LVM
# TODO

def list_volume_groups(hostname):
    '''
    Get list of all volume group on machine.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.list_volume_groups server_hostname
        salt-call maasng.list_volume_groups server_hostname
    '''
    volume_groups = {}

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    # TODO validation if exists

    json_res = json.loads(
        maas.get(u"api/2.0/nodes/{0}/volume-groups/".format(system_id)).read())
    LOG.info(json_res)
    for item in json_res:
        volume_groups[item["name"]] = item
    # return
    return volume_groups


def get_volume_group(hostname, name):
    '''
    Get information about specific volume group on machine.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.list_blockdevices server_hostname
        salt-call maasng.list_blockdevices server_hostname
    '''
    # TODO validation that exists
    return list_volume_groups(hostname)[name]


def create_volume_group(hostname, volume_group_name, disks=[], partitions=[]):
    '''
    Create new volume group on machine. Disks or partitions needs to be provided.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.create_volume_group volume_group_name, disks=[sda,sdb], partitions=[]
        salt-call maasng.create_volume_group server_hostname
    '''
    result = {}

    data = {
        "name": volume_group_name,
    }

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    disk_ids = []
    partition_ids = []

    for disk in disks:
        p_disk = get_blockdevice(hostname, disk)
        if p_disk["partition_table_type"] == None:
            disk_ids.append(str(p_disk["id"]))
        else:
            result["error"] = "Device {0} on machine {1} cointains partition table".format(
                disk, hostname)
            return result

    for partition in partitions:
        try:
            device = partition.split("-")[0]
            device_part = list_partitions(hostname, device)
            partition_ids.append(str(device_part[partition]["id"]))
        except KeyError:
            result["error"] = "Partition {0} does not exists on machine {1}".format(
                partition, hostname)
            return result

    data["block_devices"] = disk_ids
    data["partitions"] = partition_ids
    LOG.info(partition_ids)
    LOG.info(partitions)

    # TODO validation
    json_res = json.loads(maas.post(
        u"api/2.0/nodes/{0}/volume-groups/".format(system_id), None, **data).read())
    LOG.info(json_res)
    result["new"] = "Volume group {0} created".format(json_res["name"])

    return result


def delete_volume_group(hostname, name):
    '''
    Delete volume group on machine.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.delete_volume_group server_hostname vg0
        salt-call maasng.delete_volume_group server_hostname vg0
    '''

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    # TODO partitions
    # for partition in partitions:
    #    temp = disk.split("-")
    #    disk_ids.append(str(_get_blockdevice_id_by_name(hostname, temp[] partition)))

    # TODO partitions
    vg_id = name

    # TODO validation
    json_res = json.loads(maas.delete(
        u"api/2.0/nodes/{0}/volume-group/{1}/".format(system_id, vg_id)).read())
    LOG.info(json_res)

    return True


def create_volume(hostname, volume_name, volume_group, size, fs_type=None, mount=None):
    '''
    Create volume on volume group.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.create_volume server_hostname volume_name, volume_group, size, fs_type=None, mount=None
        salt-call maasng.create_volume server_hostname volume_name, volume_group, size, fs_type=None, mount=None
    '''

    data = {
        "name": volume_name,
    }

    value, unit = size[:-1], size[-1]
    bit_size = str(int(value) * SIZE[unit])
    LOG.info(bit_size)

    data["size"] = bit_size

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    LOG.info(system_id)

    volume_group_id = str(_get_volume_group_id_by_name(hostname, volume_group))

    LOG.info(volume_group_id)

    # TODO validation
    json_res = json.loads(maas.post(u"api/2.0/nodes/{0}/volume-group/{1}/".format(
        system_id, volume_group_id), "create_logical_volume", **data).read())
    LOG.info(json_res)

    if fs_type != None or mount != None:
        ret = create_volume_filesystem(
            hostname, volume_group + "-" + volume_name, fs_type, mount)

    return True


def create_volume_filesystem(hostname, device, fs_type=None, mount=None):

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]

    blockdevices_id = _get_blockdevice_id_by_name(hostname, device)
    data = {}
    if fs_type != None:
        data["fstype"] = fs_type
        # TODO validation
        json_res = json.loads(maas.post(u"/api/2.0/nodes/{0}/blockdevices/{1}/".format(
            system_id, blockdevices_id), "format", **data).read())
        LOG.info(json_res)

    if mount != None:
        data["mount_point"] = mount
        # TODO validation
        json_res = json.loads(maas.post(u"/api/2.0/nodes/{0}/blockdevices/{1}/".format(
            system_id, blockdevices_id), "mount", **data).read())
        LOG.info(json_res)

    return True


def create_partition_filesystem(hostname, partition, fs_type=None, mount=None):

    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]

    blockdevices_id = _get_blockdevice_id_by_name(hostname, device)
    data = {}
    if fs_type != None:
        data["fstype"] = fs_type
        # TODO validation
        json_res = json.loads(maas.post(u"/api/2.0/nodes/{0}/blockdevices/{1}/".format(
            system_id, blockdevices_id), "format", **data).read())
        LOG.info(json_res)

    if mount != None:
        data["mount_point"] = mount
        # TODO validation
        json_res = json.loads(maas.post(u"/api/2.0/nodes/{0}/blockdevices/{1}/".format(
            system_id, blockdevices_id), "mount", **data).read())
        LOG.info(json_res)

    return True


def set_boot_disk(hostname, name):
    '''
    Create volume on volume group.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.set_boot_disk server_hostname disk_name
        salt-call maasng.set_boot_disk server_hostname disk_name
    '''
    data = {}
    result = {}
    maas = _create_maas_client()
    system_id = get_machine(hostname)["system_id"]
    blockdevices_id = _get_blockdevice_id_by_name(hostname, name)

    maas.post(u"/api/2.0/nodes/{0}/blockdevices/{1}/".format(
        system_id, blockdevices_id), "set_boot_disk", **data).read()
    # TODO validation for error response (disk does not exists and node does not exists)
    result["new"] = "Disk {0} was set as bootable".format(name)

    return result


def list_fabric():
    '''
    Get list of all fabric

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.list_fabric
    '''
    fabrics = {}
    maas = _create_maas_client()
    json_res = json.loads(maas.get(u'api/2.0/fabrics/').read())
    LOG.info(json_res)
    for item in json_res:
        fabrics[item["name"]] = item
    return fabrics


def create_fabric(name):
    '''
    Create new fabric.

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.create_fabric
    '''
    result = {}
    data = {
        "name": name,
        "description": '',
        "class_type": '',

    }

    maas = _create_maas_client()
    json_res = json.loads(maas.post(u"api/2.0/fabrics/", None, **data).read())
    LOG.info(json_res)
    result["new"] = "Fabrics {0} created".format(json_res["name"])
    return result


def list_subnet():
    '''
    Get list of all subnets

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.list_subnet
    '''
    subnets = {}
    maas = _create_maas_client()
    json_res = json.loads(maas.get(u'api/2.0/subnets/').read())
    LOG.info(json_res)
    for item in json_res:
        subnets[item["name"]] = item
    return subnets


def list_vlans(fabric):
    '''
    Get list of all vlans for specific fabric

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.list_vlans
    '''
    vlans = {}
    maas = _create_maas_client()
    fabric_id = get_fabric(fabric)

    json_res = json.loads(
        maas.get(u'api/2.0/fabrics/{0}/vlans/'.format(fabric_id)).read())
    LOG.info(json_res)
    for item in json_res:
        vlans[item["name"]] = item
    return vlans


def get_fabric(fabric):
    '''
    Get id for specific fabric

    CLI Example:

    .. code-block:: bash

        salt-call maasng.get_fabric fabric_name
    '''
    try:
        return list_fabric()[fabric]['id']
    except KeyError:
        return {"error": "Frabic not found on MaaS server"}


def update_vlan(name, fabric, vid, description, dhcp_on=False):
    '''
    Update vlan

    CLI Example:

    .. code-block:: bash

        salt 'maas-node' maasng.update_vlan name, fabric, vid, description, dhcp_on
    '''
    result = {}

    data = {
        "name": name,
        "dhcp_on": str(dhcp_on),
        "description": description,
    }
    maas = _create_maas_client()
    fabric_id = get_fabric(fabric)

    json_res = json.loads(maas.put(
        u'api/2.0/fabrics/{0}/vlans/{1}/'.format(fabric_id, vid), **data).read())
    print(json_res)
    result["new"] = "Vlan {0} was updated".format(json_res["name"])

    return result
