from pyroute2 import IPDB
import time
from urllib2 import urlopen
import time
import requests
import eventlet

#eventlet.monkey_patch()


class Sender(object):
    def __init__(self):
        self.ip_collection = None
        self.ip = IPDB()
        pass

    def send(self):
        #print "sending ip"
        key = 'ravem-drone'
        url = 'http://manodarbai.eu/drone/set.php?key={}&pip={}&ip={}'.format(key, self.ip_collection[0],
                                                                              self.ip_collection[1])
        urlopen(url)

    def is_connected(self):
        try:
            state = self.ip.interfaces.wlp2s0.ipaddr[0]["address"]
            #print "Private ip is", state
            return [True, state]
        except:
            #print "Wifi is not connected..."
            return [False, None]

    def check_public_ip(self):
        try:
            my_ip = urlopen('http://ip.42.pl/raw').read()
            return my_ip
        except:
            #print "Can't fetch public ip"
            return None

    def ip_change(self):
        while True:
            time.sleep(3)
            inner_ip = self.is_connected()
            if inner_ip[0]:
                ip_temp = self.check_public_ip()
                if not ip_temp == None:
                    #print "Returning ip"
                    return [ip_temp, inner_ip[1]]

    def run(self):
        self.ip_collection = self.ip_change()
        self.send()
        print "IP SENT", self.ip_collection[0], self.ip_collection[1]
        counter = 0
        while True:
            if not self.is_connected()[0]:
                self.ip_collection = self.ip_change()
                ##print "public ip:", self.ip_collection[0]
                self.send()
            counter += 1
            if counter == 2:
                counter = 0
                temp_ip = self.ip_change()
                if not temp_ip[0] == self.ip_collection[0]:
                    ip_collection = temp_ip
                    self.send()
            time.sleep(5)
