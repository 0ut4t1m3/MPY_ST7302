# MPY_ST7302
## ST7302 driver for Micropython


A small framebuf based display driver for the ST7302. 
I found some cheap "memory LCD" panels on Aliexpress recently, these panels are extremely power effecient and readable in most lighting conditions so make a good replacement for e-paper without the long refresh times.
Due to the insane pixel layout of these displays some remapping of the framebuffer is needed before sending the data to the controller. I've used the viper decorator to get drawing a frame down to 70ms. Only landscape is currently supported.

![image](https://github.com/user-attachments/assets/aa0ddfce-119f-451f-a897-750e555dcf2e)

## Features
- Written in pure Micropython
- Adjustable panel refresh
- Can skip panel init for deepsleep support
- Toggles hold on IO to minimise current during deepsleep
- All normal framebuf methods such as text() and rect() supported

## Requirements
- Requires framebuf so will only work on ports that include it
- Some features might only work on ESP32 (eg. pin hold)

## Usage
```python
from st7302 import ST7302

lcd = ST7302(spi=spibus, cs=machine.Pin(48), dc=machine.Pin(47), rst=machine.Pin(21), fps=ST7302.FPS8, init=True|False)
    #spi = initilised SPI bus
    #cs, dc, rst = Pin objects
    #fps = Sets hardware screen refresh, can be FPS0_25 FPS0_5 FPS1 FPS2 FPS4 FPS8
    #init = Skip init, screen will remain blank if not already initilised

lcd.invert(True|False)
    #Takes effect on next screen refresh

lcd.sleep()
    #Puts screen to sleep and locks IO

lcd.wake()
    #Unlocks IO and resumes screen updates

lcd.pinlock(True|False)
    #Locks/unlocks IO, lock before deepsleeping MCU to minimise current draw.
    #Pins unlock when module is loaded

lcd.clear()
    #wipe framebuffer and push to screen

lcd.text('Hello ST7302', 10, 10, 1)
lcd.rect(10, 25, 40, 40, 1, 0)
lcd.rect(10, 75, 40, 40, 1, 1)
lcd.hline(55, 25, 190, 1)
lcd.ellipse(150, 73, 40, 40, 1, 1)
lcd.ellipse(150, 73, 40, 40, 0, 1, 2)
    #All normal framebuf methods can be used

lcd.draw()
    #send framebuffer to display
```


