section "header", ROM0[$100] 
	nop
    jp start


section "code", ROM0[$150]

start:

	di

	; global apu settings
	ld a, %10000000
	ldh [$ff26], a
	ld a, %00010001
	ldh [$ff25], a
	ld a, %01110111
	ldh [$ff24], a

	; sound channel 1 settings
	xor a
	ldh [$ff10], a ; no sweep
	ld a, %10000000
	ldh [$ff11], a ; 50% duty
	ld a, %11110000
	ldh [$ff12], a ; max volume, no envelope
	ld a, %10000000 | %00000111
	ldh [$ff14], a ; frequency high and control

	; enable ram
	ld a, %10101010 ; use $aa instead of $0a so we can reuse it for the preamble
	ld [$0000], a

	; send preamble
	call transmit_byte
	ld a, %10101010
	call transmit_byte

	ld c, 0 ; stores current page number

page:
	; tell mbc to select current page
	ld hl, $4000 
	ld [hl], c

	; set hl to start of page
	ld hl, $a000

byte:
	ld a, [hl+] ; load next byte
	call transmit_byte

	; bytes loop end
	ld a, $c0
	cp h
	jr nz, byte

	; page loop end
	inc c
	ld a, 4
	cp c
	jr nz, page

	reti


; transmits byte stored in the a register
; clobbers b and a
transmit_byte:
	
	ld b, 8 ; number of bits to send
	call transmit_bits

	; send sync bits
	ld a, %01000000
	ld b, 3 ; number of bits to send
	call transmit_bits

	ret


; a: bits to send
; b: number of bits to send
; clobbers a and b
transmit_bits:

bits:
	rla ; shift high bit into carry flag
	
	push af ; save a for later

	jr c, one

zero:
	ld a, %11100110
	jr done_apu
one:
	ld a, %11101110

done_apu:
	ldh [$ff13], a ; frequency low bits

	; wait for (4 + 4*256 + 12*255 + 8) = 4096 clocks = 1/(4194304 / 4096)*1000ms ~= 0.9775 ms
	xor a
wait_1_ms:
	inc a
	jr nz, wait_1_ms

	pop af

	; bits loop end
	dec b
	jr nz, bits

	ret