#! python

import sys
import time

from Crypto.Hash import SHA256
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS

#
# CONFIGURATION
#
NUMREP = int(sys.argv[1])

#
# MAIN PART
#
# 1. GENERATE KEYS
GMK = get_random_bytes(32)
SKEY1 = ECC.generate(curve='P-256')
SKEY2 = ECC.generate(curve='P-256')

# 2. INITIALIZE CRYPTO
E_CIPHER = ChaCha20.new(key=GMK)
SIG_1 = DSS.new(SKEY1, 'fips-186-3')
SIG_2 = DSS.new(SKEY2, 'fips-186-3')

# 3. COMPUTE ENTRY
entry_data = get_random_bytes(49)

start_time = time.time_ns()

for i in range(NUMREP):

    h = SHA256.new(entry_data)
    entry_sig_1 = SIG_1.sign(h)
    entry_sig_2 = SIG_2.sign(h)

    entry = entry_data + entry_sig_1 + entry_sig_2
    
    entry_ciphertext = E_CIPHER.encrypt(entry)

end_time = time.time_ns()

print(f'Membership entry with {NUMREP} repetitions: {(end_time-start_time)/NUMREP}')

# 4. COMPUTE AUTHRESPONSE
entry_data = get_random_bytes(16)

start_time = time.time_ns()

for i in range(NUMREP):

    h = SHA256.new(entry_data)
    entry_sig_1 = SIG_1.sign(h)

end_time = time.time_ns()

print(f'AuthResponse  with {NUMREP} repetitions: {(end_time-start_time)/NUMREP}')
