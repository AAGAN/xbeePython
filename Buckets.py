import struct
import random
import time

class Buckets:

    adcValue = 0.0
    weightValue = 0.0
    tareValue=0.0
    valveState = "halfOpen"

    def __init__(self, num = 0, addr64 = '\x00\x00\x00\x00\x00\x00\x00\x00', addr16 = '\xFF\xFE', cor1 = 1, cor2 = 0, color = 'red', xbee = None):
        self.number = num
        self.address16 = addr16
        self.address64 = addr64
        self.corr1 = cor1
        self.corr2 = cor2
        self.ledColor = color
        self.xbee = xbee
        print "Bucket initiated"
        print ":".join("{:02x}".format(ord(c)) for c in self.address64)

    def addressPrint(self, addresss):
        print ":".join("{:02x}".format(ord(c)) for c in addresss)

    def __str__():
        print "Object for bucket %d" % self.number

    def openValve(self, xbee):
        #function to be called to open the ball valve
        self.xbee.send("tx", dest_addr_long=self.address64,dest_addr=self.address16,data='\x6F')
        self.valveState = "open"

    def closeValve(self, xbee):
        #function to be called to close the ball valve
        self.xbee.send("tx", dest_addr_long=self.address64,dest_addr=self.address16,data='\x63')
        self.valveState = "close"

    def displayColor(self, xbee, color):
        #function to set the color of the bucket based on the data and turn the led on with that color
        setColor(color)
        self.xbee.send("tx", dest_addr_long=self.address64,dest_addr=self.address16,data=self.ledColor)

    def turnLEDon(self, color):
        #method to set the color of the 
        if color == 'red':
            self.ledColor = '\x6E\x30'
        elif color == 'green':
            self.ledColor = '\x6E\x31'
        elif color == 'blue':
            self.ledColor = '\x6E\x32'
        else:
            self.ledColor = '\x6E\x33'

    def setColor(self, adcValue):
        pass

    def requestAddr16(self):
        pass

    def requestSensorData(self, xbee):
        frameID = chr(random.randint(0,255))
        xbee.send("tx", frame_id=frameID, dest_addr_long=self.address64, dest_addr=self.address16, data='\x73')
        response = xbee.wait_read_frame()
        #print response
        if response['id']=='tx_status':
            if response['frame_id']==frameID and response['deliver_status']=='\x00':
                pass
                #print "request successfully received!\n"
                #print "Delivery Status:" + str(hex(ord(response['deliver_status'])))
            else:
                print "requestSensorData not received!"
                print "Delivery Status:" + str(hex(ord(response['deliver_status'])))
        
    def readSensor(self, xbee):
        self.requestSensorData(xbee)
        ID = ' '
        while ID != 'rx':
            try:
                response = xbee.wait_read_frame()
                ID = response['id']
                if ID=='rx':
                    if response['source_addr_long']==self.address64:
                        Response = response['rf_data'] 
                        #print response['id']+response['source_addr_long']+' '+response['rf_data']
                        self.adcValue = float(struct.unpack('H',Response)[0])
                else:
                    print response
                    pass
            except KeyboardInterrupt:
                break
    

    def tare(self, xbee):
        print "taring, wait..."
        temp = 0.0
        for i in range(1,11):
            self.readSensor(xbee)
            temp += self.adcValue
            time.sleep(2)
        self.tareValue = temp / 10.0
        print "done!"

    def requestValveState(self,xbee):
        frameID = chr(random.randint(0,255))
        xbee.send("tx", frame_id = frameID, dest_addr_long=self.address64,dest_addr=self.address16, data='\x76')
        ID = ' '
        while ID != 'rx':
            try:
                response = xbee.wait_read_frame()
                ID = response['id']
                if ID == 'rx':  
                    if response['source_addr_long'] == self.address64:
                        Response = response['rf_data'] 
                        Response = float(struct.unpack('H',Response)[0])
                        #print Response
                        if Response == 0:
                            self.valveState = "open"
                        elif Response == 1:
                            self.valveState = "close"
                        elif Response == 2:
                            self.valveState = "halfOpen"
                    else:
                        print "-------Error---------"
                        print ID
                        self.addressPrint(response['source_addr_long'])
                        print response['frame_id']
            except KeyboardInterrupt:
                break
        pass

