from os import write
import sys
def twos_complement_binary_to_decimal(binary):
    if binary[0] == '1': # If the number is negative
        # Invert all bits
        inverted = ''.join('1' if bit == '0' else '0' for bit in binary)
        # Add 1 to the inverted number
        binary = bin(int(inverted, 2) + 1)[2:].zfill(len(binary))
        # Convert the binary number to decimal
        decimal = -int(binary, 2)
    else:
        decimal = int(binary, 2)
    return decimal

def sign_extend(value, bits):
    sign_bit = value[0]
    if sign_bit == '1':
        value = value[0] * (32 - bits) + value
    else:
        value = '0' * (32 - bits) + value
    return value

def decimal_to_binary(n, length):
        return format(n if n >= 0 else (1 << length) + n, f'0{length}b')

def decimal_to_hex(decimal):
    if not (0 <= decimal <= 2**23-1):
        raise ValueError("Decimal value should be in the range 0 to 255 for 8-bit data representation")
    return '0x' + format(decimal, '08x')

regs = {
    'PC' : 0,
    '00000' : 0, '00001' : 0, '00010' : 256, '00011' : 0, '00100' : 0,
    '00101' : 0, '00110' : 0, '00111' : 0, '01000' : 0, '01000' : 0,
    '01001' : 0, '01010' : 0, '01011' : 0, '01100' : 0, '01101' : 0,
    '01110' : 0, '01111' : 0, '10000' : 0, '10001' : 0, '10010' : 0,
    '10011' : 0, '10100' : 0, '10101' : 0, '10110' : 0, '10111' : 0,
    '11000' : 0, '11001' : 0, '11010' : 0, '11011' : 0, '11100' : 0,
    '11101' : 0, '11110' : 0, '11111' : 0
}

data_mem = {
    '0x00010000': 0,
    '0x00010004': 0,
    '0x00010008': 0,
    '0x0001000c': 0,
    '0x00010010': 0,
    '0x00010014': 0,
    '0x00010018': 0,
    '0x0001001c': 0,
    '0x00010020': 0,
    '0x00010024': 0,
    '0x00010028': 0,
    '0x0001002c': 0,
    '0x00010030': 0,
    '0x00010034': 0,
    '0x00010038': 0,
    '0x0001003c': 0,
    '0x00010040': 0,
    '0x00010044': 0,
    '0x00010048': 0,
    '0x0001004c': 0,
    '0x00010050': 0,
    '0x00010054': 0,
    '0x00010058': 0,
    '0x0001005c': 0,
    '0x00010060': 0,
    '0x00010064': 0,
    '0x00010068': 0,
    '0x0001006c': 0,
    '0x00010070': 0,
    '0x00010074': 0,
    '0x00010078': 0,
    '0x0001007c': 0
    }

rtype=["0110011"]
itype = ["0000011","0010011","0010011","1100111"]
stype = ["0100011"]
btype=["1100011"]
utype=["0010111","0110111"]
jtype=["1101111"]
rhtype = ["1000101"]
mtype=["0001010"]
ltype=["0000111"]

valid_instructions = True
o_put=[]

def r_type(line):
    global regs
    rs2=line[7:12]
    rs1=line[12:17]
    rd=line[-12:-7]
    if(line[0:7]=='0000000'):
        if(line[-15:-12]=='000'):
            regs[rd]=regs[rs1]+regs[rs2]
        elif(line[-15:-12]=='001'):
            rs2 = decimal_to_binary(regs[rs2],32)
            rs2=rs2[-5:]
            rs2=int(rs2,2)
            regs[rd]=regs[rs1]<<rs2
        elif(line[-15:-12]=='010'):
            if(regs[rs1]<regs[rs2]):
                regs[rd]=1
            else:
                regs[rd]=0
        elif(line[-15:-12]=='011'):
            rs1=decimal_to_binary(regs[rs1],32)
            rs1=int(rs1,2)
            rs2=decimal_to_binary(regs[rs2],32)
            rs2=int(rs2,2)
            if(rs1<rs2):
                regs[rd]=1
            else:
                regs[rd]=0
        elif(line[-15:-12]=='100'):
            regs[rd]=(regs[rs1])^(regs[rs2])
        elif(line[-15:-12]=='101'):
            rs2 = decimal_to_binary(regs[rs2],32)
            rs2=rs2[-5:]
            rs2=int(rs2,2)
            regs[rd]=regs[rs1]>>rs2
        elif(line[-15:-12]=='110'):
            regs[rd]=regs[rs1]|regs[rs2]
        elif(line[-15:-12]=='111'):
            regs[rd]=regs[rs1]&regs[rs2]
    else:
        regs[rd]=regs[rs1]-regs[rs2]

