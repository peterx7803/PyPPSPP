import logging
import socket

class SimpleTracker(object):
    """This class abstracts a simple tracket. It can later be replaced with PPSP-TP"""

    def __init__(self):
        self._tracekr_protocol = None
        self._myip = self._GetMyIP()
        self._swarm = None

    def SetTrackerProtocol(self, proto):
        self._tracekr_protocol = proto

    def ConnectionLost(self):
        """Connection to the tracker was lost..."""
        # We can continue operating even if connection to the tracker is lost
        return None

    def _GetMyIP(self):
        """Get My IP address. This is an awful hack"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('1.1.1.1', 0))
        return s.getsockname()[0]

    def DataReceived(self, data):
        """Called with deserialized message from the tracker server"""
        
        if data['type'] == 'other_peers':
            # We got information about other peers in the system
            for member in data['details']:
                m = self._swarm.AddMember(member[0], member[1])
                if m != None:
                    m.SendHandshake()

        else:
            logging.info("Unhandled Tracker message: {0}".format(data))
    
    def SetSwarm(self, swarm):
        """Link swarm to a tracker"""
        # TODO: Here we should actually link Hive(-like) object instead of a swarm
        self._swarm = swarm

    def RegisterWithTracker(self, swarm_id):
        """Inform the tracker that we are ready to receive connection. swarm_id not used for now"""

        data = {}
        data['type'] = 'register'
        data['endpoint'] = (self._myip, 6778)

        self._tracekr_protocol.SendData(data)

    def UnregisterWithTracker(self):
        """Inform tracker that we are leaving"""
        
        data = {}
        data['type'] = 'unregister'
        data['endpoint'] = (self._myip, 6778)

        self._tracekr_protocol.SendData(data)

