/*
 * mempool.h
 *
 * Created: 06/10/2024 07:58:01 p. m.
 *  Author: Francisco Rios
 */ 


#ifndef MEMPOOL_H
#define MEMPOOL_H

#include <inttypes.h>

#define POOLSTART 0
#define NOBLOCK 0

#include "mempool_conf.h"

struct memblock
{
	memaddress begin;
	memaddress size;
	memhandle nextblock;
};

class MemoryPool
{
	#ifdef MEMPOOLTEST_H
	friend class MemoryPoolTest;
	#endif

	protected:
	static struct memblock blocks[MEMPOOL_NUM_MEMBLOCKS+1];

	public:
	static void init();
	static memhandle allocBlock(memaddress);
	static void freeBlock(memhandle);
	static void resizeBlock(memhandle handle, memaddress position);
	static void resizeBlock(memhandle handle, memaddress position, memaddress size);
	static memaddress blockSize(memhandle);
};
#endif