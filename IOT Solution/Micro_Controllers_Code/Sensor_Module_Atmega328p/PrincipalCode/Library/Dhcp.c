/*
 * Dhcp.c
 *
 * Created: 06/10/2024 05:03:27 p. m.
 *  Author: Francisco Rios
 */ 
#include <string.h>
#include <stdlib.h>
#include "utility/uipopt.h"
#if UIP_UDP
#include "Dhcp.h"
#if defined(ARDUINO)
  #include <Arduino.h>
#endif
#if defined(__MBED__)
  #include <mbed.h>
  #include "mbed/millis.h"
  #define delay(x) wait_ms(x)
#endif
#include "utility/logging.h"
#include "utility/uip.h"

int DhcpClass::beginWithDHCP(uint8_t *mac)
{
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::beginWithDHCP(uint8_t *mac) DEBUG_V1:Function started"));
    #endif
    _dhcpLeaseTime=0;
    _dhcpT1=0;
    _dhcpT2=0;
    _lastCheck=0;

    // zero out _dhcpMacAddr
    memset(_dhcpMacAddr, 0, 6); 
    reset_DHCP_lease();

    memcpy((void*)_dhcpMacAddr, (void*)mac, 6);
    _dhcp_state = STATE_DHCP_START;
    return request_DHCP_lease();
}

void DhcpClass::reset_DHCP_lease(void){
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::reset_DHCP_lease(void) DEBUG_V1:Function started"));
    #endif
    // zero out _dhcpipv4struct.SubnetMask, _dhcpipv4struct.GatewayIp, _dhcpipv4struct.LocalIp, _dhcpipv4struct.DhcpServerIp, _dhcpipv4struct.DnsServerIp
    memset(&_dhcpipv4struct, 0, sizeof(_dhcpipv4struct));
}

