/*
 * uip_arch.h
 *
 * Created: 06/10/2024 08:05:11 p. m.
 *  Author: Francisco Rios
 */ 

#ifndef __UIP_ARCH_H__
#define __UIP_ARCH_H__

#include "uip.h"


void uip_add32(u8_t *op32, u16_t op16);


 */
u16_t uip_chksum(u16_t *buf, u16_t len);

/**
 * Calculate the IP header checksum of the packet header in uip_buf.
 *
 * The IP header checksum is the Internet checksum of the 20 bytes of
 * the IP header.
 *
 * \return The IP header checksum of the IP header in the uip_buf
 * buffer.
 */
u16_t uip_ipchksum(void);

/*
 */
u16_t uip_tcpchksum(void);

u16_t uip_udpchksum(void);

/** @} */
/** @} */

#endif /* __UIP_ARCH_H__ */