# cherrypy-elastic
A template for creating an Elasticsearch interface using CherryPy

# Notes
This has been cut from a working project to provide a RESTful API onto an Elasticsearch database.  The full project also has a Swagger.io interface to give the user an easy to use and fully documented system.

cherryElastic.py has it's config set up in a dictionary object appConf.  However this is able to be overridden by creating a file app.conf in the same directory.

The only functionality not stripped out of this example file allows the user to search for an Elasticsearch document either by id or by free text.  To restore further functionality the functions 'objects' and 'search' would need to be modified along with some urls added back into 'setup_routes'.