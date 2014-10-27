#!env python
import bottle
import webui

bottle.run(host='localhost', port=8080, reloader=True, server='paste')
