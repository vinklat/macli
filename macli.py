#!/usr/bin/python

from os import environ
from marathon import MarathonClient, MarathonApp
import argparse
import json
import pprint


def app_get(id):
  c = MarathonClient(environ['MARATHON'])
  a=c.get_app(id)
  x=a.to_json()
  return(json.loads(x))

def apps_get():
  apps=[]
  c = MarathonClient(environ['MARATHON'])
  for app in c.list_apps():
    apps.append(app.id)
  return apps

def apps_detailed_get():
  apps={}
  c = MarathonClient(environ['MARATHON'])
  for app in c.list_apps():
    apps[app.id]=app_get(app.id)
  return apps
  
def hosts_get():
  hosts={}
  c = MarathonClient(environ['MARATHON'])
  for app in c.list_apps():
    for task in c.get_app(app.id).tasks:
      host = task.host
      if not host in hosts:
        hosts[host]=[]
      hosts[host].append(app)
  return hosts

def app_create( json_data ):
  c = MarathonClient(environ['MARATHON'])
  a = MarathonApp.from_json(json_data)
  return c.create_app(a.id, a) 

def app_update( json_data, force ):
  c = MarathonClient(environ['MARATHON'])
  a = MarathonApp.from_json(json_data)
  return c.update_app(a.id, a, force)

def app_delete (id, force):
  c = MarathonClient(environ['MARATHON'])
  return c.delete_app(id, force)


def ping():
  c = MarathonClient(environ['MARATHON'])
  return (c.ping())



if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Marathon command line tool')
  subparsers = parser.add_subparsers(dest='command', title='command')

  parser_ping= subparsers.add_parser('ping', help='ping the marathon server')

  parser_app = subparsers.add_parser('app', help='manage marathon apps')
  subparsers_app = parser_app.add_subparsers(dest='app_command', title='app_command')
  parser_app_list = subparsers_app.add_parser('list', help='list running apps')
  parser_app_list.add_argument('-m', action='store_true', help='include mesos task ids')
  parser_app_list.add_argument('-H', action='store_true', help='include mesos-slave hosts')
  parser_app_list.add_argument('-p', action='store_true', help='include host ports')
  parser_app_list.add_argument('-A', action='store_true', help='show all info')

  parser_app_create = subparsers_app.add_parser('create', help='create and start an app')
  parser_app_create.add_argument('json_file', help='json format app config')
  parser_app_create.add_argument('-i', metavar='id', help='force app id, walk around id in json config')
  parser_app_create.add_argument('-I', metavar="image", help='force image, walk around image in json config')

  parser_app_update = subparsers_app.add_parser('update', help='update an app')
  parser_app_update.add_argument('json_file', help='json format app config')
  parser_app_update.add_argument('-i', metavar='id', help='force app id, walk around id in json config')
  parser_app_update.add_argument('-I', metavar="image", help='force image, walk around image in json config')
  parser_app_update.add_argument('-f', action='store_true', help='force apply even if a deployment is in progress')

  parser_app_delete = subparsers_app.add_parser('delete', help='stop and destroy an app')
  parser_app_delete.add_argument('id', help='marathon app id')
  parser_app_delete.add_argument('-f', action='store_true', help='force apply even if a deployment is in progress')

  parser_app_get = subparsers_app.add_parser('get', help='get and view a single app')
  parser_app_get.add_argument('id', help='marathon app id')
  parser_app_get.add_argument('-d', action='store_true', help='show detailed info')

  parser_hosts= subparsers.add_parser('hosts', help='list mesos-slave hosts')
  parser_hosts.add_argument('-a', action='store_true', help='include marathon app ids')
#  parser_hosts.add_argument('-m', action='store_true', help='include marathon task ids')

  parser_ps= subparsers.add_parser('ps', help='list marathon apps and tasks; same as: app list -H -p -m')

  args=parser.parse_args()
#  print (args)

  if args.command == "ps":
    (args.command, args.app_command, args.m, args.H, args.p, args.A) = ('app', 'list', True, True, True, False)

  if args.command == "ping":
    print( ping() )

  elif args.command == "app":
    if args.app_command == "list" and not (args.H or args.p or args.m or args.A):
      apps=apps_get()
      for app in apps:
        print (app)

    elif args.app_command == "list":
      if args.A:
        (args.H, args.p, args.m) = (True, True, True)
      apps=apps_detailed_get()
      for app in apps:
        out=app
        for task in apps[app]['tasks']:
          out += "\n "
          if args.H:
            out += " " + task['host']
          if args.p:
            if len(task['ports']) == 1:
              out += ":" + str(task['ports'][0])
            else:
              out += ":["
              for p in task['ports'][:-1]:
                out+=str(p) + ","
              out += str(task['ports'][-1]) + "]"
          if args.m:
            out += " " + task['id']
        print (out)

    elif args.app_command == "get":
      app=app_get(args.id)
      if args.d:
        pprint.pprint(app)
      else:
        print ("Marathon id: %s" % app['id'])
        print ("Image: %s" % app['container']['docker']['image'])
        print ("Instances: %d" % app['instances'])
        print ("Cpus: %.1f" % app['cpus'])
        print ("Memory: %d" % app['mem'])
        print ("Disk: %.1f" % app['disk'])
        out= str(app['tasksRunning']) + " running mesos tasks:"
        for task in app['tasks']:
            out += "\n "
            out += " " + task['host']
            if len(task['ports']) == 1:
              out += ":" + str(task['ports'][0])
            else:
              out += ":["
              for p in task['ports'][:-1]:
                out+=str(p) + ","
              out += str(task['ports'][-1]) + "]"
            out += " " + task['id']
        print (out)

    elif args.app_command == "create":
      json_file = open(args.json_file)
      json_str = json_file.read()
      json_data = json.loads(json_str)
      if args.i:
        json_data['id']=args.i
      if args.I:
        json_data['container']['docker']['image']=args.I
      pprint.pprint (json_data)
      x=app_create(json_data)
      pprint.pprint(x)

    elif args.app_command == "update":
      json_file = open(args.json_file)
      json_str = json_file.read()
      json_data = json.loads(json_str)
      if args.i:
        json_data['id']=args.i
      if args.I:
        json_data['container']['docker']['image']=args.I
      x=app_update(json_data, args.f)
      pprint.pprint(x)

    elif args.app_command == "delete":
      x=app_delete(args.id, args.f)
      pprint.pprint(x)

  elif args.command == "hosts":
    hosts = hosts_get()
    for host in hosts:
      print (host)
      if args.a == True:
        for app in hosts[host]:
           print ("  " + app.id)
      ## todo args.m
