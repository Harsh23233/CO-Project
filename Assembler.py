import sys
global PC1
global PC2

def r_type(instruction, rd, rs1, rs2, register):
    opcode = {
    'add': '0110011', 'sub': '0110011', 'sll': '0110011', 'slt': '0110011',
    'sltu': '0110011', 'xor': '0110011', 'srl': '0110011', 'or': '0110011',
    'and': '0110011'
    }
    func3 = {
    'add': '000', 'sub': '000', 'sll': '001', 'slt': '010', 'sltu': '011',
    'xor': '100', 'srl': '101', 'or': '110', 'and': '111'
    }
    func7 = {
    'add': '0000000', 'sub': '0100000', 'sll': '0000000', 'slt': '0000000',
    'sltu': '0000000', 'xor': '0000000', 'srl': '0000000', 'or': '0000000',
    'and': '0000000'
    }

    if rd not in register or rs1 not in register or rs2 not in register:
        return None, "Invalid register"
    op = opcode[instruction]
    f3 = func3[instruction]
    f7 = func7[instruction]
    regd = register[rd]
    reg1 = register[rs1]
    reg2 = register[rs2]
    binary = f7 + reg2 + reg1 + f3 + regd + op
    return binary, None

def decimal_to_binary(n, length):
        return format(n if n >= 0 else (1 << length) + n, f'0{length}b')

def check_input_format(line, inst_type):
    if inst_type == 'lw':
        parts = line.split(',')
        return len(parts) == 2 and ' ' in parts[0] and '(' in parts[1] and ')' in parts[1]
    elif inst_type in ['addi', 'sltiu', 'jalr']:
        parts = line.split(',')
        return len(parts) == 3 and ' ' in parts[0]
    elif inst_type == 'sw':
        parts = line.split(',')
        return len(parts) == 2 and ' ' in parts[0] and '(' in parts[1] and ')' in parts[1]
    return False

def check_register(reg_name):
    return reg_name in register

def i_code(x):
    opcode, funct3 = itype[x[0]]
    if x[0] == 'lw':
        rs1, imm1 = x[1].split(',')[1].split('(')[1][:-1], x[1].split(',')[1].split('(')[0]
        if not all(map(check_register, [rs1, x[1].split(',')[0]])) or int(imm1)<-2048 or int(imm1)>=2048:
            return "Error"
        imm = decimal_to_binary(int(imm1), 12)
        return imm + register[rs1] + funct3 + register[x[1].split(',')[0]] + opcode
    elif x[0] in ['addi', 'sltiu', 'jalr']:
        if not check_register(x[1].split(',')[0]) or not check_register(x[1].split(',')[1])  or int(x[1].split(',')[2])<-2048 or int(x[1].split(',')[2])>=2048:
            return "Error"
        imm = decimal_to_binary(int(x[1].split(',')[2]), 12)
        return imm + register[x[1].split(',')[1]] + funct3 + register[x[1].split(',')[0]] + opcode
    return "Error"

def s_code(x):
    rs1, imm1 = x[1].split(',')[1].split('(')[1][:-1], x[1].split(',')[1].split('(')[0]
    if not all(map(check_register, [rs1, x[1].split(',')[0]])) or int(imm1)<-2048 or int(imm1)>=2048:
        return "Error"
    imm = decimal_to_binary(int(imm1), 12)
    opcode, funct3 = stype[x[0]]
    return imm[0:7] + register[x[1].split(',')[0]] + register[rs1] + funct3 + imm[7:] + opcode

def b_type_errors(list1,list2):
    for line in list1:
        if line not in btype.keys():
            return 1
    for i in range(0,2):
        if list2[i] not in register.keys():
            return 1
    if(int(list2[2])>=2**12 or int(list2[2])<-2**12):
        return 1
    return 0

def b_type(list1,list2):
    global output
    if list2[2] in pc_of_label:
        list2[2]=int(pc_of_label[list2[2]]-PC2)
    else:
        list2[2]=int(list2[2])
    flag=b_type_errors(list1,list2)
    if(flag):
        print("Invalid b type")
        return flag
    label=decimal_to_binary(int(list2[2]),13)
    temp = (label[0] + label[2:8] + register[list2[1]] + register[list2[0]] + btype[list1[0]] + label[8:12] + label[1] + '1100011')
    if(temp=="00000000000000000000000001100011"):
        return temp
    output.append(temp)
    return flag

register = {
    "zero": '00000', "ra": '00001', "sp": '00010', "gp": '00011', "tp": '00100',
    "t0": '00101', "t1": '00110', "t2": '00111', "s0": '01000', "fp": '01000',
    "s1": '01001', "a0": '01010', "a1": '01011', "a2": '01100', "a3": '01101',
    "a4": '01110', "a5": '01111', "a6": '10000', "a7": '10001', "s2": '10010',
    "s3": '10011', "s4": '10100', "s5": '10101', "s6": '10110', "s7": '10111',
    "s8": '11000', "s9": '11001', "s10": '11010', "s11": '11011', "t3": '11100',
    "t4": '11101', "t5": '11110', "t6": '11111'
}

