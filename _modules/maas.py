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

import logging
import os

LOG = logging.getLogger(__name__)

# Import third party libs
HAS_MASS = False
try:
    from apiclient.maas_client import MAASClient, MAASDispatcher, MAASOAuth
    HAS_MASS = True
except ImportError:
    pass


def __virtual__():
    '''
    Only load this module if maas-client
    is installed on this minion.
    '''
    if HAS_MASS:
        return 'maas'
    return False

__opts__ = {}


def _auth(**connection_args):
    '''
    Set up maas credentials

    Only intended to be used within maas-enabled modules
    '''
   
    prefix = "maas."

    # look in connection_args first, then default to config file
    def get(key, default=None):
        return connection_args.get('connection_' + key,
            __salt__['config.get'](prefix + key, default))

    api_token = get('token')
    api_url = get('url', 'https://localhost/')

    auth = MAASOAuth(*api_token.split(":"))
    dispatcher = MAASDispatcher()
    client = MAASClient(auth, dispatcher, api_url)

    return client


def cluster_get(cluster_name=None, **connection_args):
    '''
    Return a specific cluster

    CLI Example:

    .. code-block:: bash

        salt '*' maas.cluster_get cluster
    '''
    maas = _auth(**connection_args)

    object_list = maas.get(u"nodegroups/", "list").read()

    for cluster in object_list:
        if cluster.get('name') == cluster_name:
            return {cluster.get('name'): cluster}
    return {'Error': 'Could not find specified cluster'}


def cluster_list(**connection_args):
    '''
    Return a list of MAAS clusters

    CLI Example:

    .. code-block:: bash

        salt '*' maas.cluster_list
    '''
    maas = _auth(**connection_args)
    ret = {}

    object_list = maas.get(u"nodegroups/", "list").read()

    for cluster in object_list:
        ret[cluster.get('name')] = cluster
    return ret


def cluster_create(cluster_name=None, **connection_args):
    '''
    Create MAAS cluster

    CLI Examples:

    .. code-block:: bash

        salt '*' maas.cluster_create cluster
    '''
    maas = auth(**connection_args)
    if project_name:
        project = _get_project(maas, project_name)
    else:
        project = _get_project_by_id(maas, project_id)
    if not project:
        return {'Error': 'Unable to resolve project'}
    create = True
    for cluster in maas.getprojectclusters(project.get('id')):
        if cluster.get('url') == cluster_url:
            create = False
    if create:  
        maas.addprojectcluster(project['id'], cluster_url)
    return cluster_get(cluster_url, project_id=project['id'])


def cluster_delete(cluster_name=None, **connection_args):
    '''
    Delete MAAS cluster

    CLI Examples:

    .. code-block:: bash

        salt '*' maas.cluster_delete 'https://cluster.url/' project_id=300
    '''
    maas = _auth(**connection_args)
    project = _get_project(maas, project_name)

    for cluster in maas.getprojectclusters(project.get('id')):
        if cluster.get('url') == cluster_url:
            return maas.deleteprojectcluster(project['id'], cluster['id'])
    return {'Error': 'Could not find cluster'}
