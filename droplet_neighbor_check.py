#!/usr/bin/env python
################################################################################
## File: droplet_neighbor_check.py
## Author : Denny
##
## Description :
##    Make sure all my droplets not over-located in one hypervisor
##
##    Sample Usage: If more than 2 droplets in one hypervisor, report the potential risks
##      python droplet_neighbor_check.py \
##        --token 'd535bf5bf949b8c78XXXXXXXa' \
##        --max_droplets 2 \
##        --driver 'Digitalocean'
## --
## Created : <2018-02-21>
## Updated: Time-stamp: <2018-03-26 21:34:22>
################################################################################
import os, argparse, sys
import requests, json
import re

def get_droplets_from_do(digitalocean_token, name_pattern, max_droplets = 500):
    print("Calling DigitalOcean API to list all droplets")
    headers = {'Authorization': 'Bearer %s' % (digitalocean_token), \
               'Content-Type': 'application/json'}
    url = "https://api.digitalocean.com/v2/droplets?page=1&per_page=%d" % (max_droplets)
    r = requests.get(url, headers=headers)
    res = []
    if r.status_code != 200:
        print("Error: Fail to list droplets. errmsg: %s" % (r.text))
        sys.exit(1)
    
    # parse response message 
    l = []
    data = json.loads(r.text)
    for droplet in data["droplets"]:
        if droplet["name"].startswith(name_pattern):
            l.append((droplet["id"], droplet["name"]))
    return l

def check_droplets_neighbor(digitalocean_token, droplets, max_droplets):
    headers = {'Authorization': 'Bearer %s' % (digitalocean_token), \
               'Content-Type': 'application/json'}
    droplets_neighbor_cnt = max_droplets - 1
    res = []
    # https://developers.digitalocean.com/documentation/v2/#list-neighbors-for-a-droplet
    for (droplet_id, droplet_name) in droplets:
        print("Check droplet neighbors for %s" % (droplet_name))
        url = "https://api.digitalocean.com/v2/droplets/%s/neighbors" % (droplet_id)
        r = requests.get(url, headers=headers)
        res = []
        if r.status_code != 200:
            print("Error: Fail to list droplets. errmsg: %s" % (r.text))
            sys.exit(1)
        data = json.loads(r.text)
        l = data["droplets"]
        if len(l) >= droplets_neighbor_cnt:
            res.append((droplet_id, droplet_name))
    return res

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_droplets', required=False, type=int, \
                        default=2, help="The filepath of markdown file. ")
    parser.add_argument('--token', required=True, type=str, \
                        help="Use the token to list all droplet")
    parser.add_argument('--driver', required=True, type=str, default='Digitalocean', \
                        help="Which cloud provider")
    parser.add_argument('--hostname_pattern', required=False, type=str, default='', \
                        help="Filter droplets by hostname pattern. If not given, all droplets will be checked")

    l = parser.parse_args()
    digitalocean_token = l.token
    droplet_name_pattern = l.hostname_pattern
    droplets_problematic = []
    try:
        droplets = get_droplets_from_do(digitalocean_token, droplet_name_pattern)
        droplets_problematic = check_droplets_neighbor(digitalocean_token, droplets, l.max_droplets)
    except Exception as e:
        print("Unexpected error:%s, %s" % (sys.exc_info()[0], e))
        sys.exit(1)

    if len(droplets_problematic) == 0:
        print("OK: no over-allocation issues have been found")
    else:
        print("ERROR: below droplets are deployed in hypervisor which has more than %d" % (l.max_droplets))
        for (droplet_id, name) in droplets_problematic:
            print("| %s  |  %s  |" %  (str(droplet_id.ljust(10, ' '), name.ljust(25, ' '))))
        sys.exit(1)
## File: droplet_neighbor_check.py ends
