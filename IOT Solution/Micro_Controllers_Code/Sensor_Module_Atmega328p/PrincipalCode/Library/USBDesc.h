/*
 * USBDesc.h
 *
 * Created: 06/10/2024 02:08:55 p. m.
 *  Author: Francisco Rios
 */ 

#define PLUGGABLE_USB_ENABLED

#if defined(EPRST6)
#define USB_ENDPOINTS 7 // AtMegaxxU4
#else
#define USB_ENDPOINTS 5 // AtMegaxxU2
#endif

#define ISERIAL_MAX_LEN     20

// Uncomment the following line or pass -DCDC_DISABLED to the compiler
// to disable CDC (serial console via USB).
// That's useful if you want to create an USB device (like an USB Boot Keyboard)
// that works even with problematic devices (like KVM switches).
// Keep in mind that with this change you'll have to use the Arduino's
// reset button to be able to flash it.
//#define CDC_DISABLED

#ifndef CDC_DISABLED
#define CDC_ENABLED
#endif

#ifdef CDC_ENABLED
#define CDC_INTERFACE_COUNT	2
#define CDC_ENPOINT_COUNT	3
#else // CDC_DISABLED
#define CDC_INTERFACE_COUNT	0
#define CDC_ENPOINT_COUNT	0
#endif

#define CDC_ACM_INTERFACE	0	// CDC ACM
#define CDC_DATA_INTERFACE	1	// CDC Data
#define CDC_FIRST_ENDPOINT	1
#define CDC_ENDPOINT_ACM	(CDC_FIRST_ENDPOINT)							// CDC First
#define CDC_ENDPOINT_OUT	(CDC_FIRST_ENDPOINT+1)
#define CDC_ENDPOINT_IN		(CDC_FIRST_ENDPOINT+2)

#define INTERFACE_COUNT		(MSC_INTERFACE + MSC_INTERFACE_COUNT)

#define CDC_RX CDC_ENDPOINT_OUT
#define CDC_TX CDC_ENDPOINT_IN

#define IMANUFACTURER   1
#define IPRODUCT        2
#define ISERIAL         3