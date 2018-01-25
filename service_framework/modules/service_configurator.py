from service_framework.a_plugin import RestHandler as superClass


class Service(superClass):

    def get(self):
        lsr = [p for p in self.module.local_service_register]
        gsr = [p for p in self.module.global_service_register]
        response = {
            'ip_address': self.module.ip_address,
            'port': self.module.port,
            'application_secret': self.module.application_secret,
            'cookie_secret': self.module.cookie_secret,
            'local_service_register': lsr,
            'global_service_register': gsr
        }
        self.write(self.dump_message(response))

config = {
    "service_name": "builtin/service_configurator",
    "handler": Service,
    "service_type": "rest",
    "service_category": "system",
    "dependencies": []
}
