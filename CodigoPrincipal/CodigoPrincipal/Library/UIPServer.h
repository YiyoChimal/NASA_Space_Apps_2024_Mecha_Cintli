/*
 * UIPServer.h
 *
 * Created: 06/10/2024 07:33:22 p. m.
 *  Author: Francisco Rios
 */ 

#ifndef UIPSERVER_H
#define UIPSERVER_H

#include "ethernet_comp.h"
#if defined(ARDUINO)
#if defined(__RFduino__)
#include "Print.h"
#else
#include "Print.h"
#endif
#if defined(__STM32F3__) || (!defined(ARDUINO_ARCH_STM32) && defined(STM32F3)) || defined(__RFduino__)
#include "mbed/Server.h"
#else
#include "Server.h"
#endif
#endif
#if defined(__MBED__)
#include "mbed/Print.h"
#include "mbed/Server.h"
#endif
#include "UIPClient.h"

#if defined(ARDUINO) && (defined(ARDUINO_ARCH_STM32) || !defined(STM32F3)) && !defined(__RFduino__)
class UIPServer : public Server {
	#endif
	#if defined(__MBED__) || (!defined(ARDUINO_ARCH_STM32) && defined(STM32F3)) || defined(__RFduino__)
	class UIPServer : public Print, public Server {
		#endif
		public:
		UIPServer(uint16_t);
		UIPClient available();
		UIPClient accept();
		virtual void begin();
		virtual void begin(uint16_t port);
		void end();
		operator bool();

		virtual size_t write(uint8_t);
		virtual size_t write(const uint8_t *buf, size_t size);

		using Print::write;

		private:
		uint16_t _port;
		bool listening = false;
	};

	#endif