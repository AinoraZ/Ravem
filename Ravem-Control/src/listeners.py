import config
import tools
import time
import threading

class Listen(object):
    def __init__(self, vehicle):
        self.vehicle = vehicle.vehicle
        self.sio = vehicle.sio
        self.loop = False
        self._add_listeners()

    def attitude_listener(self, attribute, name, value):
        obj = {'pitch': value.pitch, 'yaw': value.yaw, 'roll': value.roll,
               'speed': self.vehicle.groundspeed, 'altitude': self.vehicle.location.global_relative_frame.alt}
        self.sio.emit('gyro_info', obj)

    def frame_listener(self, attribute, name, value):
        obj = {'lat': value.lat, 'lng': value.lon, 'alt': value.alt}
        #print obj
        self.sio.emit('location_info', obj)

    def battery_listener(self, attribute, name, value):
        obj = {'voltage': value.voltage, 'level': tools.calculate_battery(value.voltage)}
        #print obj
        self.sio.emit('battery_info', obj)

    def compass_listener(self, attribute, name, value):
        #print value
        self.sio.emit('compass_info', value)

    def arm_listener(self, attribute, name, value):
        self.sio.emit('armed_info', value)

    def mode_listener(self, attribute, name, value):
        self.sio.emit('mode_info', value.name)

    def speed_listener(self, attribute, name, value):
        self.sio.emit('speed_info', {'groundspeed': self.vehicle.groundspeed, 'airspeed': value})

    def velocity_listener(self, attribute, name, value):
        self.sio.emit('velocity_info', {'x': value[0], 'y': value[1], 'z': value[2]})

    def initial_send(self):
        attitude = self.vehicle.attitude
        obj = {'pitch': attitude.pitch, 'yaw': attitude.yaw, 'roll': attitude.roll,
               'speed': self.vehicle.groundspeed, 'altitude': self.vehicle.location.global_relative_frame.alt}
        self.sio.emit('gyro_info', obj)

        location = self.vehicle.location.global_relative_frame
        obj = {'lat': location.lat, 'lng': location.lon, 'alt': location.alt}
        self.sio.emit('location_info', obj)

        battery = self.vehicle.battery
        obj = {'voltage': battery.voltage, 'level': tools.calculate_battery(battery.voltage)}
        self.sio.emit('battery_info', obj)

        self.sio.emit('compass_info', self.vehicle.heading)
        self.sio.emit('armed_info', self.vehicle.armed)
        self.sio.emit('mode_info', self.vehicle.mode.name)
        self.sio.emit('speed_info', {'groundspeed': self.vehicle.groundspeed, 'airspeed': self.vehicle.airspeed})

        vel = self.vehicle.velocity
        self.sio.emit('velocity_info', {'x': vel[0], 'y': vel[1], 'z': vel[2]})

    def listen_all(self):
        while self.loop:
            attitude = self.vehicle.attitude
            obj = {'pitch': attitude.pitch, 'yaw': attitude.yaw, 'roll': attitude.roll,
                   'speed': self.vehicle.groundspeed, 'altitude': self.vehicle.location.global_relative_frame.alt}
            self.sio.emit('gyro_info', obj)

            location = self.vehicle.location.global_relative_frame
            obj = {'lat': location.lat, 'lng': location.lon, 'alt': location.alt}
            self.sio.emit('location_info', obj)

            battery = self.vehicle.battery
            obj = {'voltage': battery.voltage, 'level': tools.calculate_battery(battery.voltage)}
            self.sio.emit('battery_info', obj)

            self.sio.emit('compass_info', self.vehicle.heading)
            self.sio.emit('armed_info', self.vehicle.armed)
            self.sio.emit('mode_info', self.vehicle.mode.name)
            self.sio.emit('speed_info', {'groundspeed': self.vehicle.groundspeed, 'airspeed': self.vehicle.airspeed})

            vel = self.vehicle.velocity
            self.sio.emit('velocity_info', {'x': vel[0], 'y': vel[1], 'z': vel[2]})

            time.sleep(0.5)

    def listen_onesock(self):
        while self.loop:
            # print "sending..."
            attitude = self.vehicle.attitude
            location = self.vehicle.location.global_relative_frame
            battery = self.vehicle.battery
            vel = self.vehicle.velocity

            all_obj = {'pitch': attitude.pitch, 'yaw': attitude.yaw, 'roll': attitude.roll,
                       'lat': location.lat, 'lng': location.lon, 'alt': location.alt,
                       'voltage': battery.voltage, 'level': tools.calculate_battery(battery.voltage),
                       'x': vel[0], 'y': vel[1], 'z': vel[2],
                       'groundspeed': self.vehicle.groundspeed, 'airspeed': self.vehicle.airspeed,
                       'armed': self.vehicle.armed, 'compass': self.vehicle.heading, 'mode': self.vehicle.mode.name}

            self.sio.emit('all_info', all_obj)
            time.sleep(0.1)

        # self.sio.emit('compass_info', self.vehicle.heading)
        # self.sio.emit('armed_info', self.vehicle.armed)
        # self.sio.emit('mode_info', self.vehicle.mode.name)

    def _add_listeners(self):
        self.loop = True
        t = threading.Thread(target=self.listen_onesock)
        t.daemon = True
        t.start()
        # self.vehicle.add_attribute_listener('attitude', self.attitude_listener)
        # self.vehicle.add_attribute_listener('location.global_relative_frame', self.frame_listener)
        # self.vehicle.add_attribute_listener('battery', self.battery_listener)
        # self.vehicle.add_attribute_listener('heading', self.compass_listener)
        # self.vehicle.add_attribute_listener('armed', self.arm_listener)
        # self.vehicle.add_attribute_listener('mode', self.mode_listener)
        # self.vehicle.add_attribute_listener('airspeed', self.speed_listener)
        # self.vehicle.add_attribute_listener('velocity', self.velocity_listener)

    def _remove_listeners(self):
        # obj = {'pitch': 0, 'yaw': 0, 'roll': 0}
        # self.sio.emit('gyro', obj)

        self.loop = False

        # self.vehicle.remove_attribute_listener('attitude', self.attitude_listener)
        # self.vehicle.remove_attribute_listener('location.global_relative_frame', self.frame_listener)
        # self.vehicle.remove_attribute_listener('battery', self.battery_listener)
        # self.vehicle.remove_attribute_listener('heading', self.compass_listener)
        # self.vehicle.remove_attribute_listener('armed', self.arm_listener)
        # self.vehicle.remove_attribute_listener('mode', self.mode_listener)
        # self.vehicle.remove_attribute_listener('airspeed', self.speed_listener)
        # self.vehicle.add_attribute_listener('velocity', self.velocity_listener)
