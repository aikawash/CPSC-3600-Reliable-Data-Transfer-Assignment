from Simulator import Simulator, EventEntity
from enum import Enum
from struct import pack, unpack

# In this class you will implement a full-duplex Go-Back-N client. Full-duplex means that this client can 
# both send and receive data. You are responsible for implementing a Go-Back-N protocol in a simulated
# Transport layer. We are not going to use real network calls in this project, as we want to precisely 
# simulate when packet delay, loss, and corruption occurs. As such, your simulated transport protocol
# will interface with the Simulator object to communicate with simulated Application and Network layers.
#

# The Simulator will call three functions that you are responsible for implementing. These functions define
# the interface by which the simulated Application and Network layers communicate with your transport layer:
# - receive_from_application_layer(payload) will be called when the Simulator has new data from the application
#   layer that needs to be sent across the network
# - receive_from_network_layer(byte_data) will be called when the Simulator has received a new packet from the
#   network layer that the transport layer needs to process
# - timer_interrupt() will be called when the Simulator detects that a timer has expired 


# Your code can communicate with the Simulator by calling four methods:
# - Call self.simulator.pass_to_application_layer(data) when your Transport layer has successfully received and processed
#   a data packet from the other host that needs to be delivered up to the Application layer
#    * pass_to_application_layer(data) expects to receive the payload of a packet as a decoded string, not as the bytes object 
#      generated by unpack
# - Call self.simulator.pass_to_network_layer(byte_data) when your Transport layer has created a data packet or an ACK packet
#   that needs to be sent across the network to the other host
#    * pass_to_network_layer() expects to receive a packet that has been converted into a bytes object using pack. See the
#      next section in this comment for more detail
# - Call self.simulator.start_timer(self.entity, self.timer_interval) when you want to start a timer
# - Call self.simulator.stop_timer(self.entity) when you want to stop the running timer


# You will need to write code to pack/unpack data into a byte representation appropriate for 
# communication across a network. For this assignment, you will assume that all packets use the following header:
# - Sequence Number (int)           -- Set to 0 if this is an ACK
# - Acknowledgement Number (int)    -- Set to 0 if this is not an ACK
# - Checksum (half)                 -- Compute a UDP Checksum, as discussed in class
# - Acknowledgement Flag (boolean)  -- Set to True if sending an ACK, otherwise False
# - *Payload* length, in bytes (int)  -- Set this to 0 when sending an ACK message, as these will not carry a payload
# - Payload (string)                -- Leave this empty when sending an ACK message
# When unpacking data in this format, it is recommended to first unpack the fixed length header. After unpacking the
# header, you can determine if there is a payload, based on the size of Payload Length.
# NOTE: It is possible for payload length to be corrupted. In this case, you will get an Exception similar to
#       "unpack requires a buffer of ##### bytes". If you receive this exception, this is a sign that the packet is
#       corrupt. This is not the only way the packet can be corrupted, but is a special case of corruption that will
#       prevent you from unpacking the payload. If you can unpack the payload, use the checksum to determine if the
#       packet is corrupted. If you CAN'T unpack the payload, then you already KNOW that the packet is corrupted.


# Finally, you will need to implement the UDP Checksum algorithm to check for corruption in your packets. 
# As discussed in class, sum each of the 16-bit words of the packet, carrying around any overflow bits. Once you 
# have summed all of the 16-bit words, perform the 1's complement. If a packet contains an odd number of bytes 
# (i.e. the last byte doesn't fit into a 16-bit word), pad the packet (when computing the checksum) with a 0 byte. 
# When receiving a packet, check that it is valid using this checksum.


# NOTE: By default, all of the test cases created for this program capture print() output and save it in a log
#       file with the same name as the test case being run. This will prevent you from printing to the terminal
#       while your code is running (your print statements will be added to the log file instead)
#       You can disable this functionality by editing the test*.cfg file you are working on and removing the  
#       --capture_log argument (just delete it). Do NOT change any other of the option parameters in test*.cfg


