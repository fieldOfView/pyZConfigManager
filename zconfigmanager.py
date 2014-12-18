#!/usr/bin/python3

from zocp import ZOCP
import logging
import socket
import time
import json

# maintain a list of peer names
peers_names = {}

def on_peer_enter(peer, name, *args, **kwargs):
    peers_names[peer.hex] = name


if __name__ == '__main__':
    zl = logging.getLogger("zocp")
    zl.setLevel(logging.INFO)

    # setup ZOCP node, and run it for some time to discover
    # the current network
    z = ZOCP()
    z.on_peer_enter = on_peer_enter
    z.set_name("ConfigManager@%s" % socket.gethostname())
    z.start()
    start = time.time()
    while (time.time() - start) < 0.5:
        z.run_once(0)

    # create network description
    peers = {}
    for peer, capabilities in z.peers_capabilities.items():
        # store node name
        peer_name = peers_names[peer.hex]
        print("Adding node '%s' (%s)" % (peer_name, peer.hex))
        capabilities["_name"] = peer_name

        # add node names to subscribers
        for c in capabilities:
            if "subscribers" in capabilities[c]:
                subscribers = capabilities[c]["subscribers"]
                for s in range(0, len(subscribers)):
                    capabilities[c]["subscribers"][s].append( peers_names[subscribers[s][0]] )

        peers[peer.hex] = capabilities

    # write network description to file
    print("Writing to file")
    f = open("network.json", "w")
    f.write(json.dumps(peers, indent=4, sort_keys=True))
    f.close()

    # shut down ZOCP node
    z.stop()
    print("FINISH")


