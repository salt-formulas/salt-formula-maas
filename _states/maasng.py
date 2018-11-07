import logging
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


def __virtual__():
    """
    Load MaaSng module
    """
    return 'maasng'


def maasng(funcname, *args, **kwargs):
    """
    Simple wrapper, for __salt__ maasng
    :param funcname:
    :param args:
    :param kwargs:
    :return:
    """
    return __salt__['maasng.{}'.format(funcname)](*args, **kwargs)


def merge2dicts(d1, d2):
    z = d1.copy()
    z.update(d2)
    return z


def disk_layout_present(hostname, layout_type, root_size=None, root_device=None,
                        volume_group=None, volume_name=None, volume_size=None,
                        disk={}, **kwargs):
    '''
    Ensure that the disk layout does exist

    :param name: The name of the cloud that should not exist
    '''
    ret = {'name': hostname,
           'changes': {},
           'result': True,
           'comment': 'Disk layout "{0}" updated'.format(hostname)}

    machine = __salt__['maasng.get_machine'](hostname)
    if "error" in machine:
        if 0 in machine["error"]:
            ret['comment'] = "No such machine {0}".format(hostname)
            ret['changes'] = machine
        else:
            ret['comment'] = "State execution failed for machine {0}".format(hostname)
            ret['result'] = False
            ret['changes'] = machine
        return ret

    if machine["status_name"] != "Ready":
        ret['comment'] = 'Machine {0} is not in Ready state.'.format(hostname)
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Disk layout will be updated on {0}, this action will delete current layout.'.format(
            hostname)
        return ret

    if layout_type == "flat":

        ret["changes"] = __salt__['maasng.update_disk_layout'](
            hostname, layout_type, root_size, root_device)

    elif layout_type == "lvm":

        ret["changes"] = __salt__['maasng.update_disk_layout'](
            hostname, layout_type, root_size, root_device, volume_group, volume_name, volume_size)

    elif layout_type == "custom":
        ret["changes"] = __salt__[
            'maasng.update_disk_layout'](hostname, layout_type)

    else:
        ret["comment"] = "Not supported layout provided. Choose flat or lvm"
        ret['result'] = False

    return ret


def raid_present(hostname, name, level, devices=[], partitions=[],
                 partition_schema={}):
    '''
    Ensure that the raid does exist

    :param name: The name of the cloud that should not exist
    '''

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Raid {0} presented on {1}'.format(name, hostname)}

    machine = __salt__['maasng.get_machine'](hostname)
    if "error" in machine:
        if 0 in machine["error"]:
            ret['comment'] = "No such machine {0}".format(hostname)
            ret['changes'] = machine
        else:
            ret['comment'] = "State execution failed for machine {0}".format(
                hostname)
            ret['result'] = False
            ret['changes'] = machine
        return ret

    if machine["status_name"] != "Ready":
        ret['comment'] = 'Machine {0} is not in Ready state.'.format(hostname)
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Raid {0} will be updated on {1}'.format(
            name, hostname)
        return ret

    # Validate that raid exists
    # With correct devices/partition
    # OR
    # Create raid

    ret["changes"] = __salt__['maasng.create_raid'](
        hostname=hostname, name=name, level=level, disks=devices, partitions=partitions)

    # TODO partitions
    ret["changes"].update(disk_partition_present(
        hostname, name, partition_schema)["changes"])

    if "error" in ret["changes"]:
        ret["result"] = False

    return ret


