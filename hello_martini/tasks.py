# -*- coding: utf-8 -*-

import os
import sys
import yaml
from invoke import run, task
from tasks_helper import *

GOPATH="/tmp/gopath/martini/"
os.environ['GOPATH'] = GOPATH

@task()
def clean(*args, **kwargs):
    """\
    Remove all build files, configs and packages."
    """
    run("rm -rf ./build")
    run("rm -rf ./build_configs")
    run("rm -f *.deb")
    run("go clean")


@task
def clean_deps():
    """\
    Remove dependencies.
    """
    global GOPATH
    run("rm -rf %s" % (GOPATH, ))


@task
def deps(*args, **kwargs):
    """\
    Fetch dependencies.
    """
    global GOPATH
    mkdirp(GOPATH)
    run("go get -d")


@task("deps", "clean", "prepare_paths", "config_nginx", "config_supervisor", "config_post_install", "config_pre_uninstall")
def build_deb(config):
    """\
    Prepares the build and generates the package.
    """
    # get values from config
    stream = file(config, 'r')
    config_values = yaml.load(stream)

    base_path = config_values['build-vars']['srv_path'] + config_values['build-vars']['domain']
    
    # build server.go and copy to …<domain>/lib/<package_name>/.
    run("go build")
    run("cp -r ./%s build/%s/lib/%s/." % \
        (config_values['build-vars']['binary_name'], base_path, config_values['name']))
    
    # copy configs
    run("cp ./build_configs/%s ./build/etc/nginx/sites-available/." % (config_values['build-vars']['domain'], ))
    run("cp ./build_configs/%s.conf ./build/etc/supervisor/conf.d/." % (config_values['build-vars']['domain'], ))
    
    # generate version number
    version = "%(major)s.%(minor)s" % \
        {
            'major': get_major_version(), 
            'minor': get_minor_version()
        }

    package('configs/go.dajool.com.yaml', {'version': version})
    
@task()
def prepare_paths(config):
    """\
    Prepare folder structure.
    """
    
    # get values from config
    stream = file(config, 'r')
    config_values = yaml.load(stream)
    base_path = config_values['build-vars']['srv_path'] + \
        config_values['build-vars']['domain']
    
    # make directories
    for folder in ['lib', 'htdocs', 'auth']:
        mkdirp("./build" + os.path.join(base_path, folder))
    mkdirp("./build/etc/nginx/sites-available")
    mkdirp("./build/etc/supervisor/conf.d")
    mkdirp("./build/%s/lib/%s" % (base_path, config_values['name']))
    mkdirp("./build_configs")


@task
def config_pre_uninstall(config):
    """\
    Generate pre uninstall script from template.
    """
    generate_config("pre_uninstall",
                    config,
                    os.path.join("build_configs", "pre_uninstall.sh"))


@task
def config_post_install(config):
    """\
    Generate post install script from template.
    """
    generate_config("post_install",
                    config,
                    os.path.join("build_configs", "post_install.sh"))


@task
def config_nginx(config=''):
    """\
    Generate nginx config from template.
    """
    stream = file(config, 'r')
    config_values = yaml.load(stream)
    generate_config("nginx_config",
                    config,
                    os.path.join("build_configs", config_values['build-vars']['domain']))


@task
def config_supervisor(config=''):
    """\
    Gernate supervisor config from template.
    """
    stream = file(config, 'r')
    config_values = yaml.load(stream)
    generate_config("supervisor_config",
                    config,
                    os.path.join("build_configs",
                                 config_values['build-vars']['domain'] + ".conf"))
