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

ack_count = 0
old_RTT = None

#def GLOBALS(ack_count=0, old_RTT=None):
#    return (ack_count, old_RTT)

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

    global ack_count
    global old_RTT

    logger = assignment4.logging.get_logger("assignment-4-sender")
    header = bytes(str(ack_count)+'\r\n\r\n', 'utf-8') #should include ack number
    chunk_size = assignment4.MAX_PACKET-8#-len(header)
    pause = .08  
    #pause = .1 #original code
    
    offsets = range(0, len(data), assignment4.MAX_PACKET)
    #ack_count, old_RTT = GLOBALS()
    for chunk in [data[i:i + chunk_size] for i in offsets]:
        eRTT = lambda oRTT, sRTT: 0.875*oRTT+ 0.125*sRTT
        if ack_count == 0:
            #print('(50) header and chunk?', header+chunk, type(header+chunk))
            start = time.time() #start timer
            sock.send(header+chunk)
            end = time.time() #stop timer when you receive the ack
            elapsed = float(str(end-start)) #calculate elapsed time

            sample_RTT = 1
            RTT = eRTT(elapsed, 1)
            old_RTT = RTT

            ack_count+=1
        else:
            print('(63) ack_count', ack_count)
            new_header = int(header.decode('utf-8').replace('\r\n\r\n',''))+1
            print('(65) new header', new_header)
            sock.send(bytes(str(ack_count)+str(chunk), 'utf-8'))
            try:
                sock.settimeout(old_RTT)
                returned_data = sock.recv(assignment4.MAX_PACKET)
                ack_count+=1
            except:
                pass

            old_RTT = eRTT(old_RTT, (elapsed - sample_RTT) if sample_RTT < elapsed else (sample_RTT - elapsed))


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
    global ack_count
    logger = assignment4.logging.get_logger("assignment-4-receiver")
    # Naive solution, where we continually read data off the socket
    # until we don't receive any more data, and then return.
    # keep track of your sequence number.
    num_bytes = 0
    while True:
        data = sock.recv(assignment4.MAX_PACKET)
        ack_count = data.decode('utf-8')[:1]
        print('(101) ack_count', ack_count)
        if int(data.decode('utf-8')[:1]):
            sock.send(data)
            break
        else:
          decdata = data.decode('utf-8')
          chunk = decdata[str(decdata).find('\r\n\r\n')+len('\r\n\r\n'):]
         #print('(104) data',data[str(data).find('\r\n\r\n')+len('\r\n\r\n'):], data[:str(data).find('\r\n\r\n')])
          header = str(decdata[:str(decdata).find('\r\n\r\n')])
          print('(107) header', header)
          
#          new_header = int(header.replace('\r\n\r\n',''))+1
          new_header = int(header.replace('\r\n\r\n',''))+1
          print('(113) new header', new_header)
          to_sender = str(new_header)+str(chunk)
          sock.send(bytes(to_sender, 'utf-8'))
          logger.info("Received %d bytes", len(data))
          dest.write(data)
        num_bytes += len(data)
        dest.flush()
        #print('(70)', num_bytes)
    return num_bytes
