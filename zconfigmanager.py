#!/usr/bin/python3

from argparse import ArgumentParser
from zocp import ZOCP
import logging
import socket
import time
import json
import uuid

class ZConfigManagerNode(ZOCP):
    def __init__(self, nodename=""):
        self.peers_names = {}
        self.peers_alternatives = {}

        self.logger = logging.getLogger(nodename)
        self.logger.setLevel(logging.INFO)

        super(ZConfigManagerNode, self).__init__()

        self.set_name(nodename)
        self.start()


    def stop(self):
        self.logger.info("Closing ZOCP node...")
        super(ZConfigManagerNode, self).stop()


    def discover(self, duration = 0.5):
        self.logger.info("Discovering ZOCP network...")
        start = time.time()
        while (time.time() - start) < duration:
            self.run_once(0)


    def on_peer_enter(self, peer, name, *args, **kwargs):
        # maintain a list of peer names
        self.peers_names[peer.hex] = name


    def find_peer(self, peer, name):
        if peer not in self.peers_alternatives:
            # find a peer by its name, but do not return the same peer if it 
            # has already been associated with a different original peer id 
            self.peers_alternatives[peer] = None
            exclude = self.peers_alternatives.values()
            for alt_hex, alt_name in self.peers_names.items():
                alt_peer = uuid.UUID(alt_hex)
                if alt_name == name and alt_peer not in exclude:
                    self.peers_alternatives[peer] = alt_peer
                    break

        return self.peers_alternatives[peer]


    def build_network_tree(self):
        # create network description
        peers = {}
        for peer, capabilities in self.peers_capabilities.items():
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


    def restore_network_tree(self, tree):
        # restore network from description
        peers = self.peers_capabilities
        for peer_hex, peer_capabilities in tree.items():
            peer = uuid.UUID(peer_hex)
            peer_name = peer_capabilities["_name"]
            self.logger.info("Looking for node '%s' (%s)..." % (peer_name, peer_hex))
            if peer not in peers.keys():
                # if the peer has been restarted it will have a different id
                peer = self.find_peer(peer, peer_name)
                if peer:
                    self.logger.info("Alternative for node '%s' found: %s" % (peer_name, peer.hex))
                else:
                    self.logger.warning("Node '%s' not found." % peer_name)
                    continue

            # remove name from capabilities
            peer_capabilities.pop("_name", None)

            for c in peer_capabilities:
                if "subscribers" in peer_capabilities[c]:
                    subscribers = peer_capabilities[c]["subscribers"]
                    for s in subscribers:
                        subscriber_peer = uuid.UUID(s[0])
                        subscriber_sensor = s[1]
                        subscriber_name = s[2]
                        if subscriber_peer not in peers.keys():
                            # if the peer has been restarted it will have a different id
                            subscriber_peer = self.find_peer(subscriber_peer, subscriber_name)
                            if subscriber_peer:
                                self.logger.info("Alternative for subscriber '%s' found: %s" % (subscriber_name, subscriber_peer.hex))
                            else:
                                self.logger.warning("Subscriber '%s' not found." % subscriber_name)
                                continue

                        # restore subscription
                        self.signal_subscribe(peer, c, subscriber_peer, subscriber_sensor)

                    # remove subscribers from capabilities
                    peer_capabilities[c].pop("subscribers", None)

            # restore capability (structure, value)
            self.peer_set(peer, peer_capabilities)


    def write(self, filename):
        tree = self.build_network_tree()

        self.logger.info("Writing to file '%s'..." % filename)
        f = open(filename, "w")
        f.write(json.dumps(tree, indent=4, sort_keys=True))
        f.close()


    def read(self, filename):
        self.logger.info("Reading from file '%s'..." % filename)
        tree = None
        try:
            f = open(filename, "r")
            tree = json.loads(f.read())
            f.close()
        except ValueError:
            self.logger.error("Could not parse file!")
        except FileNotFoundError:
            self.logger.error("Could not read file!")

        if tree:
            self.restore_network_tree(tree)


if __name__ == '__main__':
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-w", "--write", action="store",
                       help="write the configuration to disk")
    group.add_argument("-r", "--read", action="store",
                       help="read the configuration from disk")
    args = parser.parse_args()

    # setup ZOCP node, and run it for some time to discover
    # the current network
    z = ZConfigManagerNode("ConfigManager@%s" % socket.gethostname())
    z.discover(0.5)

    if(args.write):
        # write network description to file
        z.write(args.write)
    else:
        # read network description from file
        z.read(args.read)

    # shut down ZOCP node
    z.stop()
    z = None