//return:0 on error, 1 if request is sent and response is received
int DhcpClass::request_DHCP_lease(void){
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::request_DHCP_lease(void) DEBUG_V1:Function started"));
    #endif
    
    uint8_t messageType = 0;
  
    
  
    // Pick an initial transaction ID
    #if defined(ARDUINO)
       _dhcpTransactionId = random(1UL, 2000UL);
    #endif
    #if defined(__MBED__)
       _dhcpTransactionId = (rand() % 2000UL) + 1;
    #endif
    _dhcpInitialTransactionId = _dhcpTransactionId;

    _dhcpUdpSocket.stop();
    if (_dhcpUdpSocket.begin(DHCP_CLIENT_PORT) == 0)
    {
      // Couldn't get a socket
      return 0;
    }
    
    presend_DHCP();
    
    int result = 0;
    
    unsigned long startTime = millis();
    
    while(_dhcp_state != STATE_DHCP_LEASED)
    {
        if(_dhcp_state == STATE_DHCP_START)
        {
            #if ACTLOGLEVEL>=LOG_DEBUG_V1
              LogObject.uart_send_strln(F("DhcpClass::request_DHCP_lease(void) DEBUG_V1:dhcp_state=STATE_DHCP_START -> send_DHCP_MESSAGE DHCP_DISCOVER"));
            #endif
            _dhcpTransactionId++;
            
            send_DHCP_MESSAGE(DHCP_DISCOVER, ((millis() - startTime) / 1000));
            _dhcp_state = STATE_DHCP_DISCOVER;
        }
        else if(_dhcp_state == STATE_DHCP_REREQUEST){
            #if ACTLOGLEVEL>=LOG_DEBUG_V1
              LogObject.uart_send_strln(F("DhcpClass::request_DHCP_lease(void) DEBUG_V1:dhcp_state=STATE_DHCP_REREQUEST -> send_DHCP_MESSAGE DHCP_REQUEST"));
            #endif
            _dhcpTransactionId++;
            send_DHCP_MESSAGE(DHCP_REQUEST, ((millis() - startTime)/1000));
            _dhcp_state = STATE_DHCP_REQUEST;
        }
        else if(_dhcp_state == STATE_DHCP_DISCOVER)
        {
            uint32_t respId;
            messageType = parseDHCPResponse(respId);
            if(messageType == DHCP_OFFER)
            {
                #if ACTLOGLEVEL>=LOG_DEBUG_V1
                  LogObject.uart_send_strln(F("DhcpClass::request_DHCP_lease(void) DEBUG_V1:dhcp_state=STATE_DHCP_DISCOVER,messageType=DHCP_OFFER -> send_DHCP_MESSAGE DHCP_REQUEST"));
                #endif
                // We'll use the transaction ID that the offer came with,
                // rather than the one we were up to
                _dhcpTransactionId = respId;
                send_DHCP_MESSAGE(DHCP_REQUEST, ((millis() - startTime) / 1000));
                _dhcp_state = STATE_DHCP_REQUEST;
            }
        }
        else if(_dhcp_state == STATE_DHCP_REQUEST)
        {
            uint32_t respId;
            messageType = parseDHCPResponse(respId);
            if(messageType == DHCP_ACK)
            {
                #if ACTLOGLEVEL>=LOG_DEBUG_V1
                  LogObject.uart_send_strln(F("DhcpClass::request_DHCP_lease(void) DEBUG_V1:dhcp_state=STATE_DHCP_REQUEST,messageType=DHCP_ACK"));
                #endif
                _dhcp_state = STATE_DHCP_LEASED;
                result = 1;
                //use default lease time if we didn't get it
                if(_dhcpLeaseTime == 0){
                    _dhcpLeaseTime = DEFAULT_LEASE;
                }
                //calculate T1 & T2 if we didn't get it
                if(_dhcpT1 == 0){
                    //T1 should be 50% of _dhcpLeaseTime
                    _dhcpT1 = _dhcpLeaseTime >> 1;
                }
                if(_dhcpT2 == 0){
                    //T2 should be 87.5% (7/8ths) of _dhcpLeaseTime
                    _dhcpT2 = _dhcpT1 << 1;
                }
                _renewInSec = _dhcpT1;
                _rebindInSec = _dhcpT2;
            }
            else if(messageType == DHCP_NAK)
                _dhcp_state = STATE_DHCP_START;
        }
        
        if(messageType == 255)
        {
            messageType = 0;
            _dhcp_state = STATE_DHCP_START;
        }
        
        if(result != 1 && ((millis() - startTime) > DHCP_TIMEOUT))
            break;
    #if defined(ESP8266)
       wdt_reset();
    #endif
    }
    
    // We're done with the socket now
    _dhcpUdpSocket.stop();
    _dhcpTransactionId++;

    return result;
}

void DhcpClass::presend_DHCP(void)
{
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::presend_DHCP(void) DEBUG_V1:Function started (Empty function)"));
    #endif
}