class GBNHost():

    # The __init__ method accepts:
    # - a reference to the simulator object
    # - the name for this entity (EntityType.A or EntityType.B)
    # - the interval for this entity's timer
    # - the size of the window used for the Go-Back-N algorithm
    def __init__(self, simulator, entity, timer_interval, window_size):
        
        # These are important state values that you will need to use in your code
        self.simulator = simulator
        self.entity = entity
        
        # Sender properties
        self.timer_interval = timer_interval        # The duration the timer lasts before triggering
        self.window_size = window_size              # The size of the seq/ack window
        self.window_base = 0                        # The last ACKed packet. This starts at 0 because no packets 
                                                    # have been ACKed
        self.next_seq_num = 1                       # The SEQ number that will be used next
        self.unACKed_buffer = {}                    # A buffer that stores all sent but unACKed packets
        self.app_layer_buffer = []                  # A buffer that stores all data received from the application 
                                                    #layer that hasn't yet been sent
        
        # Receiver properties
        self.expected_seq_number = 1                # The next SEQ number expected

        # NOTE: Do not edit/remove any of the code in __init__ ABOVE this line. You need to edit the line below this
        #       and may add other functionality here if so desired
        
        #dummyPack 
        self.last_ACK_pkt = self.make_pkt(True, 0,0, None, 0)
                            # TODO: The last ACK pkt sent. You should initialize this to a
                                                    # packet with ACK = 0 in case an error occurs on the first packet received. 
                                                    # If that occurs, this default ACK can be sent in response
   
    def make_pkt(self, ACK_flag, seq_num, ack_num, payload = None, checksum=None):
        #payload.encode()
       # payloadLength = len.payload
        #newPack = pack('!!?!s', self.next_seq_num, 0, False, payloadLength, payload)
        if payload is not None and checksum is None:
            pkt = pack("!ii?i%is" % len(payload), seq_num, ack_num, ACK_flag, len(payload), payload.encode())
            checksum = self.checksum(pkt)
            pkt = pack("!iiH?i%is" % len(payload), seq_num, ack_num, checksum, ACK_flag, len(payload), payload.encode())
            return pkt

        # ! int , ? bool, d double, 
        else:
            pkt = pack('!ii?i', 0, ack_num, ACK_flag, 0)
            checksum = self.checksum(pkt)
            pkt = pack("!iiH?i", 0, ack_num, checksum, ACK_flag, 0)
            return pkt
    

        #payload.SequenceNumber

        #newPacket["Sequence Number"] = payload.SequenceNumber
        #newPacket["Acknowledgement Number"] = payload.ACK
        #newPacket["Checksum"] = payload.checksum
        #newPacket["Acknowledgement Flag"] = payload.

    pass


    def checkCorrupt(self, byte_data):
        checksum = self.checksum(byte_data)
        if checksum == 0x0000:
            return False
        else: 
            return True




    def carry(self, a, b):
        c = a + b
    

    def checksum(self, pkt):
        checksum = 0
        if len(pkt) %2 != 0:
            pkt += bytes(1)
        for i in range(0, len(pkt), 2):
            word = pkt[i] << 8 | pkt[i+1]
            checksum += word 
            checksum = (checksum & 0xffff) + (checksum >> 16)
        return ~checksum & 0xffff

    '''
        else:
            for i in range(0, len(packet), 2):
                word = packet[i] << 8 | packet[i+1]

                check2 += word

                #c = a + b

                res = (check2 & 0xffff) + (check2 >> 16)

                if (res == 1):
                    check2 += 1

            #check2 = check2 >> 4
            check2 = ~check2

            if(check == 0x0000f):
                return True
            else:
                return False
    '''

        




    # TODO: Complete this function
    # This function implements the SENDING functionality. It should implement retransmit-on-timeout. 
    # Refer to the GBN sender flowchart for details about how this function should be implemented
    def receive_from_application_layer(self, payload):
        if self.next_seq_num < self.window_base + self.window_size:
            pkt = self.make_pkt(False, self.next_seq_num, 0, payload, None)
            header = unpack("!iiH?i", pkt[:15])  
            payload = unpack("!%is"%header[4], pkt[15:])[0].decode() 
            self.unACKed_buffer[self.next_seq_num] =  pkt
            self.simulator.pass_to_network_layer(self.entity, pkt, False)
            if self.window_base + 1 == self.next_seq_num:
                self.simulator.start_timer(self.entity, self.timer_interval)
            self.next_seq_num += 1
            
            
        else:
            self.app_layer_buffer.append(payload)

    


    # TODO: Complete this function
    # This function implements the RECEIVING functionality. This function will be more complex that
    # receive_from_application_layer(), it includes functionality from both the GBN Sender and GBN receiver
    # FSM's (both of these have events that trigger on receive_from_network_layer). You will need to handle 
    # data differently depending on if it is a packet containing data, or if it is an ACK.
    # Refer to the GBN receiver flowchart for details about how to implement responding to data pkts, and
    # refer to the GBN sender flowchart for details about how to implement responidng to ACKs
    def receive_from_network_layer(self, byte_data):
        try:
            header = unpack("!iiH?i", byte_data[:15])

            if self.checkCorrupt(byte_data) == True:
                self.simulator.pass_to_network_layer(self.entity, self.last_ACK_pkt, True)
                return
            
            elif header[3] == False:
                if header[0] == self.expected_seq_number:
                    if header[4] != 0:
                        unpacked_data = unpack("!%is"% header[4], byte_data[15:])[0].decode()
                        self.simulator.pass_to_application_layer(self.entity, unpacked_data)
                    
                        ack_packet = self.make_pkt(True, 0, self.expected_seq_number)
                        self.simulator.pass_to_network_layer(self.entity, ack_packet, True)

                        self.last_ACK_pkt = ack_packet
                        self.expected_seq_number += 1
                else:
                    self.simulator.pass_to_network_layer(self.entity, self.last_ACK_pkt, True)    
            else:
                if self.window_base < header[1]:
                    if header[1] > self.window_base:
                        for i in range (self.window_base, header[1] + 1):
                            if i in self.unACKed_buffer:
                                self.simulator.stop_timer(self.entity)
                                self.unACKed_buffer.pop(i)
                        
                    self.window_base = header[1]
                    self.simulator.stop_timer(self.entity)

                    if self.window_base + 1 != self.next_seq_num:
                        self.simulator.start_timer(self.entity, self.timer_interval)

                    while (len(self.app_layer_buffer) > 0 and self.next_seq_num < self.window_base + self.window_size):
                        payload = self.app_layer_buffer.pop()
                        self.unACKed_buffer[self.next_seq_num] = self.make_pkt(False, self.next_seq_num, 0, payload)
                        self.simulator.pass_to_network_layer(self.entity, self.unACKed_buffer[self.next_seq_num], False)
                        
                        if(self.window_base == self.next_seq_num):
                            self.simulator.start_timer(self.entity, self.timer_interval)

                        self.next_seq_num += 1
                else:
                    return
        except:
            pass
    


    # TODO: Complete this function
    # This function is called by the simulator when a timer interrupt is triggered due to an ACK not being 
    # received in the expected time frame. All unACKed data should be resent, and the timer restarted
    def timer_interrupt(self):
        self.simulator.start_timer(self.entity, self.timer_interval)      
        for packet in self.unACKed_buffer.values():
            self.simulator.pass_to_network_layer(self.entity, packet)
        pass