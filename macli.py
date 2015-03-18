#!/usr/bin/python

from os import environ
from marathon import MarathonClient, MarathonApp
from marathon.exceptions import *
from api_marathon import Marathon
#from api_cadvisor import Cadvisor
#from hurry.filesize import size,alternative
import argparse
import json
import pprint
from termcolor import colored


class mPrinter(pprint.PrettyPrinter):
 def format(self, object, context, maxlevels, level):
   if isinstance(object, unicode):
     return (object.encode('utf8'), True, False)
   return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Marathon command line tool')
  parser.add_argument('-M', '--server', metavar="url", help='marathon server url address')
  parser.add_argument('-nc', '--nocolor', action='store_true', help='do not use colors')
  subparsers = parser.add_subparsers(dest='command', title='command')

  parser_app = subparsers.add_parser('app', help='manage marathon apps')
  subparsers_app = parser_app.add_subparsers(dest='app_command', title='app_command')
  parser_app_list = subparsers_app.add_parser('list', help='list running apps')
  parser_app_list.add_argument('-m', action='store_true', help='include mesos task ids')
  parser_app_list.add_argument('-H', action='store_true', help='include mesos-slave hosts')
  parser_app_list.add_argument('-p', action='store_true', help='include host ports')
  parser_app_list.add_argument('-i', action='store_true', help='include image name')
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
  parser_app_get.add_argument('-j', action='store_true', help='export json format of app config')

  parser_host= subparsers.add_parser('host', help='manage mesos-slave hosts')
  subparsers_host = parser_host.add_subparsers(dest='host_command', title='host_command')
  parser_host_list = subparsers_host.add_parser('list', help='list mesos-slave hosts')
  parser_host_list.add_argument('-a', action='store_true', help='include running marathon apps')
  parser_host_list.add_argument('-m', action='store_true', help='include mesos task ids (=container names)')
#  parser_host_list.add_argument('-c', action='store_true', help='include cadvisor system stats')
  parser_host_list.add_argument('-A', action='store_true', help='show all info')

  parser_marathon = subparsers.add_parser('marathon', help='manage marathon server')
  subparsers_marathon = parser_marathon.add_subparsers(dest='marathon_command', title='marathon_command')
  parser_marathon_ping= subparsers_marathon.add_parser('ping', help='ping the marathon server')
  parser_marathon_dump = subparsers_marathon.add_parser('dump', help='backup config of all apps to one json')
#  parser_import = subparsers.add_parser('import', help='recovery apps from backup json (dump)')

#  parser_ps= subparsers.add_parser('ps', help='list marathon apps and tasks; same as: app list -H -p -m')

  args=parser.parse_args()

  #print (args)

  if not args.server:
    if not 'MARATHON' in environ:
      print ("error: marathon server not configured.\nUse -M option or MARATHON environment variable.")
      exit (1)
    else:
      args.server = environ['MARATHON']

  m = Marathon(args.server)

#  if args.command == "ps":
#    (args.command, args.app_command, args.m, args.H, args.p, args.i, args.A) = ('app', 'list', True, True, True, False, False)


  if args.command == "app":
    if args.app_command == "list" and not (args.H or args.p or args.m or args.A):
      try:
        apps=m.get_apps_dict()
      except (InternalServerError, InvalidChoiceError, MarathonError, MarathonHttpError, NotFoundError) as e:
        print (e)
        exit (1)

      for app in apps:
        out=app
        if args.i:
          out += " [" + apps[app]['container']['docker']['image'] + "]"
        print (out)

    elif args.app_command == "list":
      if args.A:
        (args.H, args.p, args.m, args.i) = (True, True, True, True)
      apps=m.get_apps_dict()
      for app in apps:
        if args.nocolor:
          out=app
        else:
          out = colored( app, 'green')
        if args.i:
          out += " [" + apps[app]['container']['docker']['image'] + "]"
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
      if args.j:
        json=m.get_app_json(args.id)
        print(json)
      elif args.d:
        app=m.get_app_dict(args.id)
        mPrinter().pprint(app)
      else:
        app=m.get_app_dict(args.id)

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
      x=m.create_app_from_json(json_data)
      mPrinter().pprint(x)

    elif args.app_command == "update":
      json_file = open(args.json_file)
      json_str = json_file.read()
      json_data = json.loads(json_str)
      if args.i:
        json_data['id']=args.i
      if args.I:
        json_data['container']['docker']['image']=args.I
      x=m.update_app_from_json(json_data, args.f)
      mPrinter().pprint(x)

    elif args.app_command == "delete":
      x=m.delete_app(args.id, args.f)
      mPrinter().pprint(x)

  elif args.command == "host":
    if args.host_command == "list":
      if args.A:
        (args.a, args.m) = (True,True)
     
      try:
        hosts = m.get_hosts_dict()
      except (InternalServerError, InvalidChoiceError, MarathonError, MarathonHttpError, NotFoundError) as e:
        print (e)
        exit (1)
      
      for host in hosts:
        if args.nocolor or not (args.a or args.m):
          strout = host
        else:
          strout = colored( host, 'green')
        print strout

        if args.a or args.m:
          for task in hosts[host]:
            strout=" "
            if args.a:
              strout += (" " + task.app_id)
            if args.m:
              strout += (" " + task.id)
#            if args.c:
            print strout

  elif args.command == "marathon":
    if args.marathon_command=="ping":
      print( m.ping() )
    elif args.marathon_command=="dump":
      print m.get_apps_json_config()