def l_type(line):
    global regs
    rs2=line[7:12]
    rs1=line[12:17]
    rd=line[-12:-7]
    result = regs[rs1]*regs[rs2]
    res = decimal_to_binary(result, 32)
    if len(res)<=32:
        s=twos_complement_binary_to_decimal(res)
        regs[rd] = s
    else:
        r = len(res)-32
        ans = res[r:len(res)]
        answer = twos_complement_binary_to_decimal(ans)
        regs[rd]=answer

def s_type(line):
    global regs
    data_mem[str(decimal_to_hex(regs[line[12:17]]+twos_complement_binary_to_decimal(line[0:7]+line[20:25])))]=regs[line[7:12]]  #rs2 = mem(rs1 + imm)
    
def i_type(line):
    global regs
    global data_mem
    global j_check
    global i
    opcode = line[-7:]
    if(opcode == '0000011'):  #lw
        regs[line[20:25]]=data_mem[str(decimal_to_hex(regs[line[12:17]]+twos_complement_binary_to_decimal(line[0:12])))]   #rs2 = mem(rs1 + imm)
    if(opcode == '0010011' and line[17:20]=='000'):   #addi
        regs[line[20:25]] = regs[line[12:17]]+twos_complement_binary_to_decimal(line[0:12])    #rs2 = rs1+imm
    if(opcode == '0010011' and line[17:20]=='011'):  #sltiu
        if(int(decimal_to_binary(regs[line[12:17]]),2)<int(line[0:12]),2):   #if unsigned(rs1)<unsigned(imm)
            regs[line[20:25]] =1
    if(opcode == '1100111'):   #jalr
        j_check=1
        regs[line[20:25]]=regs['PC']+4    #store ret address in rd
        regs['PC'] = regs[line[12:17]]+twos_complement_binary_to_decimal(line[0:12])    #update PC
        regs['PC'] = twos_complement_binary_to_decimal(decimal_to_binary(regs['PC'],32)[0:31]+'0')    #before jumping LSB of PC = 0
        imm=twos_complement_binary_to_decimal(line[0:12])+regs[line[12:17]]
        i=imm//4

def u_type(line):
    global regs
    #lui
    if line[-7:]=="0110111":
        #Extracting dest reg and immediate from instruction
        rd=line[-12:-7]
        imm=line[:-12]
        #Extending immediate according to instruction semantics
        while len(imm)<32:
            imm+='0'
        #Converting immediate to int and writing it on the specified reg
        imm=twos_complement_binary_to_decimal(imm)
        regs[rd]=imm
    else:
        #Extracting dest reg and immediate from instruction
        rd=line[-12:-7]
        imm=line[:-12]
        #Extending immediate according to instruction semantics
        while len(imm)<32:
            imm+='0'
        #Converting immediate to int and writing it on the specified reg
        imm=twos_complement_binary_to_decimal(imm)
        regs[rd]=regs['PC']+imm

def j_type(line):
    global regs
    global i
    #Extracting dest reg and immediate from instruction
    rd=line[-12:-7]
    imm=line[0]+line[-19:-12]+line[-20]+line[1:-20]
    imm=imm[:-1]+"0"
    #Saving the return address in dest reg
    regs[rd]=regs["PC"]+4
    #Adding the offset to PC and i
    imm=twos_complement_binary_to_decimal(imm)
    regs["PC"]+=imm
    i+=imm//4

