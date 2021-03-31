"""
Where solution code to Assignment should be written.  No other files should
be modified.
"""

import socket
import io
import time
import typing
import struct
import assignment4
import assignment4.logging


def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.
    """

    # Naive implementation where we chunk the data to be sent into
    # packets as large as the network will allow, and then send them
    # over the network, pausing half a second between sends to let the
    # network "rest" :)
    logger = assignment4.logging.get_logger("assignment-4-sender")
    chunk_size = assignment4.MAX_PACKET
    print('(32) chunk_size:', chunk_size, len(data))
    print('(33) do note that all lossy messages are missing exactly one chunk of data. So it drops one chunk of data because it is waiting one "unit" of time to short. Increase the speed of transmission or increase the throughput.')
    pause = .08
    #pause = .1 #original code
    
    offsets = range(0, len(data), assignment4.MAX_PACKET)

    for chunk in [data[i:i + chunk_size] for i in offsets]:
        sock.send(chunk)
        logger.info("Pausing for %f seconds", round(pause, 2))
        time.sleep(pause)


def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    """
    Implementation of the receiving logic for receiving data over a slow,
    lossy, constrained network.

    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.

    Return:
        The number of bytes written to the destination.
    """
    logger = assignment4.logging.get_logger("assignment-4-receiver")
    # Naive solution, where we continually read data off the socket
    # until we don't receive any more data, and then return.
    num_bytes = 0
    while True:
        data = sock.recv(assignment4.MAX_PACKET)
        print('-------------------------------')
        print('(63) data:', data)
        print('-------------------------------')
        if not data:
            print('(64) send back?')
            break
        logger.info("Received %d bytes", len(data))
        dest.write(data)
        num_bytes += len(data)
        dest.flush()
        print('(70)', num_bytes)
    return num_bytes
