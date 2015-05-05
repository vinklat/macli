# macli
command line tool for marathon

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
  ...do the same as above

* detailed list:

  ```
  macli app list -A
  ``` 
  then show mesos tasks (instances), hosts where tasks runs, ports, images. You can select each separately using ```-m -H -p``` or ```-i``` parameters.
  
#### Get app
* show info about one app (given cpus, memory, instances, etc.):

  ```
  macli app get /myapp
  ```

* more detailed:

  ```
  macli app get /myapp -d
  ```
  
* output json format of app config:

  ```
  macli app get /myapp -j
  ```

/todo - under construction/
