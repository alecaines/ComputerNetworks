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

def GLOBALS(ack_count=0, old_RTT=None):
    return (ack_count, old_RTT)

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
    header = b''
    chunk_size = assignment4.MAX_PACKET#-len(header)
    pause = .08  
    #pause = .1 #original code
    
    offsets = range(0, len(data), assignment4.MAX_PACKET)
    ack_count, old_RTT = GLOBALS()
    for chunk in [data[i:i + chunk_size] for i in offsets]:

        eRTT = lambda oRTT, sRTT: 0.875*oRTT+ 0.125*sRTT

        if ack_count == 0:
            start = time.time() #start timer
            sock.send(chunk)
            end = time.time() #stop timer when you receive the ack
            elapsed = float(str(end-start)) #calculate elapsed time

            sample_RTT = 1
            RTT = eRTT(elapsed, 1)
            old_RTT = RTT

            ack_count+=1
        else:
            sock.send(chunk)
            time.sleep(old_RTT)
            old_RTT = eRTT(old_RTT, elapsed - sample_RTT)
            ack_count+=1


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
    # keep track of your sequence number.
    num_bytes = 0
    while True:
        data = sock.recv(assignment4.MAX_PACKET)
    #    print('-------------------------------')
    #    print('(63) data:', data)
    #    print('-------------------------------')
        if not data:
            print('(64) send back?')
            break
#        else:
#          sock.send(b'ack')
        logger.info("Received %d bytes", len(data))
        dest.write(data)
        num_bytes += len(data)
        dest.flush()
        #print('(70)', num_bytes)
    return num_bytes
