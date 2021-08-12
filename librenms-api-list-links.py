#!/usr/bin/env python3

import dotenv
import pandas as pd
import requests
import sys

from absl import app
from absl import flags
from absl import logging
from rich.console import Console
from rich.progress import track

__version__ = '1'
FLAGS = flags.FLAGS
console = Console()

flags.DEFINE_boolean('debug', False, 'produces debugging output')


def load_env():
    """ Load env vars from dotenv file

        Returns ordered dict name config with
        dotenv key value pairs
    """

    try:
        logging.debug('DEBUG: START: %s' % load_env.__name__)
        config = dotenv.dotenv_values(".env")
        if (config["LIBRENMS_TOKEN"] is not None and
                config["LIBRENMS_URL"] is not None):
            return config

    except Exception as e:
        logging.error('%s' % (repr(e)))
        raise


def librenms_devices(token, url):
    """ Get LibreNMS devices list via REST API

        Returns dataframe with two columns
        hostname and device_id
    """

    try:
        headers = {'X-Auth-Token': token}
        devices_url = (url + '/api/v0/devices/')
        response = requests.get(devices_url, headers=headers)
        resp = response.json()
        logging.debug('DEBUG resp type: %s' % type(resp))
        logging.debug('DEBUG resp keys: %s' % resp.keys())
        logging.debug('DEBUG resp["status"]: %s' % resp["status"])
        logging.debug('DEBUG resp["count"]: %s' % resp["count"])
        if (resp['status'] == "ok"):
            console.print('Success - LibreNMS Devices count: %s' %
                          resp["count"],
                          style='bright_green')
            df = pd.json_normalize(resp['devices'])
            df = df.sort_values('hostname')
            df = df[['hostname',
                     'device_id']]
            df = df.reset_index(drop=True)
            logging.debug('DEBUG: df_devices size: %s' % len(df.index))
            logging.debug('DEBUG: df_devices keys:\n%s' % df.keys())
            logging.debug('DEBUG: df_devices:\n%s' % df.head(3))
            return df
        else:
            console.print('Failed to get LibreNMS Devices list via API',
                          style='bold red')
            sys.exit(1)

    except Exception as e:
        logging.error('%s' % (repr(e)))
        raise


def librenms_links(token, url):
    """ Get LibreNMS links list via REST API

        Returns dataframe with five columns
    """

    try:
        headers = {'X-Auth-Token': token}
        links_url = (url + '/api/v0/resources/links')
        response = requests.get(links_url, headers=headers)
        resp = response.json()
        logging.debug('DEBUG resp type: %s' % type(resp))
        logging.debug('DEBUG resp keys: %s' % resp.keys())
        logging.debug('DEBUG resp["status"]: %s' % resp["status"])
        logging.debug('DEBUG resp["count"]: %s' % resp["count"])
        if (resp['status'] == "ok"):
            console.print('Success - LibreNMS Links count: %s' %
                          resp["count"],
                          style='bright_green')
            df = pd.json_normalize(resp['links'])
            df = df[['local_device_id',
                     'remote_device_id',
                     'local_port_id',
                     'remote_port_id',
                     'protocol']]
            logging.debug('DEBUG: df_links size: %s' % len(df.index))
            logging.debug('DEBUG: df_links keys:\n%s' % df.keys())
            logging.debug('DEBUG: df_links:\n%s' % df.head(3))
            return df

        else:
            console.print('Failed to get LibreNMS Links list via API',
                          style='bold red')
            sys.exit(1)

    except Exception as e:
        logging.error('%s' % (repr(e)))
        raise


def librenms_ports(token, url):
    """ Get LibreNMS ports list via REST API

        Returns dataframe with three columns
        device_id, port_id, ifName
    """

    try:
        headers = {'X-Auth-Token': token}
        ports_url = (url + '/api/v0/ports')
        COLUMNS = 'device_id,port_id,ifName'
        params = {'columns': ('%s' % COLUMNS)}
        response = requests.get(ports_url, headers=headers, params=params)
        resp = response.json()
        logging.debug('DEBUG resp type: %s' % type(resp))
        logging.debug('DEBUG resp keys: %s' % resp.keys())
        logging.debug('DEBUG resp["status"]: %s' % resp["status"])
        logging.debug('DEBUG resp["count"]: %s' % resp["count"])
        if (resp['status'] == "ok"):
            console.print('Success - LibreNMS Ports count: %s' %
                          resp["count"],
                          style='bright_green')
            df = pd.json_normalize(resp['ports'])
            df = df[['device_id',
                     'port_id',
                     'ifName']]
            logging.debug('DEBUG: df_ports size: %s' % len(df.index))
            logging.debug('DEBUG: df_ports keys:\n%s' % df.keys())
            logging.debug('DEBUG: df_ports:\n%s' % df.head(3))
            return df

        else:
            console.print('Failed to get LibreNMS Ports list via API',
                          style='bold red')
            sys.exit(1)

    except Exception as e:
        logging.error('%s' % (repr(e)))
        raise


