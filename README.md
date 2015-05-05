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

##Examples
### Manage marathon apps
#### List apps
* list of all running apps: 

  ```
  macli -M http://marathon:8080 app list
  ```
* or you can save a bit of unnecessary work, set marathon server into environment variable:
  
  ```
  export MARATHON=http://marathon:8080
  macli app list
  ```
  ...it does the same as above

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
  
  useful for testing app with no impact but using the same json file.

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
  
* force apply even if a previous deployment is in progress

  ```
  macli app create /myapp myapp.json -f
  ```



/todo - under construction/