def disk_partition_present(hostname, name, partition_schema={}):
    '''
    Ensure that the disk has correct partititioning schema

    :param name: The name of the cloud that should not exist
    '''

    # 1. Validate that disk has correct values for size and mount
    # a. validate count of partitions
    # b. validate size of partitions
    # 2. If not delete all partitions on disk and recreate schema
    # 3. Validate type exists
    # if should not exits
    # delete mount and unformat
    # 4. Validate mount exists
    # 5. if not enforce umount or mount

    ret = {'name': hostname,
           'changes': {},
           'result': True,
           'comment': 'Disk layout {0} presented'.format(name)}

    machine = __salt__['maasng.get_machine'](hostname)
    if "error" in machine:
        if 0 in machine["error"]:
            ret['comment'] = "No such machine {0}".format(hostname)
            ret['changes'] = machine
        else:
            ret['comment'] = "State execution failed for machine {0}".format(
                hostname)
            ret['result'] = False
            ret['changes'] = machine
        return ret

    if machine["status_name"] != "Ready":
        ret['comment'] = 'Machine {0} is not in Ready state.'.format(hostname)
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Partition schema will be changed on {0}'.format(name)
        return ret

    partitions = __salt__['maasng.list_partitions'](hostname, name)

    # Calculate actual size in bytes from provided data
    for part_name, part in partition_schema.iteritems():
        size, unit = part["size"][:-1], part["size"][-1]
        part["calc_size"] = int(size) * SIZE[unit]

    if len(partitions) == len(partition_schema):

        for part_name, part in partition_schema.iteritems():
            LOG.info('validated {0}'.format(part["calc_size"]))
            LOG.info('validated {0}'.format(
                int(partitions[name+"-"+part_name.split("-")[-1]]["size"])))
            if part["calc_size"] == int(partitions[name+"-"+part_name.split("-")[-1]]["size"]):
                LOG.info('validated')
                # TODO validate size (size from maas is not same as calculate?)
                # TODO validate mount
                # TODO validate fs type
            else:
                LOG.info('breaking')
                break
            return ret

    #DELETE and RECREATE
    LOG.info('delete')
    for partition_name, partition in partitions.iteritems():
        LOG.info(partition)
        # TODO IF LVM create ERROR
        ret["changes"] = __salt__['maasng.delete_partition_by_id'](
            hostname, name, partition["id"])

    LOG.info('recreating')
    for part_name, part in partition_schema.iteritems():
        LOG.info("partitition for creation")
        LOG.info(part)
        if "mount" not in part:
            part["mount"] = None
        if "type" not in part:
            part["type"] = None
        ret["changes"] = __salt__['maasng.create_partition'](
            hostname, name, part["size"], part["type"], part["mount"])

    if "error" in ret["changes"]:
        ret["result"] = False

    return ret


def volume_group_present(hostname, name, devices=[], partitions=[]):
    '''
    Ensure that the disk layout does exist

    :param name: The name of the cloud that should not exist
    '''
    ret = {'name': hostname,
           'changes': {},
           'result': True,
           'comment': 'LVM group {0} presented on {1}'.format(name, hostname)}

    machine = __salt__['maasng.get_machine'](hostname)
    if "error" in machine:
        if 0 in machine["error"]:
            ret['comment'] = "No such machine {0}".format(hostname)
            ret['changes'] = machine
        else:
            ret['comment'] = "State execution" \
                             "failed for machine {0}".format(hostname)
            ret['result'] = False
            ret['changes'] = machine
        return ret

    if machine["status_name"] != "Ready":
        ret['comment'] = 'Machine {0} is not in Ready state.'.format(hostname)
        return ret

    # TODO validation if exists
    vgs = __salt__['maasng.list_volume_groups'](hostname)

    if name in vgs:
        # TODO validation for devices and partitions
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'LVM group {0} will be updated on {1}'.format(
            name, hostname)
        return ret

    ret["changes"] = __salt__['maasng.create_volume_group'](
        hostname, name, devices, partitions)

    if "error" in ret["changes"]:
        ret["result"] = False

    return ret


def volume_present(hostname, name, volume_group_name, size, type=None,
                   mount=None):
    """
    Ensure that the disk layout does exist

    :param name: The name of the cloud that should not exist
    """

    ret = {'name': hostname,
           'changes': {},
           'result': True,
           'comment': 'LVM group {0} presented on {1}'.format(name, hostname)}

    machine = __salt__['maasng.get_machine'](hostname)
    if "error" in machine:
        if 0 in machine["error"]:
            ret['comment'] = "No such machine {0}".format(hostname)
            ret['changes'] = machine
        else:
            ret['comment'] = "State execution failed for machine {0}".format(
                hostname)
            ret['result'] = False
            ret['changes'] = machine
        return ret

    if machine["status_name"] != "Ready":
        ret['comment'] = 'Machine {0} is not in Ready state.'.format(hostname)
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'LVM volume {0} will be updated on {1}'.format(
            name, hostname)

    # TODO validation if exists

    ret["changes"] = __salt__['maasng.create_volume'](
        hostname, name, volume_group_name, size, type, mount)

    return ret


def select_boot_disk(hostname, name):
    '''
    Select disk that will be used to boot partition

    :param name: The name of disk on machine
    :param hostname: The hostname of machine
    '''

    ret = {'name': hostname,
           'changes': {},
           'result': True,
           'comment': 'LVM group {0} presented on {1}'.format(name, hostname)}

    machine = __salt__['maasng.get_machine'](hostname)
    if "error" in machine:
        if 0 in machine["error"]:
            ret['comment'] = "No such machine {0}".format(hostname)
            ret['changes'] = machine
        else:
            ret['comment'] = "State execution" \
                             "failed for machine {0}".format(hostname)
            ret['result'] = False
            ret['changes'] = machine
        return ret

    if machine["status_name"] != "Ready":
        ret['comment'] = 'Machine {0} is not in Ready state.'.format(hostname)
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'LVM volume {0}' \
                         'will be updated on {1}'.format(name, hostname)

    # TODO disk validation if exists

    ret["changes"] = __salt__['maasng.set_boot_disk'](hostname, name)

    return ret


