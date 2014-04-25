# -*- coding: utf-8 -*-

import sys
import os
from invoke import run, task
from tasks_helper import *

from jinja2 import Template, Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

from shutil import copy

GOPATH="/tmp/gopath/martini/"
os.environ['GOPATH'] = GOPATH

@task()
def clean():
    run("rm -f post_install.sh pre_uninstall.sh")
    run("rm -rf ./build")
    run("rm -f *.deb")
    run("go clean")


@task
def clean_deps():
    global GOPATH
    run("rm -rf %s" % (GOPATH, ))


@task
def deps(*args, **kwargs):
    global GOPATH
    mkdirp(GOPATH)
    run("go get -d")


@task("deps", "config_nginx", "config_supervisor", "config_post_install", "config_pre_uninstall")
def build_deb(config):
    run("go build")
    parser = _get_ini_parser(config)
    config_values = parser.as_dict()['general']
    base_path = Template("{{ srv_path }}{{ domain }}").render(config_values)
    for folder in ['lib', 'htdocs', 'auth']:
        mkdirp("./build" + os.path.join(base_path, folder))
    mkdirp("./build/etc/nginx/sites-available")
    mkdirp("./build/etc/supervisor/conf.d")
    mkdirp("./build/%s/lib/%s" % (base_path, config_values['package_name']))
    run("cp -r ./%s build/%s/lib/%s/." % \
        (config_values['binary_name'], base_path, config_values['package_name']))
    
    # copy configs
    run("mv %s ./build/etc/nginx/sites-available/." % (config_values['domain'], ))
    run("mv %s.conf ./build/etc/supervisor/conf.d/." % (config_values['domain'], ))
    
    # generate version number
    version = "%(major)s.%(minor)s" % \
        {
            'major': get_major_version(), 
            'minor': get_minor_version()
        }

    # build the deb package
    run("""\
        fpm -s dir \
            -t deb \
            -n %(package_name)s \
            -v %(version)s \
            -a all \
            --license "MIT" \
            -m "Jochen Breuer <breuer@dajool.com>" \
            --url "http://dajool.com" \
            --deb-user root \
            --deb-group root \
            --config-files /etc/nginx/sites-available/%(domain)s \
            --config-files /etc/supervisor/conf.d/%(domain)s.conf \
            --after-install ./post_install.sh \
            --before-remove ./pre_uninstall.sh \
            -d "supervisor" \
            -d "nginx" \
            -C ./build \
            etc srv""" % {
                'package_name': config_values['package_name'],
                'domain': config_values['domain'],
                'version': version, 
            })
    

@task(pre=["config_post_install", "config_nginx", "config_supervisor"])
def build_configs(config):
    pass


@task
def config_pre_uninstall(config):
    _generate_config("pre_uninstall", config, "pre_uninstall.sh")


@task
def config_post_install(config):
    _generate_config("post_install", config, "post_install.sh")


@task
def config_nginx(config=''):
    """\
    Generate nginx config.
    """
    parser = _get_ini_parser(config)
    config_values = parser.as_dict()['general']
    _generate_config("nginx_config", config, config_values['domain'])


@task
def config_supervisor(config=''):
    """\
    Gernate supervisor config.
    """
    parser = _get_ini_parser(config)
    config_values = parser.as_dict()['general']
    _generate_config("supervisor_config", config, config_values['domain'] + ".conf")


def _get_ini_parser(config=''):
    """\
    Get the ini parser for the given path.
    """
    parser = DictConfigParser()
    parser.read(config)
    return parser


def _generate_config(template_name, config, outputfile):
    """\
    Generates a config from a template and with values from the ini config.
    """
    parser = _get_ini_parser(config)
    script_template = env.get_template(template_name)
    with open(outputfile, "wb") as fh:
        fh.write(script_template.render(parser.as_dict()['general']))