rtype = ['add', 'sub', 'sll', 'slt', 'sltu', 'xor', 'srl', 'or', 'and']
itype = {'lw': ('0000011', '010'), 'addi': ('0010011', '000'), 'sltiu': ('0010011', '011'), 'jalr': ('1100111', '000')}
stype = {'sw': ('0100011', '010')}
btype={"beq":'000',"bne":'001',"blt":'100',"bge":'101',"bltu":'110',"bgeu":'111'}
utype={"auipc":"0010111","lui":"0110111"}
jtype={"jal":"1101111"}
output = []
valid_instructions = True
pc_of_label={}
PC1=0
PC2=0

inpt=sys.argv[1]
otpt=sys.argv[2]
pointer1=open(inpt,'r')
pointer2=open(otpt,'w')
newline=[]
lines=pointer1.readlines()

for i in range(len(lines)):
        j=lines[i].split()
        if j==[]:
            newline.append(i)
            continue
        elif len(j)>3:
            valid_instructions=False
            print("Error: Invalid Instruction")
            break
        elif j[0][-1]==":":
            for k in j[0][:-1]:
                if not k.isalnum() and k!="_":
                    valid_instructions=False
                    print("Error: Invalid Label Name")
                    break
            pc_of_label[j[0][0:-1]]=PC1
            del j[0]
        lines[i]=j
        PC1+=4
if ['beq', 'zero,zero,0\n'] not in lines and ['beq', 'zero,zero,0'] not in lines:
    valid_instructions=False
else:
    if newline!=[]:
        for i in newline:
            del lines[i]
    for i in lines:
        if len(i) != 2:
            valid_instructions = False
            print("Invalid number of arguments")
            break
        elif i[0] in rtype:
            c = i[1].split(',')
            if len(c) != 3:
                valid_instructions = False
                print("Invalid number of arguments for r type")
                break
            else:
                binary, error = r_type(i[0], c[0], c[1], c[2], register)
                if error:
                    valid_instructions = False
                    print(error)
                    break
                elif binary:
                    output.append(binary)
                else:
                    valid_instructions = False
                    print("Invalid register for r type")
                    break
        elif i[0] in stype.keys() and check_input_format(i[0]+' '+i[1], 'sw'):
            result = s_code(i)
            if result == "Error":
                valid_instructions=False
                print("Invalid for s type")
                break
            output.append(result)
        elif i[0] in itype.keys() and check_input_format(i[0]+' '+i[1], i[0]):
            result = i_code(i)
            if result == "Error":
                valid_instructions=False
                print("Invalid for i type")
                break
            output.append(result)
        elif i[0] in btype.keys():
            c=i[1].split(',')
            if len(c)!=3:
                valid_instructions=False
                print("Invalid number of arguments for b type")
                break
            else:
                valid_instructions=b_type([i[0]],c)
                if(valid_instructions=="00000000000000000000000001100011"):
                    output.append(valid_instructions)
                    break
        elif i[0] in utype:
            if len(i)!=2:
                print("Error: Invalid Instruction Syntax for u type")
                valid_instructions=False
                break
            op=i[1].split(",")
            if op[0] not in register:
                print("Error: Invalid Register for u type")
                valid_instructions=False
                break
            elif len(op)!=2:
                print("Error: Inavlid Instruction Syntax for u type")
                valid_instructions=False
                break
            elif int(op[1])>=(2**31) or int(op[1])<-(2**31):
                print("Error: Immediate value out of range for u type")
                valid_instructions=False
                break
            else:
                s = decimal_to_binary(int(op[1]),32)
                line = s[0:20] + register[op[0]] + utype[i[0]]
                output.append(line)
        elif i[0] in jtype:
            op=i[1].split(",")
            s=''
            if op[1] in pc_of_label:
                op[1]=int(pc_of_label[op[1]]-PC2)
            else:
                op[1]=int(op[1])
            if len(i)!=2:
                print("Error: Invalid Instruction Syntax for j type")
                valid_instructions=False
                break
            elif op[0] not in register:
                print("Error: Invalid Register for j type")
                valid_instructions=False
                break
            elif len(op)!=2:
                print("Error: Inavlid Instruction Syntax for j type")
                valid_instructions=False
                break
            elif int(op[1])>=(2**20) or int(op[1])<-(2**20):
                print(op[1])
                print("Error: Immediate value out of range for j type")
                valid_instructions=False
                break
            s=decimal_to_binary(int(op[1]),21)
            line = s[-21] + s[-11:-1] + s[-12] + s[-20:-12] + register[op[0]] + jtype[i[0]]
            output.append(line)
        else:
            print("Error: Invalid Instruction")
            valid_instructions=False
            break
        PC2+=4

pointer1.close()
if valid_instructions:
    pointer2.write("\n".join(output))

pointer2.close()
