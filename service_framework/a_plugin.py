# -*- coding: utf-8 -*-  # NOQA
""" sample implementation of a plugin
"""
# from plugin_module import Plugin_module
import json
import sys
import os.path
from tornado import gen
from tornado import httpclient
from tornado import web
from tornado import websocket
from tornado import template
from urllib import urlencode
from threading import Lock
cl = []

class BaseHandler(object):
    """docstring for """
    def __init__(self):
        super(BaseHandler, self).__init__()

    def initialize(self, module):
        # this method is called as a new thread on start
        self.module = module

    def dump_message(self, message):
        try:
            return json.dumps(message)
        except Exception, e:
            print('JSON COULD NOT BE PARSED')
            return None

    def load_message(self, message):
        try:
            return json.loads(message)
        except Exception, e:
            print("MESSAGE COULD NOT BE PARSED!")
            return None

    def set_dependencies(self, context, config):
        context["references"] = {}
        # add reference to self:
        selfRef = next(self.module.get_services(config['service_type'] + "/" + config['service_category'] + "/" + config['service_name']))  # NOQA

        selfRef = self.make_dependency_ref(selfRef)
        context['references']['self'] = selfRef
        context['references'][config['service_name']] = selfRef

        jsRef = next(self.module.get_services('rest/miscellanceous/javascripts'), None)
        context['references']['javascript'] = [self.make_dependency_ref(jsRef)]
        # add reference to all dependencies:
        if("dependencies" not in config):
            return context
        for dep in config['dependencies']:
            context['references'][dep["name"]] = []

            services = self.module.get_services(dep["service"])
            service = next(services, None)
            while(service):
                context['references'][dep["name"]].append(self.make_dependency_ref(service))  # NOQA
                service = next(services, None)

            # if no service was found add a enpty reference!
            if(len(context['references'][dep["name"]]) == 0):
                context['references'][dep["name"]].append(self.make_dependency_ref(None))  # NOQA

        return context

    def make_dependency_ref(self, service):
        if(service is None):
            return self.__get_service_ref(service_name="", addr="")
        addr = self.get_service_address_from_request(service)
        return self.__get_service_ref(service_name=service['service_name'],
                                      addr=addr)

    def __get_service_ref(self,
                          service_name,
                          addr,
                          error=False):
        return {
                "name": service_name.replace("_", " "),
                "service_name_js": service_name.replace("/", "\\\/"),
                "service_name": service_name,
                "address": addr,
                "hasError": error
            }

    def get_service_address_from_request(self, request):
        address = None
        protocall = "http://"
        if(request['service_type'] == 'websocket'):
            protocall = 'ws://'
        if request is not None:
            address = protocall
            address += request["host_address"]
            address += ":" + str(request["port"])
            address += "/" + request["service_name"]
        return address

    def send_external_request(self, address, params, isPost=False):
        params = urlencode(params)

        # get encoded user token:
        header = {}
        token = self.get_cookie("user")
        if token is not None:
            header["Cookie"] = "user="+token

        if isPost:
            client = httpclient.AsyncHTTPClient()
            return gen.Task(client.fetch,
                            address,
                            method="POST",
                            body=params,
                            headers=header)
        else:
            url = address + "/?" + params

            client = httpclient.AsyncHTTPClient()
            return gen.Task(client.fetch,
                            request=url,
                            method="GET",
                            headers=header)

class ThreadHandler(BaseHandler):

    def __init__(self):
        super(ThreadHandler, self).__init__()
    
    def initialize(self, module, stop_event):
        # this method is called as a new thread on start
        self.module = module


