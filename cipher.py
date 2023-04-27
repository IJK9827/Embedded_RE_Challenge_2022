# def FUN_08000fd4(param_1, param_2, DAT_08001090, DAT_08001094):
#     param_3 = [0] * 4
#     local_14 = DAT_08001090
#     for i in range(4):
#         param_3[i] = (DAT_08001090 >> i) & 0xff
#     for local_c in range(param_2):
#         local_14 = DAT_08001094 * local_14 + 0x314159
#         bVar1 = (local_14 & 0xff) ^ ((local_14 >> 0x17) & 0xff) ^ (param_1[local_c] & 0xff)
#         bVar2 = ((bVar1 & 8) ^ (bVar1 >> 6) ^ ((bVar1 & 7) << 4) ^
#                 (((bVar1 & 0x60) << 1) | ((bVar1 >> 2) & 7)))
#         param_3.append(bVar2)
#     return param_3[4:]

# def reverse_bVar2(bVar1):
#     bVar2 = ((bVar1 & 8) ^ (bVar1 >> 6) ^ ((bVar1 & 7) << 4) ^
#                 (((bVar1 & 0x60) << 1) | ((bVar1 >> 2) & 7)))
#     b1 = bVar2 & 0x07
#     b2 = (bVar2 >> 4) & 0x07
#     b3 = (bVar2 >> 6) & 0x01
#     b4 = (bVar2 >> 7) & 0x01
#     bVar1 = (b4 << 7) | ((b1 << 2) & 0x1c) | ((b2 >> 1) & 0x03) | (b3 << 6) | (b2 << 4)
#     return bVar1

def rev_v(bVar2):
    #bVar2 = ((bVar1 & 8) ^ (bVar1 >> 6) ^ ((bVar1 & 7) << 4) ^ (((bVar1 & 0x60) << 1) | ((bVar1 >> 2) & 7)))
    temp8 = ((bVar2 & 0x80) >> 1) #2x01000000
    temp7 = (((bVar2 & 0x40) >> 1) ^ ((bVar2 & 0x80) >> 2) ^ ((bVar2 & 0x01) << 5))  #2x00100000
    temp6 = ((bVar2 & 0x20) >> 4)  #2x00000010
    temp5 = ((bVar2 & 0x10) >> 4)  #2x00000001
    temp4 = (bVar2 & 8)  #2x00001000
    temp3 = ((bVar2 & 4) << 2)  #2x00010000
    temp2 = ((bVar2 & 2) << 6) ^ ((bVar2 & 8) << 4) #/2x10000000
    temp1 = ((bVar2 & 1) << 2) ^ ((bVar2 & 0x80) >> 5) #2x00000100
    bVar1 = (temp8 ^ temp7 ^ temp6 ^ temp5 ^ temp4 ^ temp3 ^ temp2 ^ temp1)
    return bVar1
#((bVar2 & 0x80) >> 1) ^ (((bVar2 & 0x40) >> 1) ^ ((bVar2 & 0x80) >> 2) ^ ((bVar2 & 0x01) << 5)) ^ ((bVar2 & 0x20) >> 4) ^((bVar2 & 0x10) >> 4) ^ (bVar2 & 8) ^ ((bVar2 & 4) << 2) ^((bVar2 & 2) << 6) ^ ((bVar2 & 8) << 4) ^ ((bVar2 & 1) << 2) ^ ((bVar2 & 0x80) >> 5)

def decrypt(param_1, param_2, DAT_08001090, DAT_08001094):
    param_3 = []#[0] * 4
    local_14 = DAT_08001090
    # for i in range(4):
    #     param_3[i] = (DAT_08001090 >> i) & 0xff
    for local_c in range(0,param_2):
        local_14 = DAT_08001094 * local_14 + 0x314159
        bVar1 = rev_v(param_1[local_c])
        bVar3 = ((bVar1 & 0xff) - (local_14)) ^ ((local_14 >> 0x17) & 0xff)
        param_3.append(bVar3 & 0xff)
    return param_3

print("test: ", rev_v(0xFF))
#ee 5c 47 e4 
#ee 5c 47 e4 6e 43 50 02 cd 4c b6 01 cf 8d 0d 1b 5e df c6 00
input_data = bytearray.fromhex("6e 43 50 02 cd 4c b6 01 cf 8d 0d 1b 5e df c6") 

#input_data = input_data[::-1]
#print(input_data.hex())
output_data = bytearray(decrypt(input_data, len(input_data), 0xe4475cee, 0x0b48cd19)) #0Xee5c47e4, 0X19cd480b))#
print(output_data.hex())
for c in output_data:
    print(chr(c),end='')
print()
# for x in range(0,255):
#     print(x," ",chr(x),end='\n')
# print()