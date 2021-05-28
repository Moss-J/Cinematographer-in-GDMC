import threading
# import time
import mss
import win32gui
import numpy
import cv2

prvs_flag = False
next_flag = False


def init_flags():
    global prvs_flag, next_flag
    prvs_flag = False
    next_flag = False


def set_prvs_flag(b):
    global prvs_flag
    prvs_flag = b


def set_next_flag(b):
    global next_flag
    next_flag = b


class WindowCapturer(threading.Thread):
    def __init__(self, thread_id, name, window_name):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        hwnd = win32gui.FindWindow(None, window_name)
        # win32gui.SetForegroundWindow(hwnd)
        dimensions = win32gui.GetWindowRect(hwnd)
        print('dimensions:')
        print(dimensions)
        self.w = 720
        self.h = 480
        # Part of the screen to capture
        self.monitor = {'top': dimensions[1] + 31, 'left': dimensions[0] + 8, 'width': self.w, 'height': self.h}
        self.img = None
        self._running = True
        self.monitor_flag = False
        self.prvs_frame = None
        self.next_frame = None
        self.flow_frames = None
        self.flows_bgr = None

    def get_frame_bgr(self):
        frames = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)
        frames = [frames[:, 0:self.w // 3], frames[:, self.w // 3:2 * self.w // 3], frames[:, 2 * self.w // 3:self.w]]
        return frames

    # def get_one_frame(self):
    def get_flows(self):
        hsv = numpy.zeros_like(self.prvs_frame)
        hsv[..., 1] = 255
        prvs = cv2.cvtColor(self.prvs_frame, cv2.COLOR_BGR2GRAY)
        next = cv2.cvtColor(self.next_frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        hsv[..., 0] = ang * 180 / numpy.pi / 2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        self.flows_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        self.flow_frames = [mag[:, 0:self.w // 3], mag[:, self.w // 3:2 * self.w // 3], mag[:, 2 * self.w // 3:self.w]]

    def stop(self):
        self._running = False

    def run(self):
        global prvs_flag, next_flag
        print("start：" + self.name)
        with mss.mss() as sct:
            while self._running:
                self.img = numpy.array(sct.grab(self.monitor))
                if prvs_flag:
                    self.prvs_frame = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)
                    # print('captured prvs frame')
                    prvs_flag = False
                if next_flag:
                    self.next_frame = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)
                    # print('captured next frame')
                    next_flag = False
                    # print('caculating flow_frames')
                    self.get_flows()
                # last_time = time.time()
                # Get raw pixels from the screen, save it to a Numpy array
                # Display the picture
                # cv2.imshow("OpenCV/Numpy normal", self.img)
                if self.monitor_flag:
                    frames = self.get_frame_bgr()
                    cv2.imshow('frame_bgr 0', frames[0])
                    cv2.imshow('frame_bgr 1', frames[1])
                    cv2.imshow('frame_bgr 2', frames[2])
                    if self.prvs_frame is not None:
                        cv2.imshow('prvs_frame', self.prvs_frame)
                    if self.next_frame is not None:
                        cv2.imshow('next_frame', self.next_frame)
                    if self.flows_bgr is not None:
                        cv2.imshow('flows_bgr', self.flows_bgr)
                    # Display the picture in grayscale
                    # cv2.imshow('OpenCV/Numpy grayscale',
                    #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

                    # print("fps: {}".format(1 / (time.time() - last_time)))

                    # Press "q" to quit
                    if cv2.waitKey(25) & 0xFF == ord("q"):
                        cv2.destroyAllWindows()
                        break

        print("stop：" + self.name)
# sr = WindowCapturer(0, 'sr', 'Minecraft 1.12.2')
# sr.start()