class SocketHandler(websocket.WebSocketHandler, BaseHandler):

    def __init__(self, application, request, **kwargs):
        super(websocket.WebSocketHandler, self).__init__(application,
                                                         request,
                                                         **kwargs)
        self._on_close_called = False

    def initialize(self, event):
        print(event)
        # self.module = module

    def register_event(self, on_message, function):
        if(hasattr(self, "messages_for_listening") is False):
            self.messages_for_listening = {}
        if(on_message in self.messages_for_listening):
            print("Message allready in events! and will be replaced!")
            self.messages_for_listening[on_message] = function
        else:
            self.messages_for_listening[on_message] = function

    def check_origin(self, origin):
        return True

    def open(self):
        print("Connection opened!")
        # if self not in cl:
        #     cl.append(self)

            # TODO(SECURITY): handle authentication and premissions
            # self.user = self.get_current_user()
        if("on_open" in self.messages_for_listening):
            message = {"event": "on_open", "message": "connection opened"}
            self.messages_for_listening["on_open"](message)

    def on_message(self, message):
        jsonMsg = self.load_message(message)
        if(jsonMsg is None):
            self.send({"error": "Invalid message!, message must be JSON"})
            return
        if("event" in jsonMsg):
            if(jsonMsg["event"] in self.messages_for_listening):
                self.messages_for_listening[jsonMsg["event"]](jsonMsg)

    def on_close(self):
        # print("WebSocket closed")
        # if self in cl:
        #     cl.remove(self)
        if("on_close" in self.messages_for_listening):
            message = {"event": "on_close", "message": "connection closed"}
            self.messages_for_listening["on_close"](message)

    def send(self, message):
        self.write_message(self.dump_message(message))

    def message_contains_fields(self, message, *fields):
        missing = []
        for field in fields:
            if(field in message):
                continue
            else:
                missing.append(field)
        return missing

    def send_message_missing_fields_error(self, missing_fields):
        self.send({"error": "Request is missing parameters!",
                   "message": missing_fields})


