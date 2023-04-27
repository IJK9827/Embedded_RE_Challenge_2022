Cipher Tech Solutions Challenge STM32
By: Isaiah John Kovacich

--- 1: What is the password needed to unlock the device?
I think the password is the following:
84gK&oDH4ZzBsH$

The following is my thought process as I went through the code to find the password.
I used Ghidra to decompile the binary as ARM Cortex little endian. I've never used it before, so bare with me.
There is some text as const char pointers at the end that are used in a function called FUN_08000dd0.
Ghirda named it FUN_08000dd0, and its address is 0x08000dd0.
It seems to render the GUI on the LCD and can produce enter password and success output.
FUN_08000dd0 is called twice in FUN_0800124c, where FUN_080010e0 is inbetween them to get from "enter password" to "success" based on the 1 and 0 input.
Once FUN_080010e0 is reached, it probably has the password input.
I looked up a file called stm32f429xx.h on the stm32 github, which made it easier to find some addresses.
For my own reference, UndefinedFunction_08002480 calls FUN_0800124c. Also the param1 address passed to FUN_080010e0 is 200002D0 for SRAM which is from DAT_08001314.
UndefinedFunction_08002480 seems to be the main function.

FUN_080076c2 gets the input for the password.
After some sort of user input checking by FUN_0800759e calls, FUN_080010e0 calls FUN_08001098.
FUN_080010e0 checks the inputted password.
Inside FUN_08001098, FUN_08000fd4 and FUN_08008054 are called.
FUN_08008054 seems to compare strings.
FUN_08000fd4 seems to use a permutation cipher.
DAT_08011738 seems to be the password, but encrypted.
To reverse one part of the permutation cipher to get the password as chars, I used the following below.

bVar2 = ((bVar1 & 8) ^ (bVar1 >> 6) ^ ((bVar1 & 7) << 4) ^ (((bVar1 & 0x60) << 1) | ((bVar1 >> 2) & 7)))
bVar2 = ((bVar1 & 8) ^ (bVar1 >> 6) ^ ((bVar1 & 7) << 4) ^ (((bVar1 & 0x60) << 1) | ((bVar1 >> 2) & 7)))
bVar1        2x00001000      2x11000000      2x00000111          2x01100000                  2x00011100
bVar2        2x00001000      2x00000011      2x01110000          2x11000000                  2x00000111
bVar2 2x01000011
bVar1 2x00100100  2x10001000  2x01000100
bVar2 2x00000001^ 2x00001000  2x10000000
bVar1 = ((bVar2 & 0x80) >> 1) ^ //2x01000000
    (((bVar2 & 0x40) >> 1) ^ ((bVar2 & 0x80) >> 2) ^ ((bVar2 & 0x01) << 5)) ^ //2x00100000
    ((bVar2 & 0x20) >> 4) ^ //2x00000010
    ((bVar2 & 0x10) >> 4) ^ //2x00000001
    (bVar2 & 8) ^ //2x00001000
    ((bVar2 & 4) << 2) ^ //2x00010000
    ((bVar2 & 2) << 6) ^ ((bVar2 & 8) << 4) ^ //2x10000000
    ((bVar2 & 1) << 2) ^ ((bVar2 & 0x80) >> 5) //2x00000100

With that, I put it into a function called rev_v into a Python script called cipher.py.
I'm not sure what the "ee 5c 47 e4" means besides storing for decrytion. I skipped those bytes.
The line from the cipher.py containing:
local_14 = DAT_08001094 * local_14 + 0x314159
is indepentant of the end result, so for reversing I kept it the same.
The line from the cipher.py containing:
bVar3 = ((bVar1 & 0xff) - (local_14)) ^ ((local_14 >> 0x17) & 0xff)
is the reverse of the following from Ghidra:
bVar1 = (char)local_14 + ((byte)(local_14 >> 0x17) ^ *(byte *)(local_c + param_1))

The output of cipher.py gives the password:
84gK&oDH4ZzBsH$

I did not use ghidra.py. I kept some commented out code and pasted this for reference.
arm-none-eabi-objdump -b binary --adjust-vma=0x08000000 -D flash.bin -m arm >> dis.bin

