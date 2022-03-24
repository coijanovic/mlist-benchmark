#! python

import sys
import time
from statistics import mean, variance, stdev

from Crypto.Hash import SHA256
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

#
# CONFIGURATION
#
NUMREP = int(sys.argv[1])
NUMENTRIES = int(sys.argv[2])
DECRYPTONLY = False

#
# HELPER FUNCTIONS
#
# Process the given entry which consists of a memberlist ciphertext
# and the corresponding decryption cipher
def process_entry(entry):

    entry_ciphertext, d_cipher = entry

    # 1. Decrypt the ith entry using the ith given cipher
    entry_plaintext = d_cipher.decrypt(entry_ciphertext)
    
    if not DECRYPTONLY:
        # 2. Split the entry into data (first 49 Byte)
        #   the first signature (next 64 Byte)
        #   and the second signature (last 64 Byte)
        entry_data = entry_plaintext[:49]
        entry_sig_1 = entry_plaintext[49:113]
        entry_sig_2 = entry_plaintext[113:]
        
        # 3. Try to verify the two signatures with the given sigs
        h = SHA256.new(entry_data)
        try:
            SIG_1.verify(h, entry_sig_1)
            SIG_2.verify(h, entry_sig_2)
            return 0
        except:
            return 1

#
# MAIN PART
#
# 1. GENERATE KEYS
GMK = get_random_bytes(32)
SKEY1 = ECC.generate(curve='P-256')
SKEY2 = ECC.generate(curve='P-256')

# 2. GENERATE MEMBERLIST
MEMBERLIST = []
E_CIPHERS = [ChaCha20.new(key=GMK) for i in range(NUMENTRIES)]
SIG_1 = DSS.new(SKEY1, 'fips-186-3')
SIG_2 = DSS.new(SKEY2, 'fips-186-3')

for i in range(NUMENTRIES):

    entry_data = get_random_bytes(49)

    h = SHA256.new(entry_data)
    entry_sig_1 = SIG_1.sign(h)
    entry_sig_2 = SIG_2.sign(h)

    entry = entry_data + entry_sig_1 + entry_sig_2
    
    entry_ciphertext = E_CIPHERS[i].encrypt(entry)

    MEMBERLIST.append(entry_ciphertext)
    
# 3. PROCESS MEMBERLIST

p_times = []

for r in range(NUMREP):
    D_CIPHERS = [ChaCha20.new(key=GMK, nonce=E_CIPHERS[i].nonce) for i in range(NUMENTRIES)]
    in_list = zip(MEMBERLIST,D_CIPHERS)

    start_time = time.time()

    res = [process_entry(e) for e in in_list]

    end_time = time.time()

    if not DECRYPTONLY:
        assert sum(res) == 0

    p_times.append(end_time - start_time)

    print(f'Run {r} complete')

#
# WRITE RESULTS TO LOG
#
l = f'''
PARAMETERS
==========
Entries:      {NUMENTRIES}
Repetitions:  {NUMREP}
Decrypt-Only: {DECRYPTONLY}
RESULTS:
========
Mean:      {mean(p_times)} Seconds
Variance:  {variance(p_times)}
Std. Dev.: {stdev(p_times)}
'''
with open('/data/log', 'a') as log:
    log.write(l)
