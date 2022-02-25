#! python

import sys
import time
from statistics import mean, variance, stdev
from multiprocessing import Process

from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

#
# CONFIGURATION
#
NUMPROC = int(sys.argv[1])
NUMREP = int(sys.argv[2])
NUMENTRIES = int(sys.argv[3])
STEP = NUMENTRIES//NUMPROC
DECRYPTONLY = False

assert(isinstance(STEP, int))

#
# HELPER FUNCTIONS
#
# Process the given memberlist
# d_ciphers = list of ciphers matching the encryption ciphers used for each entry
# sig_1/2 = signature objects initiated with SKEY1 and SKEY2 respectively
def process_list(memberlist, d_ciphers, sig_1, sig_2):
    assert len(memberlist) == len(d_ciphers)

    for i in range(len(memberlist)):

        # 1. Decrypt the ith entry using the ith given cipher
        entry_plaintext = d_ciphers[i].decrypt(memberlist[i])
        
        if not DECRYPTONLY:
            # 2. Split the entry into data (first 113 Byte)
            #   the first signature (next 64 Byte)
            #   and the second signature (last 64 Byte)
            entry_data = entry_plaintext[:113]
            entry_sig_1 = entry_plaintext[113:177]
            entry_sig_2 = entry_plaintext[177:]
            
            # 3. Try to verify the two signatures with the given sigs
            h = SHA256.new(entry_data)
            try:
                sig_1.verify(h, entry_sig_1)
            except:
                print("Verify sig_1 failed")
            try:
                sig_2.verify(h, entry_sig_2)
            except:
                print("Verify sig_2 failed")

#
# MAIN PART
#
# 1. GENERATE KEYS
GMK = get_random_bytes(16)
SKEY1 = ECC.generate(curve='P-256')
SKEY2 = ECC.generate(curve='P-256')

# 2. GENERATE MEMBERLIST
MEMBERLIST = []
E_CIPHERS = [AES.new(GMK,AES.MODE_EAX) for i in range(NUMENTRIES)]
SIG_1 = DSS.new(SKEY1, 'fips-186-3')
SIG_2 = DSS.new(SKEY2, 'fips-186-3')

for i in range(NUMENTRIES):

    entry_data = get_random_bytes(113)

    h = SHA256.new(entry_data)
    entry_sig_1 = SIG_1.sign(h)
    entry_sig_2 = SIG_2.sign(h)

    entry = entry_data + entry_sig_1 + entry_sig_2
    
    entry_ciphertext = E_CIPHERS[i].encrypt(entry)

    MEMBERLIST.append(entry_ciphertext)
    
# 3. PROCESS MEMBERLIST

p_times = []

for r in range(NUMREP):
    D_CIPHERS = [AES.new(GMK,AES.MODE_EAX, E_CIPHERS[i].nonce) for i in range(NUMENTRIES)]

    start_time = time.time()

    ps = [Process(target=process_list, args=(MEMBERLIST[i:i+STEP], D_CIPHERS[i:i+STEP], SIG_1, SIG_2)) for i in range(0,NUMENTRIES,STEP)]

    [p.start() for p in ps]
    [p.join() for p in ps]

    end_time = time.time()

    p_times.append(end_time-start_time)

    print(f'Run {r} complete')

#
# PRINT RESULTS
#
print('')
print(f'Stats for {len(MEMBERLIST)} entries after {NUMREP} runs with {NUMPROC} processes:')
print('=============================================')
print(f'Mean:      {mean(p_times)} Seconds')
print(f'Variance:  {variance(p_times)}')
print(f'Std. Dev.: {stdev(p_times)}')
