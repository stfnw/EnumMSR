.PHONY: all clean test

obj-m += enum-msr.o

# ccflags-y += -DDEBUG

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

test: all
	sudo insmod enum-msr.ko
	sudo rmmod  enum-msr
# watch output with sudo dmesg -w
