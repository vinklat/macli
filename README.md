# macli
command line tool for marathon
##Install
It requires python + modules listed in requirements.txt file.   

```
git clone git@github.com:vinklat/macli.git
cd macli
pip install -r requirements.txt
make
```
then you get stand-alone binary ```macli``` in ```dist``` directory (using PyInstaller). Alternatively you can run original ```./macli.py```.

## Examples
### Test the connection
* ping the marathon server

  ```
  macli -M http://marathon:8080 marathon ping
  ```

* or you can save a bit of unnecessary future work, set marathon server url in the environment variable:
  
  ```
  export MARATHON=http://marathon:8080
  macli marathon ping
  ```
  ...it does the same as above

### Manage marathon apps
#### List apps
* list of all running apps: 

  ```
  macli app list
  ```
  
* detailed list:

  ```
  macli app list -A
  ``` 
  includes mesos tasks (instances), hosts where tasks runs, ports, image names. You can select each separately using ```-m -H -p``` or ```-i``` parameters.
  
#### Get an app
* show info about one app (given cpus priority, memory, instances, etc.):

  ```
  macli app get /myapp
  ```

* more detailed:

  ```
  macli app get /myapp -d
  ```
  
* output json format of an app resource:

  ```
  macli app get /myapp -j
  ```

#### Create an app

* create and start an app using application resource in json file

  ```
  macli app create myapp.json
  ```

* create and start an app, force another app id different than in the json file

  ```
  macli app create myapp.json -i /newapp
  ```
  
  useful for testing an app with no impact using existing json file.

* create and start an app, force image different than in the json file 

  ```
  macli app create myapp.json -I somenick/myapp2
  ```
  
  useful for one-shot :)
  

#### Update an app

* update an app using new application resource in json file

  ```
  macli app create /myapp myapp.json
  ```
  
  (```-i``` and ```-I``` parameters does the same as for create)
  
* force apply even if previous deployment is in progress

  ```
  macli app create /myapp myapp.json -f
  ```

#### Destroy an app

* destroy an application. All data about that application will be deleted.

  ```
  macli app delete /myapp
  ```
* force apply even if a deployment is in progress

  ```
  macli app delete /myapp -f
  ``` 

### Hosts overview

* list mesos-slave hosts

  ```
  macli host list
  ``` 
  
  Note: there are no empty hosts (with no tasks) in output.

* more detailed

  ```
  macli host list -A
  ``` 
  includes app ids and mesos task ids which runs on the host. You can select each separately using ```-m``` or ```-a``` parameters.