void DhcpClass::send_DHCP_MESSAGE(uint8_t messageType, uint16_t secondsElapsed)
{
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::send_DHCP_MESSAGE(uint8_t messageType, uint16_t secondsElapsed) DEBUG_V1:Function started"));
    #endif
    uint8_t buffer[32];
    memset(buffer, 0, 32);
    IPAddress dest_addr( 255, 255, 255, 255 ); // Broadcast address

    if (-1 == _dhcpUdpSocket.beginPacket(dest_addr, DHCP_SERVER_PORT))
    {
        // FIXME Need to return errors
        return;
    }

    buffer[0] = DHCP_BOOTREQUEST;   // op
    buffer[1] = DHCP_HTYPE10MB;     // htype
    buffer[2] = DHCP_HLENETHERNET;  // hlen
    buffer[3] = DHCP_HOPS;          // hops

    // xid
    unsigned long xid = htonl(_dhcpTransactionId);
    memcpy(buffer + 4, &(xid), 4);

    // 8, 9 - seconds elapsed
    buffer[8] = ((secondsElapsed & 0xff00) >> 8);
    buffer[9] = (secondsElapsed & 0x00ff);

    // flags
    unsigned short flags = htons(DHCP_FLAGSBROADCAST);
    memcpy(buffer + 10, &(flags), 2);

    // ciaddr: already zeroed
    // yiaddr: already zeroed
    // siaddr: already zeroed
    // giaddr: already zeroed

    //put data in W5100 transmit buffer
    _dhcpUdpSocket.write(buffer, 28);

    memset(buffer, 0, 32); // clear local buffer

    memcpy(buffer, _dhcpMacAddr, 6); // chaddr

    //put data in W5100 transmit buffer
    _dhcpUdpSocket.write(buffer, 16);

    memset(buffer, 0, 32); // clear local buffer

    // leave zeroed out for sname && file
    // put in W5100 transmit buffer x 6 (192 bytes)
  
    for(int i = 0; i < 6; i++) {
        _dhcpUdpSocket.write(buffer, 32);
    }
  
    // OPT - Magic Cookie
    buffer[0] = (uint8_t)((MAGIC_COOKIE >> 24)& 0xFF);
    buffer[1] = (uint8_t)((MAGIC_COOKIE >> 16)& 0xFF);
    buffer[2] = (uint8_t)((MAGIC_COOKIE >> 8)& 0xFF);
    buffer[3] = (uint8_t)(MAGIC_COOKIE& 0xFF);

    // OPT - message type
    buffer[4] = dhcpMessageType;
    buffer[5] = 0x01;
    buffer[6] = messageType; //DHCP_REQUEST;

    // OPT - client identifier
    buffer[7] = dhcpClientIdentifier;
    buffer[8] = 0x07;
    buffer[9] = 0x01;
    memcpy(buffer + 10, _dhcpMacAddr, 6);

    // OPT - host name
    buffer[16] = hostName;
    buffer[17] = strlen(HOST_NAME) + 6; // length of hostname + last 3 bytes of mac address
    strcpy((char*)&(buffer[18]), HOST_NAME);

    printByte((char*)&(buffer[24]), _dhcpMacAddr[3]);
    printByte((char*)&(buffer[26]), _dhcpMacAddr[4]);
    printByte((char*)&(buffer[28]), _dhcpMacAddr[5]);

    //put data in W5100 transmit buffer
    _dhcpUdpSocket.write(buffer, 30);

    if(messageType == DHCP_REQUEST)
    {
        buffer[0] = dhcpRequestedIPaddr;
        buffer[1] = 0x04;
        buffer[2] = _dhcpipv4struct.LocalIp[0];
        buffer[3] = _dhcpipv4struct.LocalIp[1];
        buffer[4] = _dhcpipv4struct.LocalIp[2];
        buffer[5] = _dhcpipv4struct.LocalIp[3];

        buffer[6] = dhcpServerIdentifier;
        buffer[7] = 0x04;
        buffer[8] = _dhcpipv4struct.DhcpServerIp[0];
        buffer[9] = _dhcpipv4struct.DhcpServerIp[1];
        buffer[10] = _dhcpipv4struct.DhcpServerIp[2];
        buffer[11] = _dhcpipv4struct.DhcpServerIp[3];

        //put data in W5100 transmit buffer
        _dhcpUdpSocket.write(buffer, 12);
    }
    
    buffer[0] = dhcpParamRequest;
    buffer[1] = 0x06;
    buffer[2] = subnetMask;
    buffer[3] = routersOnSubnet;
    buffer[4] = dns;
    buffer[5] = domainName;
    buffer[6] = dhcpT1value;
    buffer[7] = dhcpT2value;
    buffer[8] = endOption;
    
    //put data in W5100 transmit buffer
    _dhcpUdpSocket.write(buffer, 9);

    _dhcpUdpSocket.endPacket();
}

