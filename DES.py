"""
Coen Valk HW 1

DES implementation.
"""

import socket
import sys
import os
import numpy as np

from multiprocessing import Process

passes = 2

batch = 1024

# permute all bits as np arrays with the ordering given
# outputs: new bits np array that are humble-dy jumbled
def permute_bits(bits, ordering):
    new_bits = np.zeros(len(ordering))
    for idx, order in enumerate(ordering):
        new_bits[idx] = bits[order - 1]
    return new_bits

# expands and permutates 4 bit into 8 bit for F function
def expand_and_perm(bits):
    LHS_perm = np.array([4, 1, 2, 3])
    RHS_perm = np.array([2, 3, 4, 1])
    LHS = permute_bits(bits, LHS_perm)
    RHS = permute_bits(bits, RHS_perm)
    return np.concatenate([LHS, RHS])

# turns np array of bits into a one character byte (for easy XOR operation)
def arr_to_byte(arr):
    val = 0
    for idx, v in enumerate(arr):
        val += v * (2 ** (len(arr) - idx - 1))
    return val

# turns 8 bits as byte character into np array of 8 bits,
# for easy permutation computation and splicing and concatenation
def byte_to_arr(byte):
    arr = np.unpackbits(np.uint8(byte))
    return arr

# input: left and right half of keys
# output: (next key, new_left, new_right)
def generate_next_key(LHS, RHS):
    key_perm = np.array([6, 3, 7, 4, 8, 5, 10, 9])
    new_LHS = np.append(LHS[1:], LHS[-1])
    new_RHS = np.append(RHS[1:], RHS[-1])
    key_10 = np.concatenate([new_LHS, new_RHS])
    key_8 = permute_bits(key_10, key_perm)
    return (key_8, new_LHS, new_RHS)

# takes RHS 4 bit np array of the plaintext to be passed through
# the F function with the 8 bit key array.
# outputs 4 bit string to be XOR'd with the LHS.
def F_function(RHS, key):
    S0 = np.array(
        [
            [1, 0, 3, 2],
            [3, 2, 1, 0],
            [0, 2, 1, 3],
            [3, 1, 3, 2]
        ]
    )

    S1 = np.array(
        [
            [0, 1, 2, 3],
            [2, 0, 1, 3],
            [3, 0, 1, 0],
            [2, 1, 0, 3]
        ]
    )

    bit4_perm = np.array([2, 4, 3, 1])
    
    plain_8 = expand_and_perm(RHS)
    plain_byte = arr_to_byte(plain_8)
    key_byte = arr_to_byte(key)
    # XOR operation to get new bits
    new_byte = np.uint8(plain_byte) ^ np.uint8(key_byte)
    assert plain_byte == np.uint8(new_byte) ^ np.uint8(key_byte)
    new_arr = byte_to_arr(new_byte)
    L = new_arr[:len(new_arr) // 2]
    R = new_arr[len(new_arr) // 2:]
    # lookup bits in S tables:
    L_col = 2 * L[1] + L[2]
    L_row = 2 * L[0] + L[3]
    
    R_col = 2 * R[1] + R[2]
    R_row = 2 * R[0] + R[3]

    S0_result = byte_to_arr(np.uint8(S0[L_row][L_col]))[-2:]
    S1_result = byte_to_arr(np.uint8(S1[R_row][R_col]))[-2:]
    result = np.concatenate([S0_result, S1_result])
    result_perm = permute_bits(result, bit4_perm)
    return result_perm

# performs one round of DES
# returns LHS and RHS of the next DES round
# input LHS, RHS and 8 bit key.
def DES_round(LHS, RHS, key):
    new_R = F_function(RHS, key)
    new_R_bytes = arr_to_byte(new_R)
    LHS_bytes = arr_to_byte(LHS)
    next_byte = np.uint8(new_R_bytes) ^ np.uint8(LHS_bytes)
    next_RHS = byte_to_arr(next_byte)[-4:]

    return (RHS, next_RHS)

# takes the plaintext byte with 10 bit key array and returns a ciphertext byte.
# performs two rounds of DES.
def full_DES(plaintext, key10):
    init_perm = np.array([2, 6, 3, 1, 4, 8, 5, 7])
    rev_init_perm = np.array([4, 1, 3, 5, 7, 2, 8, 6])
    key_init_perm = np.array([3, 5, 2, 7, 4, 10, 1, 9, 8, 6])

    plain_arr = byte_to_arr(plaintext)
    plain_perm = permute_bits(plain_arr, init_perm)
    key_perm = permute_bits(key10, key_init_perm)
    
    key_LHS = key_perm[:5]
    key_RHS = key_perm[5:]
    LHS = plain_perm[:4]
    RHS = plain_perm[4:]
    for i in range(passes):
        key8, key_LHS, key_RHS = generate_next_key(key_LHS, key_RHS)
        LHS, RHS = DES_round(LHS, RHS, key8)
    full_cipher = np.concatenate([RHS, LHS])
    cipher_perm = permute_bits(full_cipher, rev_init_perm)
    return arr_to_byte(cipher_perm)

def DES_decrypt(ciphertext, key10):
    init_perm = np.array([2, 6, 3, 1, 4, 8, 5, 7])
    rev_init_perm = np.array([4, 1, 3, 5, 7, 2, 8, 6])
    key_init_perm = np.array([3, 5, 2, 7, 4, 10, 1, 9, 8, 6])

    keys = []
    
    cipher_arr = byte_to_arr(ciphertext)
    cipher_perm = permute_bits(cipher_arr, init_perm)
    key_perm = permute_bits(key10, key_init_perm)

    key_LHS = key_perm[:5]
    key_RHS = key_perm[5:]

    LHS = cipher_perm[:4]
    RHS = cipher_perm[4:]
    
    for i in range(passes):
        key8, key_LHS, key_RHS = generate_next_key(key_LHS, key_RHS)
        keys.append(key8)

    for i in range(passes):
        LHS, RHS = DES_round(LHS, RHS, keys[ - i - 1])

    full_plain = np.concatenate([RHS, LHS])
    plain_perm = permute_bits(full_plain, rev_init_perm)
    return arr_to_byte(plain_perm)

def full_encrypt(plain, key10):
    cipher = ""
    for c in plain:
        cipher += chr(np.uint8(full_DES(ord(c), key10)))
    return cipher

def full_decrypt(cipher, key10):
    plain = ""
    for c in cipher:
        plain += chr(np.uint(DES_decrypt(ord(c), key10)))
    return plain
