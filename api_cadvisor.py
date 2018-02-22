#!/usr/bin/python

import requests
import json
import dateutil.parser
import pprint


class CadvisorContainer:
    data = {}
    mesos_id = ""
    cpu_usage = 0.0

    def req_data(self, url):
        r = requests.get(url)
        #todo if r.status_code

        self.data = json.loads(r.text)
        if 'aliases' in self.data:
            #self.mesos_id = self.data['aliases'][0]
            self.mesos_id = self.data['aliases'][1]
            #todo if not substring mesos in mesos_id

    def get_subcontainers(self):
        return self.data['subcontainers']

    def get_memory_usage(self):
        return self.data['stats'][-1]['memory']['usage']

    def get_cpu_usage(self):
        ## somethin wrong :) not work properly

        a = self.data['stats'][1]['cpu']['usage']['total']
        b = self.data['stats'][0]['cpu']['usage']['total']
        c = float(t0 - t1)

        tdelta = dateutil.parser.parse(
            self.data['stats'][1]['timestamp']) - dateutil.parser.parse(
                self.data['stats'][0]['timestamp'])
        interval = tdelta.seconds * 1000000000.0 + tdelta.microseconds * 1000.0

        u = float(a - b) / float(interval)

        return (u)


#  def __init__(self, url):
#    self.req_data(url)


class Cadvisor:
    url = ""
    machine = {}
    host = CadvisorContainer()

    def req_machine(self):
        r = requests.get(self.url + "machine/")
        #todo if r.status_code
        self.machine = json.loads(r.text)

    def req_host(self):
        self.host.req_data(self.url + 'containers/docker/')

    def get_containers(self):
        ret = {}
        c_ids = self.host.get_subcontainers()
        for c_id in c_ids:
            c = CadvisorContainer()
            c.req_data(self.url + "containers" + c_id['name'])
            ret[c.mesos_id] = c
        return (ret)

    def get_num_cores(self):
        return self.machine['num_cores']

    def __init__(self, addr, port):
        self.url = "http://" + addr + ":" + str(port) + "/api/v1.2/"
        self.req_machine()
        self.req_host()