def vlan_present_in_fabric(name, fabric, vlan, primary_rack, description='', dhcp_on=False, mtu=1500):
    """

    :param name: Name of vlan
    :param fabric: Name of fabric
    :param vlan: Vlan id
    :param mtu: MTU
    :param description: Description of vlan
    :param dhcp_on: State of dhcp
    :param primary_rack: primary_rack

    """

    ret = {'name': fabric,
           'changes': {},
           'result': True,
           'comment': 'Module function maasng.update_vlan executed'}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Vlan {0} will be updated for {1}'.format(
            vlan, fabric)
        return ret
    # Check, that vlan  already defined
    _rez = __salt__['maasng.check_vlan_in_fabric'](fabric=fabric,
                                                   vlan=vlan)
    if _rez == 'not_exist':
        changes = __salt__['maasng.create_vlan_in_fabric'](name=name,
                                                           fabric=fabric,
                                                           vlan=vlan,
                                                           mtu=mtu,
                                                           description=description,
                                                           primary_rack=primary_rack,
                                                           dhcp_on=dhcp_on)
        ret['comment'] = 'Vlan {0} has ' \
                         'been created for {1}'.format(name, fabric)
    elif _rez == 'update':
        _id = __salt__['maasng.list_vlans'](fabric)[vlan]['id']
        changes = __salt__['maasng.create_vlan_in_fabric'](name=name,
                                                           fabric=fabric,
                                                           vlan=vlan,
                                                           mtu=mtu,
                                                           description=description,
                                                           primary_rack=primary_rack,
                                                           dhcp_on=dhcp_on,
                                                           update=True,
                                                           vlan_id=_id)
        ret['comment'] = 'Vlan {0} has been ' \
                         'updated for {1}'.format(name, fabric)
    ret['changes'] = changes

    if "error" in changes:
        ret['comment'] = "State execution failed for fabric {0}".format(fabric)
        ret['result'] = False
        return ret

    return ret


def boot_source_present(url, keyring_file='', keyring_data='',
                        delete_undefined_sources=False,
                        delete_undefined_sources_except_urls=[]):
    """
    Process maas boot-sources: link to maas-ephemeral repo


    :param url:               The URL of the BootSource.
    :param keyring_file:      The path to the keyring file for this BootSource.
    :param keyring_data:      The GPG keyring for this BootSource, base64-encoded data.
    :param delete_undefined_sources:  Delete all boot-sources, except defined in reclass
    """
    ret = {'name': url,
           'changes': {},
           'result': True,
           'comment': 'boot-source {0} presented'.format(url)}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'boot-source {0} will be updated'.format(url)
    maas_boot_sources = maasng('get_boot_source')
    # TODO implement check and update for keyrings!
    if url in maas_boot_sources.keys():
        ret["result"] = True
        ret["comment"] = 'boot-source {0} alredy exist'.format(url)
    else:
        ret["changes"] = maasng('create_boot_source', url,
                                keyring_filename=keyring_file,
                                keyring_data=keyring_data)
    if delete_undefined_sources:
        ret["changes"] = merge2dicts(ret.get('changes', {}),
                                     maasng('boot_sources_delete_all_others',
                                            except_urls=delete_undefined_sources_except_urls))
        # Re-import data
    return ret


def boot_sources_selections_present(bs_url, os, release, arches="*",
                                    subarches="*", labels="*", wait=True):
    """
    Process maas boot-sources selection: set of resource configurathions,
    to be downloaded from boot-source bs_url.

    :param bs_url:    Boot-source url
    :param os:        The OS (e.g. ubuntu, centos) for which to import
                      resources.Required.
    :param release:   The release for which to import resources. Required.
    :param arches:    The architecture list for which to import resources.
    :param subarches: The subarchitecture list for which to import resources.
    :param labels:    The label lists for which to import resources.
    :param wait:      Initiate import and wait for done.

    """
    ret = {'name': bs_url,
           'changes': {},
           'result': True,
           'comment': 'boot-source {0} selection present'.format(bs_url)}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'boot-source {0}' \
                         'selection will be updated'.format(bs_url)

    maas_boot_sources = maasng('get_boot_source')
    if bs_url not in maas_boot_sources.keys():
        ret["result"] = False
        ret["comment"] = 'Requested boot-source' \
                         '{0} not exist! Unable' \
                         'to proceed selection for it'.format(bs_url)
        return ret

    ret = maasng('create_boot_source_selections', bs_url, os, release,
                 arches=arches,
                 subarches=subarches,
                 labels=labels,
                 wait=wait)
    return ret


