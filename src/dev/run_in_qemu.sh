#!/bin/sh

memory=$(grep MemTotal /proc/meminfo)
actual_memory=${memory:16:-3}
memory_to_allocate=$((actual_memory/8))k

echo :: Allocated $memory_to_allocate in memory

qemu-system-x86_64 -boot d -cdrom out/archlinux-2023.05.08-x86_64.iso -m $memory_to_allocate
