import time, framebuf, gc

class ST7302(framebuf.FrameBuffer):
    
    FPS0_25 = const(0x00)
    FPS0_5  = const(0x01)
    FPS1    = const(0x02)
    FPS2    = const(0x03)
    FPS4    = const(0x04)
    FPS8    = const(0x05)

    def __init__(self, spi, cs, dc, rst, fps=FPS8, init=True):
        self.spi = spi
        self.rest_pin = rst
        self.dc_pin = dc
        self.cs_pin = cs
        self.cs_pin.init(self.cs_pin.OUT, value=1)
        self.dc_pin.init(self.dc_pin.OUT)
        self.rest_pin.init(self.rest_pin.OUT)
        self.fps = fps
        self.buffer  = bytearray(4125)
        self.out_buf = bytearray(4125)
        super().__init__(self.buffer, 250, 122, framebuf.MONO_HLSB)
        self.pinlock(False)
        if init: self.init()
        
    def invert(self, val=True):
        self.command(0x21 if val else 0x20)
        time.sleep_ms(100)
        
    def pinlock(self, enabled):
        self.rest_pin.init(hold=enabled)
        self.dc_pin.init(hold=enabled)
        self.cs_pin.init(hold=enabled)
        
    def sleep(self):
        self.command(0x10)
        time.sleep_ms(10)
        self.pinlock(True)
        
    def wake(self):
        self.pinlock(False)
        self.command(0x11)
        time.sleep_ms(10)
    
    def reset(self):
        self.rest_pin.value(0)
        time.sleep_ms(200)
        self.rest_pin.value(1)
    
    def clear(self):
        self.fill(0)
        self.draw()
        
    @micropython.native
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
        for col in range(125):
            blk = 0
            byt_msk = (col*2) // 8
            bit_msk = 7 - (col*2) % 8
            for l in range(col*33, col*33+32, 1):
                buf = 0
                buf = buf | (0b10000000 if int(self.buffer[byt_msk +  blk])     & (1 <<  bit_msk  )  else 0)
                buf = buf | (0b01000000 if int(self.buffer[byt_msk +  blk])     & (1 << (bit_msk-1)) else 0)           
                buf = buf | (0b00100000 if int(self.buffer[byt_msk + (blk+32)]) & (1 <<  bit_msk  )  else 0)
                buf = buf | (0b00010000 if int(self.buffer[byt_msk + (blk+32)]) & (1 << (bit_msk-1)) else 0)
                buf = buf | (0b00001000 if int(self.buffer[byt_msk + (blk+64)]) & (1 <<  bit_msk  )  else 0)
                buf = buf | (0b00000100 if int(self.buffer[byt_msk + (blk+64)]) & (1 << (bit_msk-1)) else 0)
                buf = buf | (0b00000010 if int(self.buffer[byt_msk + (blk+96)]) & (1 <<  bit_msk  )  else 0)
                buf = buf | (0b00000001 if int(self.buffer[byt_msk + (blk+96)]) & (1 << (bit_msk-1)) else 0)
                self.out_buf[l] = buf
                blk += 128 
        self.command(0x2c, self.out_buf)
        gc.collect()

    def init(self):
        self.reset()
        self.command(0x38)
        self.command(0xeb, b'\x02')
        self.command(0xd7, b'\x68')
        self.command(0xd1, b'\x01')
        self.command(0xc0, b'\x80')
        self.command(0xc1, b'\x28\x28\x28\x28\x14\x00')
        self.command(0xc2, b'\x00\x00\x00\x00')
        self.command(0xcb, b'\x14')
        self.command(0xb4, b'\xe5\x77\xf1\xff\xff\x4f\xf1\xff\xff\x4f')
        self.command(0xb0, b'\x64')
        self.command(0xb2, bytearray([0x00,self.fps]))
        self.command(0x11)
        time.sleep_ms(10)
        self.command(0xc7, b'\xa6\xe9')
        self.command(0x34)
        self.command(0x36, b'\x00')
        self.command(0x3a, b'\x11')
        self.command(0xb9, b'\x23')
        self.command(0xb8, b'\x09')
        self.command(0xd0, b'\x1f')
        self.command(0x29)
        self.command(0xb9, b'\xe3')
        time.sleep_ms(100)
        self.command(0xb9, b'\x23')
        self.command(0x72, b'\x00')
        self.command(0x39)
        self.command(0x19, b'\x23')
        self.command(0x2a, b'\x19\x23')
        self.command(0x2b, b'\x00\x7c')
        self.command(0xb3, b'\x94')
        self.clear()