uint8_t DhcpClass::parseDHCPResponse(uint32_t& transactionId)
{
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::parseDHCPResponse(uint32_t& transactionId) DEBUG_V1:Function started"));
    #endif
    uint8_t type = 0;
    uint8_t opt_len = 0;
     
    unsigned long startTime = millis();

    while(_dhcpUdpSocket.parsePacket() <= 0)
    {
        if((millis() - startTime) > DHCP_RESPONSE_TIMEOUT)
        {
            return 255;
        }
        delay(50);
    }
    // start reading in the packet
    RIP_MSG_FIXED fixedMsg;
    _dhcpUdpSocket.read((char*)&fixedMsg, sizeof(RIP_MSG_FIXED));
  
    if(fixedMsg.op == DHCP_BOOTREPLY && _dhcpUdpSocket.remotePort() == DHCP_SERVER_PORT)
    {
        transactionId = ntohl(fixedMsg.xid);
        if(memcmp(fixedMsg.chaddr, _dhcpMacAddr, 6) != 0 || (transactionId < _dhcpInitialTransactionId) || (transactionId > _dhcpTransactionId))
        {
            // Need to read the rest of the packet here regardless
            _dhcpUdpSocket.flush();
            return 0;
        }

        memcpy(_dhcpipv4struct.LocalIp, fixedMsg.yiaddr, 4);

        // Skip to the option part
        // Doing this a byte at a time so we don't have to put a big buffer
        // on the stack (as we don't have lots of memory lying around)
        for (int i =0; i < (240 - (int)sizeof(RIP_MSG_FIXED)); i++)
        {
            _dhcpUdpSocket.read(); // we don't care about the returned byte
        }

        while (_dhcpUdpSocket.available() > 0) 
        {
            switch (_dhcpUdpSocket.read()) 
            {
                case endOption :
                    break;
                    
                case padOption :
                    break;
                
                case dhcpMessageType :
                    opt_len = _dhcpUdpSocket.read();
                    type = _dhcpUdpSocket.read();
                    break;
                
                case subnetMask :
                    opt_len = _dhcpUdpSocket.read();
                    _dhcpUdpSocket.read((char*)_dhcpipv4struct.SubnetMask, 4);
                    break;
                
                case routersOnSubnet :
                    opt_len = _dhcpUdpSocket.read();
                    _dhcpUdpSocket.read((char*)_dhcpipv4struct.GatewayIp, 4);
                    for (int i = 0; i < opt_len-4; i++)
                    {
                        _dhcpUdpSocket.read();
                    }
                    break;
                
                case dns :
                    opt_len = _dhcpUdpSocket.read();
                    _dhcpUdpSocket.read((char*)_dhcpipv4struct.DnsServerIp, 4);
                    for (int i = 0; i < opt_len-4; i++)
                    {
                        _dhcpUdpSocket.read();
                    }
                    break;
                
                case dhcpServerIdentifier :
                    opt_len = _dhcpUdpSocket.read();
                    if( IPAddress(_dhcpipv4struct.DhcpServerIp) == IPAddress(0,0,0,0) ||
                        IPAddress(_dhcpipv4struct.DhcpServerIp) == _dhcpUdpSocket.remoteIP() )
                    {
                        _dhcpUdpSocket.read((char*)_dhcpipv4struct.DhcpServerIp, sizeof(_dhcpipv4struct.DhcpServerIp));
                    }
                    else
                    {
                        // Skip over the rest of this option
                        while (opt_len--)
                        {
                            _dhcpUdpSocket.read();
                        }
                    }
                    break;

                case dhcpT1value : 
                    opt_len = _dhcpUdpSocket.read();
                    _dhcpUdpSocket.read((char*)&_dhcpT1, sizeof(_dhcpT1));
                    _dhcpT1 = ntohl(_dhcpT1);
                    break;

                case dhcpT2value : 
                    opt_len = _dhcpUdpSocket.read();
                    _dhcpUdpSocket.read((char*)&_dhcpT2, sizeof(_dhcpT2));
                    _dhcpT2 = ntohl(_dhcpT2);
                    break;

                case dhcpIPaddrLeaseTime :
                    opt_len = _dhcpUdpSocket.read();
                    _dhcpUdpSocket.read((char*)&_dhcpLeaseTime, sizeof(_dhcpLeaseTime));
                    _dhcpLeaseTime = ntohl(_dhcpLeaseTime);
                    _renewInSec = _dhcpLeaseTime;
                    break;

                default :
                    opt_len = _dhcpUdpSocket.read();
                    // Skip over the rest of this option
                    while (opt_len--)
                    {
                        _dhcpUdpSocket.read();
                    }
                    break;
            }
        }
    }

    // Need to skip to end of the packet regardless here
    _dhcpUdpSocket.flush();

    return type;
}


