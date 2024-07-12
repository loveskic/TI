import time
import sensor
import math
import image
import ustruct
from pyb import UART
import pyb


uart = UART(3, 115200, timeout_char=200)
uart.init(115200, bits=8, parity=None, stop=1)  # init with given parameters

threshold_index = 0                             # 0 for red, 1 for green, 2 for blue
thresholds = [
      # generic_red_thresholds
    (38, 52, 22, 47, -4, 20),  # generic_green_thresholds

]
cx=0
cy=0
cw=0
ch=0
# time4 freq=5Hz 一秒发五个数据
tim=pyb.Timer(4,freq=10)

def send_data(x,y,w,h):
    global uart;
    FH = bytearray([0xb3,0xb3])     # 帧头
    uart.write(FH)                  # 写到串口

    uart.write(str(x))
    uart.write(bytearray([0x20]))   # 发送空格
    uart.write(str(y))
    uart.write(bytearray([0x20]))
    uart.write(str(w))
    uart.write(bytearray([0x20]))
    uart.write(str(h))

    uart.write(bytearray([0x20]))
    FH = bytearray([0x0d,0x0a])     # 帧尾,换行和回车的ascll
    uart.write(FH)
# 中断服务函数
def tim_callback():
    send_data(cx,cy,cw,ch)

# 中断回调函数
tim.callback(tim_callback())


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)# QVGA的中心坐标：160,120
sensor.skip_frames(time=2000)    # 跳过2000毫秒的帧让相机图像在改变相机设置后稳定下来
sensor.set_auto_gain(False)      # 必须关闭才能进行颜色跟踪
sensor.set_auto_whitebal(False)  # 必须关闭才能进行颜色跟踪
clock = time.clock()

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob.pixels() > max_size:
            max_blob = blob
            max_size = blob.pixels()
    return max_blob






while True:
    clock.tick()
    img = sensor.snapshot()
    blobs = img.find_blobs([thresholds[threshold_index]],merge=True)

    #如果找到了目标颜色
    for blob in blobs:
#    if blobs:
#        max_blob = find_max(blobs)
#        cx=max_blob[5]
#        cy=max_blob[6]
#        cw=max_blob[2]
#        ch=max_blob[3]
        cx=blob[5]
        cy=blob[6]
        cw=blob[2]
        ch=blob[3]

        # 这些值取决于max_blob不是圆形的，否则它们将不稳定.
        # 检查max_blob是否显著偏离圆形
#        if max_blob.elongation() > 0.5:
#            img.draw_edges(max_blob.min_corners(), color=(255, 0, 0))
#            img.draw_line(max_blob.major_axis_line(), color=(0, 255, 0))
#            img.draw_line(max_blob.minor_axis_line(), color=(0, 0, 255))

#        # 这些值始终是稳定的。
#        # img.draw_rectangle(max_blob.rect())
        img.draw_rectangle(160,120,35,35)
        img.draw_cross(cx, cy)

        # 注意-max_blob旋转仅限于0-180。
        img.draw_keypoints(
            [(cx, cy, int(math.degrees(blob.rotation())))], size=20
        )

        send_data(cx,cy,cw,ch)      # 发送数据

        print(cx,cy,cw,ch)
        print(clock.fps())
