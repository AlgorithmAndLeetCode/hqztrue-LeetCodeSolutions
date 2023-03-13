import time
from ctypes import *
import mmap

def translate(s):
    res=b''
    for l in s.split('\n'):
        if not ':' in l or '>:' in l: continue
        l=l[l.find(':')+1:].strip()
        l=l[:l.find('   ')].strip()
        for b in l.split(' '):
            res+=int(b,16).to_bytes(1,byteorder='little')
    return res

def compile_asm(s,ftype):
    global buf
    buf=mmap.mmap(-1,mmap.PAGESIZE,prot=mmap.PROT_READ|mmap.PROT_WRITE|mmap.PROT_EXEC)
    buf.write(translate(s))
    return ftype(addressof(c_void_p.from_buffer(buf)))

asm_func=compile_asm('''

''',CFUNCTYPE(c_int,POINTER(c_int),c_int))


#https://defuse.ca/online-x86-assembler.htm#disassembly2
#https://defuse.ca/online-x86-assembler.htm
#order: edi,esi,edx,ecx,r8d
#-Ofast -mavx -mavx2

n=100000
a=[i%100 for i in range(n)]
a1=(c_int*n)()
for i in range(n): a1[i]=a[i]
n1=c_int(n)
d=7
d1=c_int(d)

#sum x in a
asm_sum=compile_asm('''
0:  b9 00 00 00 00          mov    ecx,0x0
5:  48 8d 14 b7             lea    rdx,[rdi+rsi*4]
0000000000000009 <begin>:
9:  8b 1f                   mov    ebx,DWORD PTR [rdi]
b:  01 d9                   add    ecx,ebx
d:  48 8d 7f 04             lea    rdi,[rdi+0x4]
11: 48 39 d7                cmp    rdi,rdx
14: 75 f3                   jne    9 <begin>
16: 89 c8                   mov    eax,ecx
18: c3                      ret
''',CFUNCTYPE(c_int,POINTER(c_int),c_int))

t1=time.time()
for i in range(10000):
    #t=0
    #for x in a: t+=x
    #t=sum(a)
    t=asm_sum(a1,n1)
    #print(t)
print('time sum=',time.time()-t1) #4633 vs 446ms


#sum parallel 4
asm_sum_4=compile_asm('''
0:  41 b8 00 00 00 00       mov    r8d,0x0
6:  41 b9 00 00 00 00       mov    r9d,0x0
c:  41 ba 00 00 00 00       mov    r10d,0x0
12: 41 bb 00 00 00 00       mov    r11d,0x0
18: 48 8d 14 b7             lea    rdx,[rdi+rsi*4]
000000000000001c <begin>:
1c: 44 03 07                add    r8d,DWORD PTR [rdi]
1f: 44 03 4f 04             add    r9d,DWORD PTR [rdi+0x4]
23: 44 03 57 08             add    r10d,DWORD PTR [rdi+0x8]
27: 44 03 5f 0c             add    r11d,DWORD PTR [rdi+0xc]
2b: 48 8d 7f 10             lea    rdi,[rdi+0x10]
2f: 48 39 d7                cmp    rdi,rdx
32: 75 e8                   jne    1c <begin>
34: 44 89 c0                mov    eax,r8d
37: 44 01 c8                add    eax,r9d
3a: 44 01 d0                add    eax,r10d
3d: 44 01 d8                add    eax,r11d
40: c3                      ret
''',CFUNCTYPE(c_int,POINTER(c_int),c_int)) #189ms


