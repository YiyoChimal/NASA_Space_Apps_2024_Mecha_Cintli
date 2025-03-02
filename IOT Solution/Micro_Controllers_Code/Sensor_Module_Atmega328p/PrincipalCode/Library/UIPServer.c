/*
 * UIPServer.c
 *
 * Created: 06/10/2024 07:32:41 p. m.
 *  Author: Francisco Rios
 */ 

#include "UIPEthernet.h"
#include "UIPServer.h"
#include "utility/logging.h"
extern "C" {
#include "utility/uipopt.h"
}

UIPServer::UIPServer(uint16_t port) : _port(htons(port))
{
}

UIPClient UIPServer::available()
{
UIPEthernetClass::tick();
for ( uip_userdata_t* data = &UIPClient::all_data[0]; data < &UIPClient::all_data[UIP_CONNS]; data++ )
{
if (data->packets_in[0] != NOBLOCK
&& (((data->state & UIP_CLIENT_CONNECTED) && uip_conns[data->conn_index].lport ==_port)
|| ((data->state & UIP_CLIENT_REMOTECLOSED) && ((uip_userdata_closed_t *)data)->lport == _port)))
return UIPClient(data);
}
return UIPClient();
}

UIPClient UIPServer::accept()
{
UIPEthernetClass::tick();
for ( uip_userdata_t* data = &UIPClient::all_data[0]; data < &UIPClient::all_data[UIP_CONNS]; data++ )
{
if (!(data->state & UIP_CLIENT_ACCEPTED)
&& (((data->state & UIP_CLIENT_CONNECTED) && uip_conns[data->conn_index].lport ==_port)
|| ((data->state & UIP_CLIENT_REMOTECLOSED) && ((uip_userdata_closed_t *)data)->lport == _port))) {
data->state |= UIP_CLIENT_ACCEPTED;
return UIPClient(data);
}
}
return UIPClient();
}

void UIPServer::begin()
{
uip_listen(_port);
UIPEthernetClass::tick();
listening = true;
}

void UIPServer::begin(uint16_t port) {
_port = htons(port);
begin();
}

void UIPServer::end() {
uip_unlisten(_port);
listening = false;
for ( uip_userdata_t* data = &UIPClient::all_data[0]; data < &UIPClient::all_data[UIP_CONNS]; data++ )
{
if ((data->state & UIP_CLIENT_CONNECTED) && uip_conns[data->conn_index].lport ==_port)
{
UIPClient client(data);
client.stop();
}
}
}

UIPServer::operator bool() {
return listening;
}

size_t UIPServer::write(uint8_t c)
{
return write(&c,1);
}

size_t UIPServer::write(const uint8_t *buf, size_t size)
{
size_t ret = 0;
for ( uip_userdata_t* data = &UIPClient::all_data[0]; data < &UIPClient::all_data[UIP_CONNS]; data++ )
{
if ((data->state & UIP_CLIENT_CONNECTED) && uip_conns[data->conn_index].lport ==_port)
ret += UIPClient::_write(data,buf,size);
}
return ret;
}
