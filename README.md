# What is it?
This is just a quick and dirty example of how the deployment of a go web application could look like with debian packages. For this purpose a hello world martini application is build and packaged with the help of invoke and fpm.

# Dependencies
* [invoke](https://github.com/pyinvoke/invoke)
* [fpm](https://github.com/jordansissel/fpm/wiki)
* and [golang](http://golang.org/)

# Building the deb file
1) `cd hello_martini`  
2) `invoke build_deb --config configs/go.dajool.com.yaml`  
invoke then creates the needed folder structure and generates all the configs and post-/pre-install scripts we want in this demo. You might want to change the `domain_name` if you actually want to install this package. Also take a look at the folder structure first.

# Installation
Since this package comes with a nginx config and launches the go-binary with supervisor (which could easily be replaced by a upstart or systemd script), everything is up and running after a simple `dpkg -i go-test-dajool_0.20140312~213054_all.deb` – or, if you have your own debian repository, `apt-get install go-test-dajool`.

You can easily adopt this to other packaging systems. fpm also supports e.g. RPM.
