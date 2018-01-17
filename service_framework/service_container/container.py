from tornado import web, ioloop  # NOQA
from service_framework.common import utilities as util
from service_framework.common_modules import ui_modules as uim


class Container(object):
    """docstring for Container"""

    def __init__(self, port, settings={}):
        self.port = port

        if('ui_modules' not in self.settings):
            self.settings["ui_modules"] = {
                "Rest_Service_Module": uim.Rest_Service_Module,
                "Websocket_Service_Module": uim.Websock_Service_Module,
                "Head_Module": uim.Head_Module
                }
        else:
            self.settings["ui_modules"]["Rest_Service_Module"] = uim.Rest_Service_Module
            self.settings["ui_modules"]["Websocket_Service_Module"] = uim.Websock_Service_Module
            self.settings["ui_modules"]["Head_Module"] = uim.Head_Module

        
        app = self.configure_module()
        self.start_webserver(app)


    def start_webserver(self, app):
        # add listener to port:
        app.listen(self.port)
        print("Module started!")
        ioloop.IOLoop.instance().start()

    def configure_module(self):
        # set up tornado frame work:
        return web.Application(paths, **self.settings)