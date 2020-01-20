#!/usr/bin/python
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
from database_Setup import Base, Restaurant, MenuItem, create_engine
from sqlalchemy.orm import sessionmaker
import cgi
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

# the dbsession gives me the staging zone

DBsession = sessionmaker(bind=engine)
session = DBsession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith('/insert'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ''
                output += '<html><body>'
                output += ' <h2> Okay, Add </h2>'
                output += \
                    '''<form method='POST' enctype='multipart/form-data' action='/insert'><h2>enter restaurant name to insert</h2><input name="name" type="text" ><input type="submit" value="Submit"> </form>'''
                output += '</body></html>'
                self.wfile.write(output.encode('utf-8'))
                return

            if self.path.endswith('/edit'):
                res_ID = self.path.split('/')[1]
                l = session.query(Restaurant).filter_by(id=res_ID).one()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ''
                output += '<html><body>'
                output += '<h1> edit as per your choice </h1>'
                output += \
                    '''<form method='POST' enctype='multipart/form-data' action='/%s/edit'><h2>enter new restaurant name  </h2><input name="name" type="text" ><input type="submit" value="Submit"> </form>''' \
                    % res_ID
                output += '</body></html>'
                self.wfile.write(output.encode('utf-8'))
                return

            if self.path.endswith('/delete'):
                res_ID = self.path.split('/')[1]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ''
                output += '<html><body>'
                output += '<h1> are you sure </h1>'
                output += \
                    '''<form enctype='multipart/form-data' action = "" method = "post">
    						<button>delete</button>
							<form>'''
                output += '</body></html>'
                self.wfile.write(output.encode('utf-8'))

                return

            if self.path.endswith('/restaurants'):
                qu = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ''
                output += '<html><body>'
                for i in qu:
                    output += '<h1> %s </h1>' % i.name
                    output += "<a href='/%s/delete'>delete</a></br>" \
                        % i.id
                    output += "<a href='/%s/edit'>edit</a>" % i.id
                output += \
                    "</br><a href='/insert'>add new restaurant</a>"
                self.wfile.write(output.encode('utf-8'))
                return
                
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        if self.path.endswith('/insert'):
            (ctype, pdict) = \
                cgi.parse_header(self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                
                messagecontent = fields.get('name')
                myres = Restaurant(name=messagecontent[0])
                session.add(myres)
                session.commit()
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()
            return

        if self.path.endswith('/edit'):
            (ctype, pdict) = \
                cgi.parse_header(self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                
                route = self.path.split('/')[1]
                messagecontent = fields.get('name')
                obj = \
                    session.query(Restaurant).filter_by(id=route).one()
                obj.name = messagecontent[0]
                session.commit()
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()
            return

        if self.path.endswith('/delete'):
        	ctype, pdict = cgi.parse_header(self.headers['content-type'])
        	pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        	if ctype == 'multipart/form-data':
        		fields = cgi.parse_multipart(self.rfile, pdict)
        		route = self.path.split('/')[1]
        		obj = session.query(Restaurant).filter_by(id=route).one()        
        		session.delete(obj)
        		session.commit()
        	self.send_response(301)
        	self.send_header('Content-type', 'text/html')
        	self.send_header('Location', '/restaurants')
        	self.end_headers()
        	return


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print('Web Server running on port %s' % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(' ^C entered, stopping web server....')
        server.socket.close()


if __name__ == '__main__':
    main()

