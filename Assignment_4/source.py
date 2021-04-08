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

    ack_count = 0
    old_RTT = 1
    RTT = 1 

    logger = assignment4.logging.get_logger("assignment-4-sender")
    header = bytes(str(ack_count)+'\r\n\r\n', 'utf-8') #should include ack number
    chunk_size = assignment4.MAX_PACKET-8#-len(header)
    pause = .08  #pause = .1 #original code
    
    offsets = range(0, len(data), assignment4.MAX_PACKET)

    for chunk in [data[i:i + chunk_size] for i in offsets]:
        eRTT = lambda oRTT, sRTT: 0.875*oRTT+ 0.125*sRTT
        if ack_count == 0:
            start = time.time() #start timer
            sock.send(header+chunk)
            end = time.time() #stop timer when you receive the ack
            elapsed = float(str(end-start)) #calculate elapsed time

            sample_RTT = 1
            #RTT = eRTT(elapsed, 1)
            #old_RTT = RTT
            old_RTT = elapsed
            ack_count+=1
        else:
            #print('(63) ack_count', ack_count)
            new_header = int(header.decode('utf-8').replace('\r\n\r\n',''))+1
            #print('(65) new header', new_header)
            #sock.send(bytes(str(ack_count)+str(chunk), 'utf-8'))

            try:
          #      sock.settimeout(old_RTT)
                sock.settimeout(RTT)
                returned_data = sock.recv(3)
                #print('(63) returned data', returned_data)
                ack_count = int(returned_data.decode('utf-8'))+1
                sock.send(bytes(str(ack_count)+str(chunk), 'utf-8'))
            except:
                pass
                #print('(67) hit the except :(')
                #sock.send(bytes(str(ack_count)+str(chunk), 'utf-8'))
            #sock.send(bytes(str(ack_count)+str(chunk), 'utf-8'))
            old_RTT = RTT
            RTT = old_RTT + 4*(old_RTT - RTT)
            #old_RTT = eRTT(old_RTT, (elapsed - sample_RTT) if sample_RTT < elapsed else (sample_RTT - elapsed))


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
    ack_count = 0
    logger = assignment4.logging.get_logger("assignment-4-receiver")

    num_bytes = 0
    data_ack = -1
    while ack_count != data_ack:
        data = sock.recv(assignment4.MAX_PACKET)
        data_ack = data.decode('utf-8')[:1]
#        if int(data.decode('utf-8')[:1]) != ack_count:
#          sock.send(bytes(str(ack_count), 'utf-8'))
#        else:
        #ack_count+=1
        #print('(99) ack count')

        sock.send(bytes(str(ack_count), 'utf-8'))
        logger.info("Received %d bytes", len(data))
        dest.write(data[1:])

        ack_count+=1
        #print('(119) ack_count and header', ack_count, data.decode('utf-8')[:1])

        #print('(95) ack count data ack',ack_count,data_ack)
        num_bytes += len(data)
        dest.flush()
    return num_bytes
