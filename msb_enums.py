msb_buttons = { #Nintendo Switch
    0x65 : "BUTTON_A",
    0x66 : "BUTTON_B",
    0x67 : "BUTTON_X",
    0x68 : "BUTTON_Y",
    0x69 : "BUTTON_L",
    0x6A : "BUTTON_R",
    0x6B : "BUTTON_ZL",
    0x6C : "BUTTON_ZR",
    0x6D : "BUTTON_SL",
    0x6E : "BUTTON_SR",
    0x6F : "ARROW_UP",
    0x70 : "ARROW_DOWN",
    0x71 : "ARROW_LEFT",
    0x72 : "ARROW_RIGHT",
    0x73 : "L_STICK",
    0x74 : "R_STICK",
    0x75 : "L_STICK_PRESS",
    0x76 : "R_STICK_PRESS",
    0x77 : "BUTTON_DOWN1",
    0x78 : "BUTTON_DOWN2",
    0x79 : "BUTTON_UP",
    0x7A : "BUTTON_LEFT",
    0x7B : "BUTTON_PLUS",
    0x7C : "BUTTON_MINUS",
    0x7D : "BUTTON_HOME",
    0x7E : "BUTTON_PHOTO"
}

msb_codes = {
	0x00 : ["NextLine", 0],
	0x04 : ["Color", 3], #4 arguments for the first code, then 3 for the second
    0x05 : ["5", 0],
	0x09 : ["9", 0],
    0x0A : ["A", 0],
	0x0B : ["B", 0],
	0x0E : ["E", 0],
	0x0F : ["Center", 0],
	0x11 : ["InputInit", 2],
    0x12 : ["12", 2],
	0x15 : ["15", 10],
	0x18 : ["InputWait", 0],
	0x19 : ["19", 2],
    0x1A : ["1A", 2],
	0x20 : ["LastName", 0],
	0x21 : ["FirstName", 0],
	0x22 : ["22", 0],
	0x24 : ["Underscores", 0],
	0x30 : ["30", 0],
    0x35 : ["35", 0],
	0x53 : ["53", 0],
	0x56 : ["56", 0]
}

msb_spec_chars = {
    0x7F : chr(0x2009), #used after line breaks to align the text with the first line. Same width as the symbol above
    0x2BF : chr(0x2008) #espace insécable utilisé dans les traductions françaises, devant les symboles de ponctuations nécessitant un espace (?, !, etc.)
}