import numpy as np
import cv2
import mss
import pyvirtualcam


def virtual_cam_loop(select_rect, is_running, on_stop):
    print(f"启动虚拟摄像头，区域: {select_rect}")
    with mss.mss() as sct:
        width = select_rect.width()
        height = select_rect.height()
        fps = 20

        try:
            with pyvirtualcam.Camera(width=width, height=height, fps=fps) as cam:
                print(f'虚拟摄像头开启: {cam.device}')
                print(f"虚拟摄像头初始化成功: {width}x{height}@{fps}fps")
                while is_running():
                    monitor = {
                        'top': select_rect.top(),
                        'left': select_rect.left(),
                        'width': width,
                        'height': height
                    }
                    img = np.array(sct.grab(monitor))
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    cam.send(frame)
                    cam.sleep_until_next_frame()
                cam.close()
        except Exception as e:
            print(f"虚拟摄像头错误: {str(e)}")
            on_stop()
            return

    on_stop()