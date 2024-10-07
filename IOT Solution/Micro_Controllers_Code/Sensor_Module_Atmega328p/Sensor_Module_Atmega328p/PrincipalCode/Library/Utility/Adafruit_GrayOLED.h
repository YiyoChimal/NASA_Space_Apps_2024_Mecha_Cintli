/*
 * Adafruit_GrayOLED.h
 *
 * Created: 06/10/2024 09:26:33 p. m.
 *  Author: Francisco Rios
 */ 

#ifndef _Adafruit_GRAYOLED_H_
#define _Adafruit_GRAYOLED_H_

// Not for ATtiny, at all
#if !defined(__AVR_ATtiny85__) && !defined(__AVR_ATtiny84__)

#include <Adafruit_GFX.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_SPIDevice.h>
#include <SPI.h>
#include <Wire.h>

#define GRAYOLED_SETCONTRAST 0x81   ///< Generic contrast for almost all OLEDs
#define GRAYOLED_NORMALDISPLAY 0xA6 ///< Generic non-invert for almost all OLEDs
#define GRAYOLED_INVERTDISPLAY 0xA7 ///< Generic invert for almost all OLEDs

#define MONOOLED_BLACK 0   ///< Default black 'color' for monochrome OLEDS
#define MONOOLED_WHITE 1   ///< Default white 'color' for monochrome OLEDS
#define MONOOLED_INVERSE 2 ///< Default inversion command for monochrome OLEDS

/*!
    @brief  Class that stores state and functions for interacting with
            generic grayscale OLED displays.
*/
class Adafruit_GrayOLED : public Adafruit_GFX {
public:
  Adafruit_GrayOLED(uint8_t bpp, uint16_t w, uint16_t h, TwoWire *twi = &Wire,
                    int8_t rst_pin = -1, uint32_t preclk = 400000,
                    uint32_t postclk = 100000);
  Adafruit_GrayOLED(uint8_t bpp, uint16_t w, uint16_t h, int8_t mosi_pin,
                    int8_t sclk_pin, int8_t dc_pin, int8_t rst_pin,
                    int8_t cs_pin);
  Adafruit_GrayOLED(uint8_t bpp, uint16_t w, uint16_t h, SPIClass *spi,
                    int8_t dc_pin, int8_t rst_pin, int8_t cs_pin,
                    uint32_t bitrate = 8000000UL);

  ~Adafruit_GrayOLED(void);

  /**
   @brief The function that sub-classes define that writes out the buffer to
   the display over I2C or SPI
   **/
  virtual void display(void) = 0;
  void clearDisplay(void);
  void invertDisplay(bool i);
  void setContrast(uint8_t contrastlevel);
  void drawPixel(int16_t x, int16_t y, uint16_t color);
  bool getPixel(int16_t x, int16_t y);
  uint8_t *getBuffer(void);

  void oled_command(uint8_t c);
  bool oled_commandList(const uint8_t *c, uint8_t n);

protected:
  bool _init(uint8_t i2caddr = 0x3C, bool reset = true);

  Adafruit_SPIDevice *spi_dev = NULL; ///< The SPI interface BusIO device
  Adafruit_I2CDevice *i2c_dev = NULL; ///< The I2C interface BusIO device
  int32_t i2c_preclk = 400000,        ///< Configurable 'high speed' I2C rate
      i2c_postclk = 100000;           ///< Configurable 'low speed' I2C rate
  uint8_t *buffer = NULL; ///< Internal 1:1 framebuffer of display mem

  int16_t window_x1, ///< Dirty tracking window minimum x
      window_y1,     ///< Dirty tracking window minimum y
      window_x2,     ///< Dirty tracking window maximum x
      window_y2;     ///< Dirty tracking window maximum y

  int dcPin,  ///< The Arduino pin connected to D/C (for SPI)
      csPin,  ///< The Arduino pin connected to CS (for SPI)
      rstPin; ///< The Arduino pin connected to reset (-1 if unused)

  uint8_t _bpp = 1; ///< Bits per pixel color for this display
private:
  TwoWire *_theWire = NULL; ///< The underlying hardware I2C
};

#endif // end __AVR_ATtiny85__ __AVR_ATtiny84__
#endif // _Adafruit_GrayOLED_H_