import time
import Queue
import threading

class ProcessingThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.data = None
        self.command = None
        self.cont = True
    def run(self):
        while self.cont:
            try:
                self.command, self.data = self.queue.get(timeout=0.01)
            except Queue.Empty:
                self.command = self.timeout
                self.data = None

            self.command()

    def timeout(self):
        time.sleep(0.01)

    def playMovie(self):
        self.data.threadWait()

    def stop(self):
        self.cont = False



