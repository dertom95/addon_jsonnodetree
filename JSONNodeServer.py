import time
import zmq
import rx
import rxUtils

from rx import Observable
from rx.concurrency import ThreadPoolScheduler
from threading import current_thread
import multiprocessing, time, random

optimal_thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

def mapper(val):
    time.sleep(10)
    return val;

def zmqserver(val):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        #  Wait for next request from client
        print("Start server on tcp://*:5555 Thread:"+current_thread().name); 

        message = socket.recv()
        print("Received reply %s [ %s ]" % (request, message))
        #  Do some 'work'
        time.sleep(1)
        socket.send(b"World")

def startServer():
    rxUtils.addDisposable(rx.Observable.from_([1],pool_scheduler).map(zmqserver). subscribe(lambda val: print("VALUE:"+str(val)+" "+current_thread().name)))