def inner_merge(left_df, right_df, on_column):
    """ Inner merge two dataframes by specific
        column

        Returns dataframe with merged data
    """

    try:
        logging.debug('DEBUG: left_df keys:\n%s' % left_df.keys())
        logging.debug('DEBUG: right_df keys:\n%s' % right_df.keys())
        df_merged = pd.merge(left_df,
                             right_df,
                             how='inner',
                             on=on_column)
        logging.debug('DEBUG: df_merged size: %s' %
                      len(df_merged.index))
        logging.debug('DEBUG: df_merged keys:\n%s' % df_merged.keys())
        logging.debug('DEBUG: df_merged:\n%s' % df_merged.head(3))
        return df_merged

    except Exception as e:
        logging.error('%s' % (repr(e)))
        raise


def left_merge(left_df, right_df, on_column):
    """ Left merge two dataframes by specific
        column

        Returns dataframe with left merged data
    """

    try:
        logging.debug('DEBUG: left_df keys:\n%s' % left_df.keys())
        logging.debug('DEBUG: right_df keys:\n%s' % right_df.keys())
        df_lefted = pd.merge(left_df,
                             right_df,
                             how='left',
                             on=on_column)
        logging.debug('DEBUG: df_lefted size: %s' %
                      len(df_lefted.index))
        logging.debug('DEBUG: df_lefted keys:\n%s' % df_lefted.keys())
        logging.debug('DEBUG: df_lefted:\n%s' % df_lefted.head(3))
        return df_lefted

    except Exception as e:
        logging.error('%s' % (repr(e)))
        raise


def main(argv):
    try:
        if FLAGS.debug:
            logging.set_verbosity(logging.DEBUG)
            logging.debug('non-flag arguments: %s' % argv)

        logging.debug('DEBUG: START: %s' % main.__name__)
        console.rule('[bold red]LibreNMS API list links')
        # load dotenv variables
        config = load_env()
        LIBRENMS_TOKEN = config['LIBRENMS_TOKEN']
        LIBRENMS_URL = config['LIBRENMS_URL']
        console.print('Loaded LibreNMS URL: %s' % LIBRENMS_URL)
        # get lists via api
        df_devices = librenms_devices(LIBRENMS_TOKEN, LIBRENMS_URL)
        df_links = librenms_links(LIBRENMS_TOKEN, LIBRENMS_URL)
        df_ports = librenms_ports(LIBRENMS_TOKEN, LIBRENMS_URL)
        # merge hostnames into ports by device_id
        df_full_ports = inner_merge(df_ports, df_devices, 'device_id')
        # create new df's
        df_named_links = df_links.copy()
        df_local_ports = df_full_ports.copy()
        df_remote_ports = df_full_ports.copy()
        # rename columns to match local ones
        df_local_ports.columns = ['local_device_id',
                                  'local_port_id',
                                  'local_ifName',
                                  'local_hostname']
        df_remote_ports.columns = ['remote_device_id',
                                   'remote_port_id',
                                   'remote_ifName',
                                   'remote_hostname']
        # merge local ports into named links
        df_named_links = left_merge(df_named_links,
                                    df_local_ports,
                                    'local_port_id')
        # merge local ports into named links
        df_named_links = left_merge(df_named_links,
                                    df_remote_ports,
                                    'remote_port_id')
        # keep only named colums
        df_named_links = df_named_links[['local_hostname',
                                         'local_ifName',
                                         'remote_hostname',
                                         'remote_ifName',
                                         'protocol']]
        # print result df into std out
        console.print(df_named_links.to_csv())
        sys.exit(0)

    except Exception as e:
        logging.error('%s %s' % (repr(e), FLAGS))
        raise


if __name__ == '__main__':
    app.run(main)
