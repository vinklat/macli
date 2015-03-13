#!/usr/bin/python

from os import environ
from marathon import MarathonClient, MarathonApp
import argparse
import json
import pprint

def get_apps():
  apps=[]
  c = MarathonClient(environ['MARATHON'])
  for app in c.list_apps():
    apps.append(app.id)
  return apps

def get_apps_hosts():
  apps={} # key: appid ; value: [ hostnames ]
  hosts={} # key: hostname; value: [ appids ]

  c = MarathonClient(environ['MARATHON'])
  for app in c.list_apps():
    apps[app.id]=[]
    for task in c.get_app(app.id).tasks:
      apps[app.id].append(task.host)
      if not task.host in hosts:
        hosts[task.host]=[]
      hosts[task.host].append(app.id)

  return [ apps, hosts ]


def app_get(id):
  c = MarathonClient(environ['MARATHON'])
  a=c.get_app(id)
  x=a.to_json()
  return(json.loads(x))
  

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
  parser_app_list.add_argument('-t', action='store_true', help='include marathon tasks')
  parser_app_list.add_argument('-H', action='store_true', help='include mesos-slave hosts')

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

  parser_hosts= subparsers.add_parser('hosts', help='list mesos-slave hosts')
  parser_hosts.add_argument('-a', action='store_true', help='include marathon apps')
  parser_hosts.add_argument('-t', action='store_true', help='include marathon task ids')

  parser_ps= subparsers.add_parser('ps', help='list marathon tasks; same as: app list -H')

  args=parser.parse_args()
  print (args)

  if args.command == "ps":
    (args.command, args.app_command, args.H) = ('app', 'list', True)

  if args.command == "ping":
    print( ping() )

  elif args.command == "app":
    if args.app_command == "list" and args.H == False:
      apps=get_apps()
      for app in apps:
        print (app)

    elif args.app_command == "list" and args.H == True:
      [ apps, hosts ] =get_apps_hosts()
      for app in apps:
        print (app)
        for h in apps[app]:
          print ("  " + h)

    elif args.app_command == "get":
      app=app_get(args.id)
      pprint.pprint(app)

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
    [ apps, hosts ] =get_apps_hosts()
    for host in hosts:
      print (host)
      if args.a == True:
        for task in hosts[host]:
           print ("  " + task)

