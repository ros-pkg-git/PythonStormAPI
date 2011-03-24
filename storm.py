#!/usr/bin/env python

# Software License Agreement (BSD License)
#
# Copyright (c) 2011, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import urllib2
import json
import pprint
import time

large_vm_preconfig = {u'template_description': u'Ubuntu 10.04 LTS (lucid) X86_64 Self-managed', u'domain': u'storm-test.willowgarage.com', u'config_id': u'6', u'create_date': u'2010-11-09 16:03:52', u'backup_enabled': u'0', u'zone': u'b3s4z1', u'subaccnt': u'33', u'ip': u'67.225.234.76', u'vlan': u'401', u'backup_size': u'0.00', u'uniq_id': u'6EP3C1', u'config_description': u'Storm 32GB', u'ip_count': 1, u'template': u'UBUNTULUCID', u'bandwidth_quota': 0, u'active': 1, u'accnt': u'194167', u'backup_quota': u'0', u'backup_plan': u'', u'manage_level': u'self'}


pending_status_identifiers = ['Building', 'Created', 'Booting']

class StormAPI:
    def __init__(self, username, password):
        self.password_mgr =  urllib2.HTTPPasswordMgrWithDefaultRealm()
        self.password_mgr.add_password(None, 'https://api.stormondemand.com', username, password)
        self.handler = urllib2.HTTPBasicAuthHandler(self.password_mgr)
        self.opener = urllib2.build_opener(self.handler)

        self.password = password # store for creation

    def storm_server_available(self, domain):
        url = 'https://api.stormondemand.com/Storm/Server/available'
        values = {'params': {"domain": domain}}
        jsondump = json.dumps(values)
        request = urllib2.Request(url, jsondump)
        response = self.opener.open(request)
        d = json.loads(response.read())
        if 'domain' in d:
            return d['domain']
        return None


    def account_paymethod_balance(self):
        url = 'https://api.stormondemand.com/Account/Paymethod/balance'
        request = urllib2.Request(url)
        response = self.opener.open(request)
        d = json.loads(response.read())
        if 'balance' in d:
            return d['balance']
        return None

    def account_limits_servers(self):
        url = 'https://api.stormondemand.com/Account/Limits/servers'
        request = urllib2.Request(url)
        response = self.opener.open(request)
        d = json.loads(response.read())
        if 'limit' in d:
            return int(d['limit'])
        return None


    def storm_server_create(self, backup_enabled, backup_plan, bandwidth_quota, config_id,
                            domain, image_id, ip_count, password, template):
        pass
    def storm_server_create_preconfig(self):
        url = 'https://api.stormondemand.com/Storm/Server/create'
        values = {'params':
                  {"backup_enabled": 0,
                   "bandwidth_quota": 0,
                   "config_id": 6,
                   "domain": 'hudson.storm.willowgarage.com',
                   "ip_count": 1,
                   "password": self.password,
                   "template": 'UBUNTULUCID',
                   }
                  }
        jsondump = json.dumps(values)
        request = urllib2.Request(url, jsondump)
        response = self.opener.open(request)
        d = json.loads(response.read())
        return d
        
    def storm_server_destroy(self, uniq_id): 
        url = 'https://api.stormondemand.com/Storm/Server/destroy'
        values = {'params': {"uniq_id": uniq_id}}
        jsondump = json.dumps(values)
        request = urllib2.Request(url, jsondump)
        response = self.opener.open(request)
        d = json.loads(response.read())
        if 'destroyed' in d:
            return d['destroyed']
        return None

    def storm_server_details(self, uniq_id): 
        url = 'https://api.stormondemand.com/Storm/Server/details'
        values = {'params': {"uniq_id": uniq_id}}
        jsondump = json.dumps(values)
        request = urllib2.Request(url, jsondump)
        response = self.opener.open(request)
        d = json.loads(response.read())
        return d

    def storm_server_status(self, uniq_id): 
        url = 'https://api.stormondemand.com/Storm/Server/status'
        values = {'params': {"uniq_id": uniq_id}}
        jsondump = json.dumps(values)
        request = urllib2.Request(url, jsondump)
        response = self.opener.open(request)
        d = json.loads(response.read())
        if 'status' in d:
            #print "status", d['status']
            return d['status']
        return None


    def storm_server_list(self):
        url = 'https://api.stormondemand.com/Storm/Server/list'
        request = urllib2.Request(url)
        response = self.opener.open(request)
        d = json.loads(response.read())
        if 'servers' in d:
            return d['servers']
        return None



    

    # Helper functions
    def wait_for_running(self, server_ids, timeout = 30):
        running_servers = []
        failed_servers = []
        unreached_servers = server_ids
        count = 0
        sleep_time = 1.0
        while unreached_servers:
            count = count + 1
            index = count % len(unreached_servers)
            s = unreached_servers[index]
            print "getting status of server", s
            status = self.storm_server_status(s)
            print status
            if status == 'Running':
                running_servers.append(s)
                unreached_servers.remove(s)
            elif status not in pending_status_identifiers:
                print "wait_for_running unknown status ", status
                unreached_servers.remove(s)
                failed_servers.append(s)
            time.sleep(sleep_time)
            if sleep_time * count > timeout:
                print "wait_for_running timed out after %.2f second"%timeout
                break
        return (running_servers, unreached_servers, failed_servers)
            
