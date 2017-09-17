function loadRestService(htmlLocation, hostLocaton, requestType="GET", data = "") {
    requestRestservice(host_address=hostLocaton,
                       callback=function(response){
                        $(htmlLocation).html(response);
                       },
                       requestType=requestType,
                       data=data)
    return false;
}


function requestRestservice(host_address, callback, requestType="GET", data = "") {
    $.ajax({
     type: requestType,
     url: host_address,
     data: data,
     crossDomain: true,
     headers: {'ajax-lazy-load-call': true},
     xhrFields: {
          withCredentials: true
    },
     success:function(response, textStatus, request){
         // do stuff with json (in this case an array)
         callback(response);
     },
     error:function(xhr, ajaxOptions, thrownError){
         console.log("cannot load from:");
         console.log(host_address);
         console.log(xhr);
         console.log(ajaxOptions);
         console.log(thrownError);
         //alert("Error could not load content from: " + hostLocaton);
     }
    });

}

class ServiceHandler {
    constructor() {
        this.connection_dict = {};
    }

    connect(address, location) {
        if(location in this.connection_dict){
            // console.log("WebSocket ALLREADY OPEN: " + location + "\t" + address);
            return
        }
        var socket = new WebSocketHandler(address, location);
        this.connection_dict[location] = socket;
    }

    send_message(location, message) {
        this.connection_dict[location].connection.send(JSON.stringify(message))
    }
}


class WebSocketHandler{
    constructor(address, location) {
        this.location = location
        try{
            this.connection = new WebSocket(address);
        }catch(error){
            console.log(error);
            return
        }

        this.connection.onopen = function(){
           console.log('Connection open!');
           var event = new CustomEvent("onwebsocketopen", {'detail': location});
           document.dispatchEvent(event);
        }

        this.connection.onclose = function(){
           console.log('Connection closed');
        }

        this.connection.onerror = function(error){
           console.log('Error detected: ' + error);
        }

        this.connection.onmessage = function(e){
            var server_message = JSON.parse(e.data);
            if(server_message.hasOwnProperty('event')){
                var event = new CustomEvent(server_message.event, {'detail': server_message.data});
                document.dispatchEvent(event);
            }
            if (server_message.hasOwnProperty('panel')){
                $('#' + location).html(server_message.panel);
            }
        }
    }
}

var plugin_handler = new ServiceHandler()
