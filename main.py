#! python

import time
from statistics import mean, variance, stdev
from multiprocessing import Process

from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

NUMPROC = 5
NUMREP = 25
NUMENTRIES = 1000
STEP = NUMENTRIES//NUMPROC

def process_list(memberlist, d_ciphers, verifier_1, verifier_2):
    for i in range(len(memberlist)):
        entry_plaintext = d_ciphers[i].decrypt(memberlist[i])

        entry_data = entry_plaintext[:113]
        entry_sig_1 = entry_plaintext[113:177]
        entry_sig_2 = entry_plaintext[177:]
        
        h = SHA256.new(entry_data)
        try:
            verifier_1.verify(h, entry_sig_1)
        except:
            print("Verify sig_1 failed")
        try:
            verifier_2.verify(h, entry_sig_2)
        except:
            print("Verify sig_2 failed")

# 1. GENERATE KEYS
GMK = get_random_bytes(16)
SKEY1 = ECC.generate(curve='P-256')
SKEY2 = ECC.generate(curve='P-256')

# 2. GENERATE MEMBERLIST
MEMBERLIST = []
E_CIPHERS = [AES.new(GMK,AES.MODE_EAX) for i in range(NUMENTRIES)]
signer_1 = DSS.new(SKEY1, 'fips-186-3')
signer_2 = DSS.new(SKEY2, 'fips-186-3')

for i in range(NUMENTRIES):

    entry_data = get_random_bytes(113)

    h = SHA256.new(entry_data)
    entry_sig_1 = signer_1.sign(h)
    entry_sig_2 = signer_2.sign(h)

    entry = entry_data + entry_sig_1 + entry_sig_2
    
    entry_ciphertext = E_CIPHERS[i].encrypt(entry)

    MEMBERLIST.append(entry_ciphertext)
    
# 3. PROCESS MEMBERLIST

p_times = []

for r in range(NUMREP):
    D_CIPHERS = [AES.new(GMK,AES.MODE_EAX, E_CIPHERS[i].nonce) for i in range(NUMENTRIES)]
    verifier_1 = DSS.new(SKEY1, 'fips-186-3')
    verifier_2 = DSS.new(SKEY2, 'fips-186-3')

    start_time = time.time()

    ps = [Process(target=process_list, args=(MEMBERLIST[i:i+STEP], D_CIPHERS[i:i+STEP], verifier_1, verifier_2)) for i in range(0,NUMENTRIES,STEP)]

    [p.start() for p in ps]
    [p.join() for p in ps]

    end_time = time.time()

    p_times.append(end_time-start_time)

    print(f'Run {r} complete')

print('')
print(f'Stats for {len(MEMBERLIST)} entries after {NUMREP} runs with {NUMPROC} processes:')
print('=============================================')
print(f'Mean:      {mean(p_times)} Seconds')
print(f'Variance:  {variance(p_times)}')
print(f'Std. Dev.: {stdev(p_times)}')
