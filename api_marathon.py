#!/usr/bin/python

from marathon import MarathonClient, MarathonApp
import json

class Marathon (MarathonClient):
  def get_app_json(self,id):
    app=MarathonClient.get_app(self,id)
    return (app.to_json())

  def get_app_dict(self,id):
    return(json.loads(self.get_app_json(id)))

  def get_apps_list(self):
    apps=[]
    for app in MarathonClient.list_apps(self):
      apps.append(app.id)
    return apps

  def get_apps_dict(self):
    apps={}
    for app in MarathonClient.list_apps(self):
      apps[app.id]=self.get_app_dict(app.id)
    return apps
 
  def get_hosts_dict(self):
    hosts={}
    for app in MarathonClient.list_apps(self):
      for task in MarathonClient.get_app(self,app.id).tasks:
        host = task.host
        if not host in hosts:
          hosts[host]=[]
        hosts[host].append(app)
    return hosts

  def create_app_from_json(self, json_data ):
    a = MarathonApp.from_json(json_data)
    return MarathonClient.create_app(self, a.id, a)

  def update_app_from_json( self, json_data, force ):
    a = MarathonApp.from_json(json_data)
    return MarathonClient.update_app(self, a.id, a, force)

  def __init__(self, addr):
    MarathonClient.__init__(self, addr)
