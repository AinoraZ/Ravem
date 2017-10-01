from control import DroneControl
import socketio
import threading
import config
import eventlet.wsgi
import tools
from data_parser import ParseAndWork
import time

if __name__ == '__main__':
    sio = socketio.Server()

    reset_config_data = tools.make_config(False)
    tools.load_config()
    worker = DroneControl(config.DRONE_LOCAL, sio)

    print "Worker initialised"

    @sio.on('connect')
    def connect(sid, environ):
        sio.emit("vehicle_success", worker.success)

    @sio.on("vehicle_connect")
    def vehicle_connect(sid):
        if not worker.success:
            worker.connect(config.DRONE_LOCAL)
            tools.config_settable_init(worker)
        else:
            print "Already connected"
            sio.emit('response', {'data': "Already connected"})

    @sio.on("vehicle_disconnect")
    def vehicle_disconnect(sid):
        worker.disconnect()

    @sio.on('mission')
    def message(sid, data):
        t = threading.Thread(target=ParseAndWork, kwargs={'data': data, 'worker': worker})
        t.daemon = True
        t.start()

    @sio.on('force_land')
    def message(sid):
        t = threading.Thread(target=worker.force_land)
        t.daemon = True
        t.start()

    @sio.on('force_rtl')
    def message(sid):
        t = threading.Thread(target=worker.force_RTL)
        t.daemon = True
        t.start()

    @sio.on('force_loiter')
    def message(sid):
        t = threading.Thread(target=worker.force_loiter)
        t.daemon = True
        t.start()

    @sio.on('clear_missions')
    def message(sid):
        t = threading.Thread(target=worker.clear_missions)
        t.daemon = True
        t.start()

    @sio.on('vehicle_auto')
    def message(sid):
        t = threading.Thread(target=worker.vehicle_auto)
        t.daemon = True
        t.start()

    @sio.on('vehicle_guided')
    def message(sid):
        t = threading.Thread(target=worker.vehicle_guided)
        t.daemon = True
        t.start()

    @sio.on('set_airspeed')
    def message(sid, data):
        t = threading.Thread(target=worker.set_airspeed, kwargs={'air_speed': data})
        t.daemon = True
        t.start()

    @sio.on('arm')
    def message(sid):
        t = threading.Thread(target=worker.arm_direct)
        t.daemon = True
        t.start()

    @sio.on('remove_bad_status')
    def message(sid):
        t = threading.Thread(target=worker.remove_bad_status)
        t.daemon = True
        t.start()

    @sio.on('disarm')
    def message(sid):
        t = threading.Thread(target=worker.disarm)
        t.daemon = True
        t.start()

    @sio.on('get_config')
    def get_config(sid):
        sio.emit('config_response', tools.make_config())

    @sio.on('config_post')
    def config_post(sid, data):
        tools.change_config(data, worker)
        sio.emit('response', {'data': "Config changed"})
        print "Config changed"

    @sio.on('reset_config')
    def reset_config(sid):
        tools.change_config(reset_config_data, worker)
        sio.emit('config_response', tools.make_config())

    @sio.on('set_airspeed')
    def set_airspeed(sid, data):
        worker.set_airspeed(data)
        print "airspeed set to", data

    @sio.on('get_data')
    def get_data(sid):
        if worker.success:
            worker.listen.initial_send()
        else:
            sio.emit('response', {'data': "Drone is not connected!"})

    @sio.on('disconnect')
    def disconnect(sid):
        print('disconnect ', sid)

    app = socketio.Middleware(sio)
    eventlet.wsgi.server(eventlet.listen(('192.168.1.200', 8001)), app)