/*
    returns:
    0/DHCP_CHECK_NONE: nothing happened
    1/DHCP_CHECK_RENEW_FAIL: renew failed
    2/DHCP_CHECK_RENEW_OK: renew success
    3/DHCP_CHECK_REBIND_FAIL: rebind fail
    4/DHCP_CHECK_REBIND_OK: rebind success
*/
int DhcpClass::checkLease(void){
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::checkLease(void) DEBUG_V1:Function started"));
    #endif

    //this uses a signed / unsigned trick to deal with millis overflow
    unsigned long now = millis();
    signed long snow = (long)now;
    int rc=DHCP_CHECK_NONE;
    if (_lastCheck != 0){
        signed long factor;
        //calc how many ms past the timeout we are
        factor = snow - (long)_secTimeout;
        //if on or passed the timeout, reduce the counters
        if ( factor >= 0 ){
            //next timeout should be now plus 1000 ms minus parts of second in factor
            _secTimeout = snow + 1000 - factor % 1000;
            //how many seconds late are we, minimum 1
            factor = factor / 1000 +1;
            
            //reduce the counters by that mouch
            //if we can assume that the cycle time (factor) is fairly constant
            //and if the remainder is less than cycle time * 2 
            //do it early instead of late
            if(_renewInSec < factor*2 )
                _renewInSec = 0;
            else
                _renewInSec -= factor;
            
            if(_rebindInSec < factor*2 )
                _rebindInSec = 0;
            else
                _rebindInSec -= factor;
        }

        //if we have a lease but should renew, do it
        if (_dhcp_state == STATE_DHCP_LEASED && _renewInSec <=0){
            _dhcp_state = STATE_DHCP_REREQUEST;
            rc = 1 + request_DHCP_lease();
        }

        //if we have a lease or is renewing but should bind, do it
        if( (_dhcp_state == STATE_DHCP_LEASED || _dhcp_state == STATE_DHCP_START) && _rebindInSec <=0){
            //this should basically restart completely
            _dhcp_state = STATE_DHCP_START;
            reset_DHCP_lease();
            rc = 3 + request_DHCP_lease();
        }
    }
    else{
        _secTimeout = snow + 1000;
    }

    _lastCheck = now;
    return rc;
}

IPAddress DhcpClass::getLocalIp(void)
{
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::getLocalIp(void) DEBUG_V1:Function started"));
    #endif
    return IPAddress(_dhcpipv4struct.LocalIp);
}

IPAddress DhcpClass::getSubnetMask(void)
{
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::getSubnetMask(void) DEBUG_V1:Function started"));
    #endif
    return IPAddress(_dhcpipv4struct.SubnetMask);
}

IPAddress DhcpClass::getGatewayIp(void)
{
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::getGatewayIp(void) DEBUG_V1:Function started"));
    #endif
    return IPAddress(_dhcpipv4struct.GatewayIp);
}

IPAddress DhcpClass::getDhcpServerIp(void)
{
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::getDhcpServerIp(void) DEBUG_V1:Function started"));
    #endif
    return IPAddress(_dhcpipv4struct.DhcpServerIp);
}

IPAddress DhcpClass::getDnsServerIp(void)
{
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::getDnsServerIp(void) DEBUG_V1:Function started"));
    #endif
    return IPAddress(_dhcpipv4struct.DnsServerIp);
}

void DhcpClass::printByte(char * buf, uint8_t n ) {
    #if ACTLOGLEVEL>=LOG_DEBUG_V1
      LogObject.uart_send_strln(F("DhcpClass::printByte(char * buf, uint8_t n ) DEBUG_V1:Function started"));
    #endif
  char *str = &buf[1];
  buf[0]='0';
  do {
    unsigned long m = n;
    n /= 16;
    char c = m - 16 * n;
    *str-- = c < 10 ? c + '0' : c + 'A' - 10;
  } while(n);
}
#endif