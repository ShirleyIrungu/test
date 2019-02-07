import logging
import multiprocessing
import socket

from gossip.communication.client_receiver import GossipClientReceiver

class GossipServer(multiprocessing.Process):
class GossipServer(multiprocessing.Process):
    def __init__(self, server_label, client_receiver_label, bind_address, tcp_port, to_controller_queue,
                 connection_pool):
        """ The Gossip server waits for new connections established by other clients. It also instantiates new receivers
        for incoming connections."""
        multiprocessing.Process.__init__(self)
        self.server_label = server_label
        self.client_receiver_label = client_receiver_label
        self.bind_address = bind_address
        self.tcp_port = tcp_port
        self.to_controller_queue = to_controller_queue
        self.connection_pool = connection_pool

    def run(self):
        """ Typical run method for the sender process. It waits for new connections, refers to newly instantiated
        receiver instances, and finally starts the new receivers. """
        try:
            logging.info('%s started (%s:%d) - PID: %s' % (self.server_label, self.bind_address, self.tcp_port,
                                                           self.pid))
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.bind_address, self.tcp_port))
            server_socket.listen(5)
            while True:
                client_socket, address = server_socket.accept()
                tcp_address, tcp_port = address
                connection_identifier = '%s:%d' % (tcp_address, tcp_port)
                self.connection_pool.add_connection(connection_identifier, client_socket)
                logging.info("%s | Added new connection to connection pool" % self.server_label)
                client_receiver = GossipClientReceiver(self.client_receiver_label, client_socket, tcp_address, tcp_port,
                                                       self.to_controller_queue, self.connection_pool)
                client_receiver.start()
            server_socket.close()
        except OSError as os_error:
            logging.error('%s crashed (%s:%d) - PID: %s - %s' % (self.server_label, self.bind_address, self.tcp_port,
                                                                 self.pid, os_error))