def b_type(instruction):
    global regs
    global i
    global j_check
    #extracting immediate
    imm = sign_extend(instruction[0] + instruction[24:25] + instruction[1:7] + instruction[20:24] + '0', 13)
    #extracting registers
    rs2 = regs[instruction[7:12]]
    rs1 = regs[instruction[12:17]]
    funct3 = instruction[17:20]
    #beq
    if funct3 == '000':
        if rs1 == rs2:
            regs['PC'] += twos_complement_binary_to_decimal(imm)
            i+=twos_complement_binary_to_decimal(imm)//4
            j_check=1
    #bne
    elif funct3 == '001':
        if rs1 != rs2:
            regs['PC'] += twos_complement_binary_to_decimal(imm)
            i+=twos_complement_binary_to_decimal(imm)//4
            j_check=1
    #blt
    elif funct3 == '100':
        if rs1 < rs2:
            regs['PC'] += twos_complement_binary_to_decimal(imm)
            i+=twos_complement_binary_to_decimal(imm)//4
            j_check=1
    #bge
    elif funct3 == '101':
        if rs1 >= rs2:
            regs['PC'] += twos_complement_binary_to_decimal(imm)
            i+=twos_complement_binary_to_decimal(imm)//4
            j_check=1
    #bltu
    elif funct3 == '110':
        if rs1 < rs2:
            regs['PC'] += twos_complement_binary_to_decimal(imm)
            i+=twos_complement_binary_to_decimal(imm)//4
            j_check=1
    #bgeu
    elif funct3 == '111':
        if rs1 >= rs2:
            regs['PC'] += twos_complement_binary_to_decimal(imm)
            i+=twos_complement_binary_to_decimal(imm)//4
            j_check=1
def rh_type(instruction):
    global flag
    global regs
    global j_check
    if(instruction[0:25] == '1'*25):
        for i in regs.keys and i!='PC':
            regs[i] = 0
    elif(instruction[0:25] == '0'*25):
        j_check=1
        flag=1

def m_type(instruction):
    rd = int(instruction[-12:-7],2)
    rs = int(instruction[-17:-12],2)
    rs_content = decimal_to_binary(regs[str(rs)],32)[::-1]
    regs[str(rd)] = int(rs_content, 2)

inpt=sys.argv[1]
otpt=sys.argv[2]
pointer1=open(inpt,'r')
pointer2=open(otpt,'a')
lines=pointer1.readlines()

j_check=0

for i in range(0,len(lines)-1):    
    lines[i]=lines[i][:-1]

i = 0
flag=0

while i<len(lines):
    output=[]
    if(len(lines[i])!=32):
        valid_instructions=False
        break
    if lines[i][-7:] in rtype:
        r_type(lines[i])
    elif lines[i][-7:] in itype:
        i_type(lines[i])
    elif lines[i][-7:] in stype:
        s_type(lines[i])
    elif lines[i][-7:] in btype:
        if(lines[i]=="00000000000000000000000001100011"):
            flag=1
        b_type(lines[i])
    elif lines[i][-7:] in utype:
        u_type(lines[i])
        if lines[i][-7:]=='1100111':
            j_check=1
    elif lines[i][-7:] in jtype:
        j_type(lines[i])
        j_check=1
    elif lines[i][-7:] in rhtype:
        rh_type(lines[i])
    elif lines[i][-7:] in mtype:
        m_type(lines[i])
    elif lines[i][-7:] in ltype:
        l_type(lines[i])
    else:
        valid_instructions = False
        break
    regs['00000']=0
    if j_check==0:
        i+=1
        regs["PC"]=i*4
    j_check=0
    for j in regs:
        a=decimal_to_binary(regs[j],32)
        b="0b"+a
        output.append(b)
    if valid_instructions:
        pointer2.write(" ".join(output))
        pointer2.write("\n")
    if flag==1:
        break

if valid_instructions:
    for i in data_mem:
        pointer2.write(i+":"+"0b"+decimal_to_binary(data_mem[i],32)+"\n")

pointer1.close()
pointer2.close()