def iprange_present(name, type_range, start_ip, end_ip, subnet=None,
                    comment=None):
    """

    :param name: Name of iprange
    :param type_range: Type of iprange
    :param start_ip: Start ip of iprange
    :param end_ip: End ip of iprange
    :param comment: Comment for specific iprange

    """

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Module function maasng.iprange_present executed'}

    # Check, that range  already defined
    _rez = __salt__['maasng.get_startip'](start_ip)
    if 'start_ip' in _rez.keys():
        if _rez["start_ip"] == start_ip:
            ret['comment'] = 'Iprange {0} already exist.'.format(name)
            return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Ip range {0} will be ' \
                         'created with start ip: {1} ' \
                         'and end ip: {2} and ' \
                         'type {3}'.format(name, start_ip, end_ip, type_range)
        return ret

    changes = __salt__['maasng.create_iprange'](type_range=type_range,
                                                start_ip=start_ip,
                                                end_ip=end_ip, subnet=subnet, comment=comment)
    ret["changes"] = changes
    if "error" in changes:
        ret['comment'] = "State execution failed for iprange {0}".format(name)
        ret['result'] = False
        return ret
    return ret


def subnet_present(cidr, name, fabric, gateway_ip, vlan):
    """

    :param cidr: Cidr for subnet
    :param name: Name of subnet
    :param fabric: Name of fabric for subnet
    :param gateway_ip: gateway_ip

    """

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Module function maasng.subnet_present executed'}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Subnet {0} will be created for {1}'.format(
            name, fabric)
        return ret
    # Check, that subnet already defined
    _rez = __salt__['maasng.check_subnet'](cidr, name, fabric, gateway_ip)
    if _rez == 'not_exist':
        changes = __salt__['maasng.create_subnet'](cidr=cidr, name=name,
                                                   fabric=fabric,
                                                   gateway_ip=gateway_ip,
                                                   vlan=vlan)
        ret['comment'] = 'Subnet {0} ' \
                         'has been created for {1}'.format(name, fabric)
    elif _rez == 'update':
        _id = __salt__['maasng.list_subnets'](sort_by='cidr')[cidr]['id']
        changes = __salt__['maasng.create_subnet'](cidr=cidr, name=name,
                                                   fabric=fabric,
                                                   gateway_ip=gateway_ip,
                                                   vlan=vlan, update=True,
                                                   subnet_id=_id)
        ret['comment'] = 'Subnet {0} ' \
                         'has been updated for {1}'.format(name, fabric)

    if "error" in changes:
        ret['comment'] = "State execution failed for subnet {0}".format(name)
        ret['result'] = False
        ret['changes'] = changes
        return ret

    return ret


def fabric_present(name, description=None):
    """

    :param name: Name of fabric
    :param description: Name of description

    """

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Module function maasng.fabric_present executed'}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'fabric {0} will be updated'.format(name)
        return ret
    # All requested subnets
    _r_subnets = __salt__['config.get']('maas').get('region', {}).get('subnets',
                                                                      {})
    # Assumed subnet CIDrs, expected to be in requested fabric
    _a_subnets = [_r_subnets[f]['cidr'] for f in _r_subnets.keys() if
                  _r_subnets[f]['fabric'] == name]
    _rez = __salt__['maasng.check_fabric_guess_with_cidr'](name=name,
                                                           cidrs=_a_subnets)

    if 'not_exist' in _rez:
        changes = __salt__['maasng.create_fabric'](name=name,
                                                   description=description)
        ret['new'] = 'Fabric {0} has been created'.format(name)
    elif 'update' in _rez:
        f_id = _rez['update']
        changes = __salt__['maasng.create_fabric'](name=name,
                                                   description=description,
                                                   update=True, fabric_id=f_id)
        ret['new'] = 'Fabric {0} has been updated'.format(name)
    ret['changes'] = changes

    if "error" in changes:
        ret['comment'] = "State execution failed for fabric {0}".format(fabric)
        ret['result'] = False
        return ret

    return ret


def sshkey_present(name, sshkey):
    """

    :param name: Name of user
    :param sshkey: SSH key for MAAS user

    """

    ret = {'name': name,
           'changes': {},
           'result': True,
           'comment': 'Module function maasng.ssshkey_present executed'}

    # Check, that subnet already defined
    _rez = __salt__['maasng.get_sshkey'](sshkey)
    if 'key' in _rez.keys():
        if _rez["key"] == sshkey:
            ret['comment'] = 'SSH key {0} already exist for user {1}.'.format(
                sshkey, name)
            return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'SSH  key {0} will be add it to MAAS for user {1}'.format(
            sshkey, name)

        return ret

    changes = __salt__['maasng.add_sshkey'](sshkey=sshkey)
    ret['comment'] = 'SSH-key {0} ' \
        'has been added for user {1}'.format(sshkey, name)

    ret['changes'] = changes

    if "error" in changes:
        ret['comment'] = "State execution failed for sshkey: {0}".format(
            sshkey)
        ret['result'] = False
        ret['changes'] = changes
        return ret

    return ret