class RestHandler(web.RequestHandler, BaseHandler):

    def __init__(self, application, request, **kwargs):
        super(RestHandler, self).__init__(application, request, **kwargs)

    def initialize(self, module):
        self.module = module

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def set_default_headers(self):
        origin = self.request.headers.get('Origin')
        # refer = self.request.headers.get('Referer')
        # TODO(SECURITY): check origin from a list!
        if origin is None:
            self.set_header("Access-Control-Allow-Origin", "*")
        else:
            # print(origin)
            # print(refer)
            self.set_header("Access-Control-Allow-Origin", origin)
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header("Access-Control-Allow-Headers", "ajax-lazy-load-call")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get_basic_context(self, config):
        context = {}

        # check the origin of the request
        origin = self.request.headers.get('Origin')
        if origin is None:
            context["origin"] = 'DIRECT'
        else:
            context["origin"] = 'CROSS'

        # check if request is lazy load
        isLazyLoad = self.request.headers.get('ajax-lazy-load-call')
        if(isLazyLoad is not None and isLazyLoad):
            context["isLazyLoad"] = isLazyLoad
        else:
            context["isLazyLoad"] = False

        # set user information:
        context = self.__set_user_info(context)

        # set references to dependencies:
        context = self.set_dependencies(context, config)

        return context

    def __set_user_info(self, context):
        user = self.get_current_user()
        context["user"] = user
        if user:
            context["loggedin"] = True
        else:
            context["loggedin"] = False
        return context


    def render_response(self, template_name, **kwargs):
        # render the response for an request by populating the specified template with the given context/key-value argument. 
        if self._finished:
            raise RuntimeError("Cannot render() after finish()")

        # Generate the given template with the given arguments.

        # If no template_path is specified, use the path of the calling file
        template_path = self.get_template_path()
        if not template_path:
            frame = sys._getframe(0)
            web_file = frame.f_code.co_filename
            while frame.f_code.co_filename == web_file:
                frame = frame.f_back
            template_path = os.path.dirname(frame.f_code.co_filename)

        # translate path:
        root = os.path.abspath(template_path)

        # build specific path to file
        path = os.path.join(root, template_name)

        # set parameters for lazyload:
        top = '<!DOCTYPE html>\n<html>\n{% module Head_Module(context) %}\n<body>'
        buttom = '</body>\n</html>'
        #print(kwargs)
        context = kwargs['context']
        if("isLazyLoad" in context):
            # print("found is lazyload " + str(context['isLazyLoad']))
            if(context['isLazyLoad']):
                top = ''
                buttom = ''
                # print("ISLAZYLOAD TOP AND BUTTOM REMOVED!!")

        # build template:
        t = None
        with open(path, "rb") as f:
            top += f.read()
            top += buttom
            t = template.Template(top, name=template_name)
        
        namespace = self.get_template_namespace()
        namespace.update(kwargs)

        # populate template with context:
        html = t.generate(**namespace)

        # Insert the additional JS and CSS added by the modules on the page
        js_embed = []
        js_files = []
        css_embed = []
        css_files = []
        html_heads = []
        html_bodies = []
        for module in getattr(self, "_active_modules", {}).values():
            embed_part = module.embedded_javascript()
            if embed_part:
                js_embed.append(utf8(embed_part))
            file_part = module.javascript_files()
            if file_part:
                if isinstance(file_part, (unicode_type, bytes)):
                    js_files.append(file_part)
                else:
                    js_files.extend(file_part)
            embed_part = module.embedded_css()
            if embed_part:
                css_embed.append(utf8(embed_part))
            file_part = module.css_files()
            if file_part:
                if isinstance(file_part, (unicode_type, bytes)):
                    css_files.append(file_part)
                else:
                    css_files.extend(file_part)
            head_part = module.html_head()
            if head_part:
                html_heads.append(utf8(head_part))
            body_part = module.html_body()
            if body_part:
                html_bodies.append(utf8(body_part))

        def is_absolute(path):
            return any(path.startswith(x) for x in ["/", "http:", "https:"])
        if js_files:
            # Maintain order of JavaScript files given by modules
            paths = []
            unique_paths = set()
            for path in js_files:
                if not is_absolute(path):
                    path = self.static_url(path)
                if path not in unique_paths:
                    paths.append(path)
                    unique_paths.add(path)
            js = ''.join('<script src="' + escape.xhtml_escape(p) +
                         '" type="text/javascript"></script>'
                         for p in paths)
            sloc = html.rindex(b'</body>')
            html = html[:sloc] + utf8(js) + b'\n' + html[sloc:]
        if js_embed:
            js = b'<script type="text/javascript">\n//<![CDATA[\n' + \
                b'\n'.join(js_embed) + b'\n//]]>\n</script>'
            sloc = html.rindex(b'</body>')
            html = html[:sloc] + js + b'\n' + html[sloc:]
        if css_files:
            paths = []
            unique_paths = set()
            for path in css_files:
                if not is_absolute(path):
                    path = self.static_url(path)
                if path not in unique_paths:
                    paths.append(path)
                    unique_paths.add(path)
            css = ''.join('<link href="' + escape.xhtml_escape(p) + '" '
                          'type="text/css" rel="stylesheet"/>'
                          for p in paths)
            hloc = html.index(b'</head>')
            html = html[:hloc] + utf8(css) + b'\n' + html[hloc:]
        if css_embed:
            css = b'<style type="text/css">\n' + b'\n'.join(css_embed) + \
                b'\n</style>'
            hloc = html.index(b'</head>')
            html = html[:hloc] + css + b'\n' + html[hloc:]
        if html_heads:
            hloc = html.index(b'</head>')
            html = html[:hloc] + b''.join(html_heads) + b'\n' + html[hloc:]
        if html_bodies:
            hloc = html.index(b'</body>')
            html = html[:hloc] + b''.join(html_bodies) + b'\n' + html[hloc:]

        # send response:
        self.finish(html)

    def get(self):
        self.set_default_headers()

    def post(self):
        self.set_default_headers()

    def options(self):
        self.set_default_headers()