#sum -Ofast
asm_sum_Ofast=compile_asm('''
0:  85 f6                   test   esi,esi
2:  0f 8e 83 00 00 00       jle    8b <L7>
8:  8d 46 ff                lea    eax,[rsi-0x1]
b:  83 f8 03                cmp    eax,0x3
e:  76 7f                   jbe    8f <L8>
10: 89 f2                   mov    edx,esi
12: 48 89 f8                mov    rax,rdi
15: 66 0f ef c0             pxor   xmm0,xmm0
19: c1 ea 02                shr    edx,0x2
1c: 48 c1 e2 04             shl    rdx,0x4
20: 48 01 fa                add    rdx,rdi
0000000000000023 <L5>:
23: f3 0f 6f 10             movdqu xmm2,XMMWORD PTR [rax]
27: 48 83 c0 10             add    rax,0x10
2b: 66 0f fe c2             paddd  xmm0,xmm2
2f: 48 39 d0                cmp    rax,rdx
32: 75 ef                   jne    23 <L5>
34: 66 0f 6f c8             movdqa xmm1,xmm0
38: 89 f2                   mov    edx,esi
3a: 66 0f 73 d9 08          psrldq xmm1,0x8
3f: 83 e2 fc                and    edx,0xfffffffc
42: 66 0f fe c1             paddd  xmm0,xmm1
46: 66 0f 6f c8             movdqa xmm1,xmm0
4a: 66 0f 73 d9 04          psrldq xmm1,0x4
4f: 66 0f fe c1             paddd  xmm0,xmm1
53: 66 0f 7e c0             movd   eax,xmm0
57: 40 f6 c6 03             test   sil,0x3
5b: 74 31                   je     8e <L10>
000000000000005d <L3>:
5d: 48 63 ca                movsxd rcx,edx
60: 03 04 8f                add    eax,DWORD PTR [rdi+rcx*4]
63: 8d 4a 01                lea    ecx,[rdx+0x1]
66: 39 ce                   cmp    esi,ecx
68: 7e 23                   jle    8d <L1>
6a: 48 63 c9                movsxd rcx,ecx
6d: 03 04 8f                add    eax,DWORD PTR [rdi+rcx*4]
70: 8d 4a 02                lea    ecx,[rdx+0x2]
73: 39 ce                   cmp    esi,ecx
75: 7e 16                   jle    8d <L1>
77: 48 63 c9                movsxd rcx,ecx
7a: 83 c2 03                add    edx,0x3
7d: 03 04 8f                add    eax,DWORD PTR [rdi+rcx*4]
80: 39 d6                   cmp    esi,edx
82: 7e 09                   jle    8d <L1>
84: 48 63 d2                movsxd rdx,edx
87: 03 04 97                add    eax,DWORD PTR [rdi+rdx*4]
8a: c3                      ret
000000000000008b <L7>:
8b: 31 c0                   xor    eax,eax
000000000000008d <L1>:
8d: c3                      ret
000000000000008e <L10>:
8e: c3                      ret
000000000000008f <L8>:
8f: 31 d2                   xor    edx,edx
91: 31 c0                   xor    eax,eax
93: eb c8                   jmp    5d <L3>
''',CFUNCTYPE(c_int,POINTER(c_int),c_int)) #129ms


#sum x//d where x in a
asm_sum_div=compile_asm('''
0:  89 d3                   mov    ebx,edx
2:  b9 00 00 00 00          mov    ecx,0x0
7:  48 8d 34 b7             lea    rsi,[rdi+rsi*4]
000000000000000b <begin>:
b:  8b 07                   mov    eax,DWORD PTR [rdi]
d:  ba 00 00 00 00          mov    edx,0x0
12: f7 fb                   idiv   ebx
14: 01 c1                   add    ecx,eax
16: 48 8d 7f 04             lea    rdi,[rdi+0x4]
1a: 48 39 f7                cmp    rdi,rsi
1d: 75 ec                   jne    b <begin>
1f: 89 c8                   mov    eax,ecx
21: c3                      ret
''',CFUNCTYPE(c_int,POINTER(c_int),c_int,c_int))

t1=time.time()
for i in range(1000):
    #t=sum(x//d for x in a)
    t=asm_sum_div(a1,n1,d1)
    #print(t)
print('time sum div=',time.time()-t1) #3788 vs 173ms


#count x in a s.t. x xor y in [l,r]
asm_xor_in_count=compile_asm('''
0:  89 f0                   mov    eax,esi
2:  41 89 ca                mov    r10d,ecx
5:  89 d6                   mov    esi,edx
7:  85 c0                   test   eax,eax
9:  7e 2f                   jle    3a <L4>
b:  83 e8 01                sub    eax,0x1
e:  45 31 c9                xor    r9d,r9d
11: 4c 8d 5c 87 04          lea    r11,[rdi+rax*4+0x4]
0000000000000016 <L3>:
16: 8b 17                   mov    edx,DWORD PTR [rdi]
18: 31 f2                   xor    edx,esi
1a: 44 39 d2                cmp    edx,r10d
1d: 0f 9d c1                setge  cl
20: 31 c0                   xor    eax,eax
22: 44 39 c2                cmp    edx,r8d
25: 0f 9e c0                setle  al
28: 48 83 c7 04             add    rdi,0x4
2c: 21 c8                   and    eax,ecx
2e: 41 01 c1                add    r9d,eax
31: 49 39 fb                cmp    r11,rdi
34: 75 e0                   jne    16 <L3>
36: 44 89 c8                mov    eax,r9d
39: c3                      ret
000000000000003a <L4>:
3a: 45 31 c9                xor    r9d,r9d
3d: 44 89 c8                mov    eax,r9d
40: c3                      ret
''',CFUNCTYPE(c_int,POINTER(c_int),c_int,c_int,c_int))


#del fpointer
#buf.close()

