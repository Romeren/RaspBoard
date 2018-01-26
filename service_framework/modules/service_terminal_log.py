from service_framework.a_plugin import ThreadHandler as superClass


class Service(superClass):
    def initialize(self, module, stopevent):
        self.module = module
        self.stopevent = stopevent
        self.module.event_dispatcher.add_event_listener('*', self.print_log)

    def print_log(self, event):
        isInt, level = self.try_parse(self.module.log_level)
        if(isInt and event.type == 'LOG' and level <= event.data[0]):
            print(event.origin_host, event.data[1:])
        elif(isInt and event.type != 'LOG' and level == 0):
            print(event.type)
        elif(not isInt and self.module.log_level == 'ALL'):
            if(event.type == 'LOG'):
                print(event.origin_host, event.data[1:])
            else:
                print(event.origin_host, event.type, event.data)

    def try_parse(self, unknown_var):
        try:
            int_var = int(unknown_var)
            return True, int_var
        except Exception as e:
            return False, unknown_var


config = {
    "service_name": "builtin/terminal_log",
    "handler": Service,
    "service_type": "thread",
    "service_category": "system",
    "dependencies": []
}
