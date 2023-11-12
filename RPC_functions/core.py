import random
import sys
from impacket import system_errors
from impacket.dcerpc.v5 import transport
from impacket.dcerpc.v5.ndr import NDRCALL, NDRSTRUCT
from impacket.dcerpc.v5.dtypes import UUID, ULONG, WSTR, DWORD, LONG, NULL, BOOL, UCHAR, PCHAR, RPC_SID, LPWSTR, GUID
from impacket.dcerpc.v5.rpcrt import DCERPCException, RPC_C_AUTHN_WINNT, RPC_C_AUTHN_LEVEL_PKT_PRIVACY
from impacket.uuid import uuidtup_to_bin

class DCERPCSessionError(DCERPCException):
    def __init__(self, error_string=None, error_code=None, packet=None):
        DCERPCException.__init__(self, error_string, error_code, packet)

    def __str__(self):
        key = self.error_code
        if key in system_errors.ERROR_MESSAGES:
            error_msg_short = system_errors.ERROR_MESSAGES[key][0]
            error_msg_verbose = system_errors.ERROR_MESSAGES[key][1]
            return 'SessionError: code: 0x%x - %s - %s' % (self.error_code, error_msg_short, error_msg_verbose)
        else:
            return 'SessionError: unknown error code: 0x%x' % self.error_code



class EFS_RPC_BLOB(NDRSTRUCT):
    structure = (
        ('Data', DWORD),
        ('cbData', PCHAR),
    )

class RPCProtocol(object):
    """
    Documentation for class RPCProtocol
    """

    uuid = None
    version = None
    pipe = None

    ncan_target = None
    __rpctransport = None
    dce = None

    def __init__(self):
        super(RPCProtocol, self).__init__()

    def connect(self, username, password, domain, lmhash, nthash, target, dcHost, doKerberos=False, targetIp=None):
        self.ncan_target = r'ncacn_np:%s[%s]' % (target, self.pipe)
        self.__rpctransport = transport.DCERPCTransportFactory(self.ncan_target)

        if hasattr(self.__rpctransport, 'set_credentials'):
            self.__rpctransport.set_credentials(
                username=username,
                password=password,
                domain=domain,
                lmhash=lmhash,
                nthash=nthash
            )

        if doKerberos == True:
            self.__rpctransport.set_kerberos(doKerberos, kdcHost=dcHost)
        if targetIp is not None:
            self.__rpctransport.setRemoteHost(targetIp)

        self.dce = self.__rpctransport.get_dce_rpc()
        self.dce.set_auth_type(RPC_C_AUTHN_WINNT)
        self.dce.set_auth_level(RPC_C_AUTHN_LEVEL_PKT_PRIVACY)

        print("[>] Connecting to %s ... " % self.ncan_target, end="")
        sys.stdout.flush()
        try:
            self.dce.connect()
        except Exception as e:
            print("\x1b[1;91mfail\x1b[0m")
            print("[!] Something went wrong, check error status => %s" % str(e))
            return False
        else:
            print("\x1b[1;92msuccess\x1b[0m")

        print("[>] Binding to <uuid='%s', version='%s'> ... " % (self.uuid, self.version), end="")
        sys.stdout.flush()
        try:
            self.dce.bind(uuidtup_to_bin((self.uuid, self.version)))
        except Exception as e:
            print("\x1b[1;91mfail\x1b[0m")
            print("[!] Something went wrong, check error status => %s" % str(e))
            return False
        else:
            print("\x1b[1;92msuccess\x1b[0m")

        return True
    
class EfsRpcDecryptFileSrvResponse(NDRCALL):
    structure = ()


class EfsRpcDecryptFileSrv(NDRCALL):
    opnum = 5
    structure = (
        ('FileName', WSTR),   # Type: wchar_t *
        ('OpenFlag', ULONG),  # Type: unsigned
    )


class EfsRpcFileKeyInfoEx(NDRCALL):
    opnum = 16
    structure = (
        ('dwFileKeyInfoFlags', DWORD), # Type: DWORD
        ('Reserved', EFS_RPC_BLOB), # Type: EFS_RPC_BLOB *
        ('FileName', WSTR), # Type: wchar_t *
        ('InfoClass', DWORD), # Type: DWORD
    )


class EfsRpcFileKeyInfoExResponse(NDRCALL):
    structure = ()


class EfsRpcEncryptFileSrv(NDRCALL):
    opnum = 4
    structure = (
        ('FileName', WSTR), # Type: wchar_t *
    )

class EfsRpcEncryptFileSrvResponse(NDRCALL):
    structure = ()

class EfsRpcQueryUsersOnFile(NDRCALL):
    opnum = 6
    structure = (
        ('FileName', WSTR),  # Type: wchar_t *
    )

class EfsRpcQueryUsersOnFileResponse(NDRCALL):
    structure = ()

class EfsRpcQueryRecoveryAgents(NDRCALL):
    opnum = 7
    structure = (
        ('FileName', WSTR),  # Type: wchar_t *
    )

class EfsRpcQueryRecoveryAgentsResponse(NDRCALL):
    structure = ()

class EfsRpcFileKeyInfo(NDRCALL):
    opnum = 12
    structure = (
        ('FileName', WSTR),   # Type: wchar_t *
        ('InfoClass', DWORD)  # Type: DWORD
    )

class EfsRpcFileKeyInfoResponse(NDRCALL):
    structure = ()

class EfsRpcDuplicateEncryptionInfoFile(NDRCALL):
    opnum = 13
    structure = (
        ('SrcFileName', WSTR), # Type: wchar_t *
        ('DestFileName', WSTR), # Type: wchar_t *
        ('dwCreationDisposition', DWORD), # Type: DWORD
        ('dwAttributes', DWORD), # Type: DWORD
        ('RelativeSD', EFS_RPC_BLOB), # Type: EFS_RPC_BLOB *
        ('bInheritHandle', BOOL), # Type: BOOL
    )

class EfsRpcDuplicateEncryptionInfoFileResponse(NDRCALL):
    structure = ()

class ENCRYPTION_CERTIFICATE_LIST(NDRSTRUCT):
    align = 1
    structure = (
        ('Data', ':'),
    )

class EfsRpcAddUsersToFileEx(NDRCALL):
    opnum = 15
    structure = (
        ('dwFlags', DWORD), # Type: DWORD
        ('Reserved', EFS_RPC_BLOB), # Type: EFS_RPC_BLOB *
        ('FileName', WSTR), # Type: wchar_t *
        ('EncryptionCertificates', ENCRYPTION_CERTIFICATE_LIST), # Type: ENCRYPTION_CERTIFICATE_LIST *
    )

class EfsRpcAddUsersToFileExResponse(NDRCALL):
    structure = ()

class EfsRpcFileKeyInfoEx(NDRCALL):
    opnum = 16
    structure = (
        ('dwFileKeyInfoFlags', DWORD), # Type: DWORD
        ('Reserved', EFS_RPC_BLOB), # Type: EFS_RPC_BLOB *
        ('FileName', WSTR), # Type: wchar_t *
        ('InfoClass', DWORD), # Type: DWORD
    )

class EfsRpcFileKeyInfoExResponse(NDRCALL):
    structure = ()
    