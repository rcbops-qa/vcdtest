#!/usr/bin/env python

import argh
import xmltodict
from ampq import AmqpConnection
from vcd import VCloud


def resolve_entity(data):
    links = data['Entity']['Link']
    if isinstance(links, list):
        for link in links:
            resolve(link['@href'], link['@type'])
    else:
        resolve(links['@href'], links['@type'])


def resolve(url, name):
    vcloud = VCloud()
    print name
    response = vcloud.req(url)
    data = xmltodict.parse(response.text)
    # print response.text
    if "Entity" in data:
        resolve_entity(data)
    else:
        print response.text


def callback(channel, method, header, body):
    data = xmltodict.parse(body)
    print "{0}:".format(data['vmext:Notification']['@type'])
    print body
    resolver = data['vmext:Notification']['vmext:Link']['@href']
    for entity in data['vmext:Notification']['vmext:EntityLink']:
        name = entity['@type']
        id = entity['@id']
        resolve(resolver+id, name)


def _drain(*args):
    print "message received"


def drain(host, username, password, virtual_host, queue):
    connection = AmqpConnection(host=host, username=username,
                                password=password, virtual_host=virtual_host)
    connection.receive(_drain, queue=queue)


def crawl(host, username, password, virtual_host, queue):
    connection = AmqpConnection(host=host, username=username,
                                password=password, virtual_host=virtual_host)
    connection.receive(callback, queue=queue)

argh.dispatch_commands([crawl, drain])
