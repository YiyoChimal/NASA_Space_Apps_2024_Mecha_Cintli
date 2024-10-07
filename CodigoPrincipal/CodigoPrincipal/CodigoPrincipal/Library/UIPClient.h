/*
 * UIPClient.h
 *
 * Created: 06/10/2024 07:28:22 p. m.
 *  Author: Francisco Rios
 */ 



#ifndef UIPCLIENT_H
#define UIPCLIENT_H

#include "ethernet_comp.h"
#if defined(ARDUINO)
#include "Print.h"
#if defined(__STM32F3__) || (!defined(ARDUINO_ARCH_STM32) && defined(STM32F3)) || defined(__RFduino__)
#include "mbed/Client.h"
#else
#include "Client.h"
#endif
#endif
#if defined(__MBED__)
#include "mbed/Print.h"
#include "mbed/Client.h"
#endif
#include "utility/mempool.h"
#include "utility/logging.h"

extern "C" {
	#include "utility/uip.h"
}

#define UIP_SOCKET_DATALEN UIP_TCP_MSS
//#define UIP_SOCKET_NUMPACKETS UIP_RECEIVE_WINDOW/UIP_TCP_MSS+1
#ifndef UIP_SOCKET_NUMPACKETS
#define UIP_SOCKET_NUMPACKETS 5
#endif

#define UIP_CLIENT_CONNECTED 0x01
#define UIP_CLIENT_CLOSE 0x02
#define UIP_CLIENT_REMOTECLOSED 0x04
#define UIP_CLIENT_RESTART 0x08
#define UIP_CLIENT_ACCEPTED 0x10

typedef uint8_t uip_socket_ptr;

typedef struct {
	uint8_t conn_index;
	uint8_t state;
	memhandle packets_in[UIP_SOCKET_NUMPACKETS];
	uint16_t lport;        /**< The local TCP port, in network byte order. */
} uip_userdata_closed_t;

typedef struct {
	uint8_t conn_index;
	uint8_t state;
	memhandle packets_in[UIP_SOCKET_NUMPACKETS];
	memhandle packets_out[UIP_SOCKET_NUMPACKETS];
	memaddress out_pos;
	#if UIP_CLIENT_TIMER >= 0
	unsigned long timer;
	#endif
} uip_userdata_t;

#if defined(ARDUINO) && (defined(ARDUINO_ARCH_STM32) || !defined(STM32F3)) && !defined(__RFduino__)
class UIPClient : public Client {
	#endif
	#if defined(__MBED__) || (!defined(ARDUINO_ARCH_STM32) && defined(STM32F3)) || defined(__RFduino__)
	class UIPClient : public Print, public Client {
		#endif
		public:
		UIPClient();
		virtual int connect(IPAddress ip, uint16_t port);
		virtual int connect(const char *host, uint16_t port);
		virtual int read(uint8_t *buf, size_t size);
		virtual void stop();
		virtual uint8_t connected();
		virtual operator bool();
		virtual bool operator==(const EthernetClient&);
		virtual bool operator!=(const EthernetClient& rhs) { return !this->operator==(rhs); };

		virtual size_t write(uint8_t);
		virtual size_t write(const uint8_t *buf, size_t size);
		virtual int availableForWrite();

		virtual int available();
		virtual int read();
		virtual int peek();
		virtual void flush();

		using Print::write;

		IPAddress remoteIP();
		uint16_t remotePort();

		private:
		UIPClient(struct uip_conn *_conn);
		UIPClient(uip_userdata_t* conn_data);

		uip_userdata_t* data;

		static uip_userdata_t all_data[UIP_CONNS];
		static uip_userdata_t* _allocateData();

		static uint16_t _write(uip_userdata_t *,const uint8_t *buf, size_t size);
		static int _available(uip_userdata_t *);

		static uint8_t _currentBlock(memhandle* blocks);
		static void _eatBlock(memhandle* blocks);
		static void _flushBlocks(memhandle* blocks);

		#if ACTLOGLEVEL>=LOG_DEBUG_V2
		static void _dumpAllData(void);
		#endif

		friend class UIPEthernetClass;
		friend class UIPServer;

		friend void uipclient_appcall(void);

	};

	#endif