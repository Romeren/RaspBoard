import zmq
import json
from RaspBoard.service_framework.events.event_module import Event as frameworkEvent

class Event_Subscriber(object):
    """docstring for Event_Subscriber"""
    def __init__(self, event_dispatcher):
        super(Event_Subscriber, self).__init__()
        self.event_dispatcher = event_dispatcher

    def subscribe(self, broker_address, broker_port, stop_event):
        print("SUBSCRIBER HAVE BEEN STARTED!")

        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        bk_url = "tcp://" + broker_address + ":" + str(broker_port)
        socket.connect(bk_url)

        # initiate listener:
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        while (not stop_event.is_set()):
            socks = dict(poller.poll(1000))
            if socket in socks and socks[socket] == zmq.POLLIN:
                [event, data] = socket.recv_multipart()
                data = json.loads(data.decode("utf-8"))

                print(event, data)
                self.event_dispatcher.dispatch_event(frameworkEvent(event, data=data))
        print("SUBSCRIBER HAVE BEEN TERMINATED!")

        