--- 2: What interface or communication protocol is used to enter the password? 
I think the protocol being used is USART with 9600 baud rate.
FUN_080010e0 called FUN_080076c2 passing (local_118 + local_c) as (auStack_114 + local_c + -4), which I should change for Ghidra.
local_118 should be the password input, because it is used in FUN_08001098.
FUN_080076c2 writes to local_118 from USART as (*param1)[1]. The param1 is 200002D0 from DAT_08001314.
200002D0 SRAM is a struct that has 40011000 USART1 address written to the first index from FUN_08001778 the USART init function.
In FUN_08004678, 0x600 is GPIOA pins 9 and 10 for USART1_TX and USART1_RX
GPIOA clock speed is set for 3 very high clock speed for 84MHz but may vary with capacitance.
In FUN_08001778 the USART init function with USART struct, the baud rate is set to 0x2580 9600, and the register is initilzed with (*param_1 + 8) in FUN_080078e4.
The code in FUN_080078e4 changes it into a float format and with formula Tx/Rx Baud = fck/(8*(2-OVER8)xUSARTDIV) and also based on RCC PPRE2 APB high-speed prescaler.
Also it uses ulonglong to float, which is what makes it so complicated.
The USART registers states CK pin disabled, LIN mode disabled, IrDA disabled, Half duplex mode is not selected, and Smartcard Mode disabled are set.
      

Using the Memory mapping section from stm32f429xx document, I tried to describe some addresses and what they are used for. I'm not familiar with STM32 HAL library source code.
Below is a tree of function calls with addresses and 32 ints used, so I could understand what addresses and devices were being used and where.
It was helpful for me, but there is probably a better way to organize.

