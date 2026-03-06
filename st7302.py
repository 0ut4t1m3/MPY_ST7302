import time, framebuf, gc
from machine import Pin

class ST7302(framebuf.FrameBuffer):

    FPS0_25 = const(0x00)
    FPS0_5  = const(0x01)
    FPS1    = const(0x02)
    FPS2    = const(0x03)
    FPS4    = const(0x04)
    FPS8    = const(0x05)

    def __init__(self, spi, cs, dc, rst, fps=FPS8, init=True):
        self.spi = spi
        self.rest_pin = Pin(rst, Pin.OUT)
        self.dc_pin = Pin(dc, Pin.OUT)
        self.cs_pin = Pin(cs, Pin.OUT, value=1)
        self.fps = fps
        self.buffer  = bytearray(4125)
        self.out_buf = bytearray(4125)
        super().__init__(self.buffer, 250, 122, framebuf.MONO_HLSB)
        if init: self.init()
        
    def invert(self, val=True):
        self.command(0x21 if val else 0x20)
        time.sleep_ms(100)
        
    def sleep(self):
        self.command(0x10)
        time.sleep_ms(10)
        
    def wake(self):
        self.command(0x11)
        time.sleep_ms(10)
    
    def reset(self):
        self.rest_pin.value(0)
        time.sleep_ms(200)
        self.rest_pin.value(1)
    
    def clear(self):
        self.fill(0)
        self.draw()
    
    def command(self, command, data=None):
        self.cs_pin.value(0)
        self.dc_pin.value(0)
        self.spi.write(bytearray([command]))
        if data is not None:
            self.dc_pin.value(1)
            self.spi.write(data)
        self.cs_pin.value(1)
    
    @micropython.viper
    def draw(self):
        src = ptr8(self.buffer)
        dst = ptr8(self.out_buf)
        for col in range(125):
            blk = 0
            byt_msk = (col*2) // 8
            bit_msk = 7 - (col*2) % 8
            mask_a = 1 <<  bit_msk
            mask_b = 1 << (bit_msk-1)
            for l in range(col*33, col*33+32, 1):
                b0 = src[byt_msk +  blk]
                b1 = src[byt_msk + (blk+32)]
                b2 = src[byt_msk + (blk+64)]
                b3 = src[byt_msk + (blk+96)]
                res = 0
                if b0 & mask_a: res |= 0x80
                if b0 & mask_b: res |= 0x40
                if b1 & mask_a: res |= 0x20
                if b1 & mask_b: res |= 0x10
                if b2 & mask_a: res |= 0x08
                if b2 & mask_b: res |= 0x04
                if b3 & mask_a: res |= 0x02
                if b3 & mask_b: res |= 0x01
                dst[l] = res
                blk += 128 
        self.command(0x2c, self.out_buf)

    def init(self):
        self.reset()
        self.command(0xeb, b'\x02') #NV Load Enable
        self.command(0xd7, b'\x68') #NV Load Ctrl
        self.command(0xd1, b'\x01') #Booster Enable
        self.command(0xc0, b'\x80') #Gate Control
        self.command(0xc1, b'\x28\x28\x28\x28\x14\x00') #Source High Voltage Control
        self.command(0xc2, b'\x00\x00\x00\x00') #Source Low Voltage Control
        self.command(0xcb, b'\x14') #VCOMH Control
        self.command(0xb4, b'\xe5\x77\xf1\xff\xff\x4f\xf1\xff\xff\x4f') #Update Period Gate EQ Control
        self.command(0xb0, b'\x64') #Duty Setting
        self.command(0x39) #Low power mode
        self.command(0xb2, bytearray([0x00,self.fps])) #FR Control
        self.command(0x11) #Sleep out
        time.sleep_ms(10)
        self.command(0xc7, b'\xa6\xe9') #OSC Enable
        self.command(0x34) #Tearing effect line off
        self.command(0x36, b'\x00') #Memory data access control
        self.command(0x3a, b'\x11') #Data format select
        self.command(0xb9, b'\x23') #Source Setting
        self.command(0xb8, b'\x09') #Panel Setting
        self.command(0x29) #Display on
        self.command(0x2a, b'\x19\x23') #Column address set
        self.command(0x2b, b'\x00\x7c') #Row address set
        self.command(0xb3, b'\x94') #VCOM EQ Enable
        self.clear()
        