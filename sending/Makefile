all:
	rgbasm -L -o "send_save.o" "send_save.asm"
	rgblink -o "send_save.gb" "send_save.o"
	rgbfix -f lhg -p 0 -m 19 -r 3 "send_save.gb"