UndefinedFunction_08002480(void); //main function? 200000D0, 20030000, 20000000, 200005C8
    FUN_0800245c(); //E000ED00
    FUN_0800800c(); //uses function pointer?
    FUN_0800124c(); //20000348 LCD or gyro struct?, 20000230, 40020800, 000186A0, 200002D0 SRAM with password input [1]
        FUN_08003a5c(); //sets RCC with 40023C00 from DAT_08003a9c for something.
            FUN_08003d28(); //E000ED00 ?
            FUN_08003aa0(); //20000000, 20000048, 20000044
            FUN_08001cc8();
        FUN_08001318(); //40023800, 40007000
            FUN_080055dc(); //40023800 RCC, 42470000, 42470E80, 200005B4
            FUN_0800553c(); //40023800, 420E0040, 40007000 PWR, 420E0044, 200005B4
            FUN_08005acc(); //40023800, 20000000, 20000044, 200005B4
        FUN_0800186c(); //sets RCC with 40023800 from DAT_08001990 for something
        FUN_08001778(); //sets something at 200002D0 from DAT_080017c4 same as from DAT_08001314,  40011000 USART1 set to param1[0] struct in SRAM?
            FUN_08007504(); //USART init
                        *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) & 0xffffdfff; // USART prescaler and outputs disabled 
                        //                                                                        
                        *(uint *)(*param_1 + 0x10) = *(uint *)(*param_1 + 0x10) & 0xffffb7ff; //CK pin disabled, LIN mode disabled
                        *(uint *)(*param_1 + 0x14) = *(uint *)(*param_1 + 0x14) & 0xffffffd5; //IrDA disabled, Half duplex mode is not selected, Smartcard Mode disabled
                        *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) | 0x2000; //USART enabled
                        param_1[0x10] = 0;
                        *(undefined *)((int)param_1 + 0x3d) = 0x20;
                        *(undefined *)((int)param_1 + 0x3e) = 0x20;
                FUN_080021d4(); //40011000 USART1, 40023800 RCC, 40020000 GPIOA //Contains Baudrate?
                                    *(uint *)(DAT_0800225c + 0x44) = *(uint *)(DAT_0800225c + 0x44) | 0x10; //RCC  USART1 clock enabled
                                    *(uint *)(DAT_0800225c + 0x30) = *(uint *)(DAT_0800225c + 0x30) | 1; //RCC GPIOAEN: IO port A clock enable
                    FUN_08004678(); //GPIOA Init 40023800, 40013800, 40020000, 40020400, 40020800, 40020C00, 40021000, 40021400, 40021800, 40021C00, 40022000, 40022400,
                                    40013C00 EXTI, 
                                    0x600 is GPIOA pins 9 and 10 for USART1_TX and USART1_RX
                                    param_1[2] = param_2[3] << ((local_c & 0x7f) << 1) | ~(3 << ((local_c & 0x7f) << 1)) & param_1[2]; //GPIOA clock speed
                                    3 is for very high clock speed for 84MHz but may vary with capacitance
                FUN_080078e4(); // 40011000 USART1, 40011400 USART6, 51EB851F,
                                (*param_1 + 8) = //set Baudrate to 0x2580 9600
                                The code changes it into a float format and with formula Tx/Rx Baud = fck/(8*(2-OVER8)xUSARTDIV) and also based on RCC PPRE2 APB high-speed prescaler.
                                From 0xffff69f3 and 0xc, parity control is disabled.
                    FUN_08005ee4(); //20000000 SRAM base, 40023800 RCC
                    FUN_08005ebc(); //same as ^ but with 0xd instead of 10
                    FUN_08000acc(); //Finds remainder long int division
                         FUN_08000afc(); //Lots of stuff, code address return 0x8000be6??? mistake? UNRECOVERED_JUMPTABLE?
                                Code maybe divides param_1 and param_2 as one single 64int divided into param_3, and store the quotient in *param_5 and the remainder as the return value.
        FUN_08001508(); //20000188, 40016800 LCD, F000F800?
        FUN_080013fc(); //200000EC, 40023000 RCC, 40023800
        FUN_08001424(); //200000F4, 4002B000 DMA2D, 40023800 Not addresses: 000186A0, 001E847F, 003D08FF, 431BDE83, 10624DD3
        FUN_080017cc(); //20000314, A0000140 FMC control FMC_SDCR SDRAM, 00000000 low addresses read from?
        FUN_080016d8(); //20000288, 40010000 TIM1, 40023800
            FUN_0800740c(); //40010000, 40000400, 40000800, 40000C00, 40010400, 40014000, 40001800
        FUN_08001488(); //20000134, 40005C00 I2C3, 000186A0
            FUN_08004c1c(); //000186A0, 001E847F, 003D08FF, 431BDE83, 10624DD3
        FUN_0800166c(); //20000230, 40015000
        FUN_080019a4(); //40023830, 40020000, 4002000C, 40021800, 40021804, 40021808, 4002180C
        FUN_08001b76();
            FUN_08001a94();
                FUN_08006510(); //200005B4
        FUN_0800759e(); //gyroscope failed.
        FUN_08002b88(); //200003BC, 40016800, 200004A4, 200004F0, 20000004, 20000064
            FUN_08005f0c(); //42470068, 40023800, 42470070, 40007000, 200005B4
        FUN_08002c8c(0,0xd0000000);
        FUN_08002c8c(1,0xd0000000); //200003BC, 200004D8, 20000064
            FUN_08002c5c(); //200004F0 + 0x28 SRAM run code ptr?
            FUN_08002c74(); //200004F0 + 0x2c SRAM run code ptr?
            FUN_0800513c();
                FUN_0800520c(); //stuff
            FUN_080051b8(); //40016800 + 0x18
        FUN_08003244(); //200004F0 SRAM run code ptr?
        FUN_08000dd0(1); //Enter password text with LCD
        FUN_080010e0(DAT_08001314); //Password input
            FUN_08008074(); //copy
            FUN_0800759e(); //Out text maybe? Enter password text and 1B 63 00 00. 200005B4 system time SRAM
            FUN_08001a50(); //40020010 GPIOA, 40021818 GPIOG maybe USART pins
            FUN_080076c2(); //Reads password input from (*param_1)[1] reads from 40011000 USART from SRAM 200002D0 struct, which is set in FUN_08001778();
                            UTF-16 ushort ( << 0x17) >> 0x17 ) or UTF-8 byte ( & 0x7f )
                FUN_08007806(); //(*param_1)[3] and [5] reads from 40011000 USART
            FUN_0800759e(); //Checks password input for something???
            FUN_08001098(); //Checks if correct password
                FUN_08000fd4(); //cipher text input
                FUN_08008054(); //compare ciphered strings, password at DAT_08011738 as string
        FUN_08000dd0(0); //Success text with LCD
        do {
            FUN_08001bc8(DAT_08001300);
            FUN_08000ec4(DAT_08001300);
            FUN_08003b40(100); //sleep, 20000048
                FUN_08003b28(); //200005B4 Gets system time from SRAM
        } while( true );

--- 3: Besides entering the correct password, what other conditions, if any, must be satisfied to unlock the device?
FUN_08001998 disables interrupts and goes into an infinit loop, which seems to be used when an error occurred.
So all times when that function could be called are conditions that must be satisfied. 
The gyroscope seems to need to be initailized and working.

--- 4: What vulnerabilities exist in the device's firmware? How might you go about exploiting them?
From USART input, an attacker could brute force the password.
Also an attacker could find the password length based on computation time,
because in FUN_08001098, it skips a lot of computation if the entered password doesn't have a length of 0xf.
Also the compare string function returns early if the first chars aren't equal.
I would make a program to brute force different lengths while recording an accurate time in nanoseconds taken to reply.
Then with the longest time, brute force the first char, and do the same for the other chars in order finding the longest computation time for all of them.

Some other vulnerability ideas I had could be turning on unnesscary devices and unstable power to skip instructions (not firmware),