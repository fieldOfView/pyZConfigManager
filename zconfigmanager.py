#!/usr/bin/python3

from argparse import ArgumentParser
from zocp import ZOCP
import logging
import socket
import time
import json

class ZConfigManagerNode(ZOCP):
    def __init__(self, nodename=""):
        self.peers_names = {}

        self.logger = logging.getLogger(nodename)
        self.logger.setLevel(logging.INFO)

        super().__init__()

        self.set_name(nodename)
        self.start()


    def stop(self):
        self.logger.info("Closing ZOCP node...")
        super().stop()


    def discover(self, duration = 0.5):
        self.logger.info("Discovering ZOCP network...")
        start = time.time()
        while (time.time() - start) < duration:
            z.run_once(0)


    def build_network_tree(self):
        # create network description
        peers = {}
        for peer, capabilities in z.peers_capabilities.items():
            # store node name
            peer_name = self.peers_names[peer.hex]
            self.logger.info("Adding node '%s' (%s)..." % (peer_name, peer.hex))
            capabilities["_name"] = peer_name

            # add node names to subscribers
            for c in capabilities:
                if "subscribers" in capabilities[c]:
                    subscribers = capabilities[c]["subscribers"]
                    for s in range(0, len(subscribers)):
                        capabilities[c]["subscribers"][s].append( 
                                self.peers_names[subscribers[s][0]])

            peers[peer.hex] = capabilities

        return peers


    def write(self, filename, tree):
        self.logger.info("Writing to file '%s'..." % filename)
        f = open(filename, "w")
        f.write(json.dumps(network_tree, indent=4, sort_keys=True))
        f.close()


    def on_peer_enter(self, peer, name, *args, **kwargs):
        # maintain a list of peer names
        self.peers_names[peer.hex] = name


if __name__ == '__main__':
    # setup ZOCP node, and run it for some time to discover
    # the current network
    z = ZConfigManagerNode("ConfigManager@%s" % socket.gethostname())
    z.discover(0.5)
    network_tree = z.build_network_tree()

    # write network description to file
    z.write("network.json", network_tree)

    # shut down ZOCP node
    z.stop()
