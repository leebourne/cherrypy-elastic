#!/usr/bin/python
'''
Created on Apr 16, 2014

@author: Lee Khan-Bourne

Template for calling Elasticsearch from within a CherryPy website
Modify functions 'objects', 'search' and 'setup_routes' to suit your needs
    
'''

import sys
sys.stdout = sys.stderr

import os, os.path
import string
import json
import atexit
import threading
import cherrypy

import pystache
from pystache import Renderer
renderer = Renderer()

import elasticsearch
from elasticsearch import Elasticsearch
es = Elasticsearch()

# Set up some globals (these should be put in a config file)
rootDir = os.path.dirname(os.path.realpath(__file__))
esIndex = 'myIndex'

cherrypy.config.update({'environment': 'embedded'})

if cherrypy.__version__.startswith('3.0') and cherrypy.engine.state == 0:
	cherrypy.engine.start(blocking=False)
	atexit.register(cherrypy.engine.stop)

def api():
	return file(rootDir + '/static/index.html')

def http_error_page(status, message, traceback, version):
	'''
	Serve up a standard http error screen with a customised message embedded
	'''
	fileHandle = open(rootDir + '/templates/http_error.html' ,'r')
	contents = renderer.render(fileHandle.read(), {'responseCode': status, 'responseMessage': message})

	return contents

def objects(objectType,objectId,*args,**kw):
	'''
	Search for and return an Elasticsearch document by id
	'''
	debug = application.config['global']['debug.on']
	if debug:
		cherrypy.log(json.dumps(queryObj))	

	res = es.get(index=esIndex, doc_type=objectType, id=objectId)
	if res['found'] == True:
		return json.dumps(res['source'])
	else:
		raise cherrypy.HTTPError(404, message="The %s you have requested does not exist" % objectType)
	

def unicode_string(param):
	return param.replace("%u","\u").decode('unicode-escape')
		
def search(objectType,*args,**kw):
	'''
	Search for and return one or more documents based on a free text string passed in as an argument called 'text'
	'''
	debug = application.config['global']['debug.on']
	if 'text' not in kw:  	
		raise cherrypy.HTTPError(404, message="Please provide some text to search by")

	# Perform search on free text
	cherrypy.log('Searching by programme name - for related objects')
	
	queryObj = {
		"query": {
			"match" : {
				"_all" : unicode_string(kw['text'])
			}
		}
	}		
	if debug:
		cherrypy.log(json.dumps(queryObj))
	
	res = es.search(index=esIndex, body=queryObj)
	
	if res['hits']['total'] > 0:
		return json.dumps(res['hits']['hits'])
	else:
		raise cherrypy.HTTPError(404, message="Could not find any documents matching your criteria")

dispatcher = None

def setup_routes():
	'''
	Set up a number of regexp style url patterns that this application can handle
	'''

	d = cherrypy.dispatch.RoutesDispatcher()
	d.connect('objects', '/{objectType:(type_one|type_two|type_three)}s/{objectId:([0-9]+)}', objects)
	d.connect('search', '/search', search)
	d.connect('root', '/', api)
	dispatcher = d
	return dispatcher

cherrypy.config.update({
	'error_page.400'  : http_error_page,
	'error_page.404'  : http_error_page,
	'error_page.500'  : http_error_page,
})

serverConf = {
	'global': {
	}
}

# Read the config defined above
# then override it with any entries in server.conf
cherrypy.config.update(serverConf)
cherrypy.config.update(rootDir + "/server.conf")

appConf = {
	'/': {
		'tools.sessions.on': True,
		'tools.encode.on': True,
		'tools.encode.encoding': 'utf-8',
		'request.dispatch': setup_routes()
	},
	'/static': {
		'tools.staticdir.on': True,
		'tools.staticdir.dir': rootDir + '/static'
	},
	'/favicon.ico': {
		'tools.staticfile.on': True,
		'tools.staticfile.filename': rootDir + '/static/favicon.ico'
	}
}
	
application = cherrypy.Application(None, '/elastic', appConf)
application.merge(rootDir + '/app.conf')
