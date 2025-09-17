/* -*- Mode: C++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
/*
 * This file is part of the LibreOffice project.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

#include "AIAgentService.hxx"
#include <com/sun/star/frame/Desktop.hpp>
#include <com/sun/star/text/XTextDocument.hpp>
#include <comphelper/processfactory.hxx>
#include <tools/urlobj.hxx>
#include <osl/process.h>
#include <osl/file.hxx>
#include <rtl/bootstrap.hxx>
#include <sal/log.hxx>

#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <sstream>

#pragma comment(lib, "ws2_32.lib")

using namespace css;

namespace sw::aiagent {

AIAgentService::AIAgentService()
    : m_bInitialized(false)
{
    SAL_INFO("sw.aiagent", "AIAgentService constructor");
}

AIAgentService::~AIAgentService()
{
    SAL_INFO("sw.aiagent", "AIAgentService destructor");
    stopPythonAgent();
}

// XServiceInfo
OUString SAL_CALL AIAgentService::getImplementationName()
{
    return getImplementationName_Static();
}

sal_Bool SAL_CALL AIAgentService::supportsService(const OUString& rServiceName)
{
    return cppu::supportsService(this, rServiceName);
}

uno::Sequence<OUString> SAL_CALL AIAgentService::getSupportedServiceNames()
{
    return getSupportedServiceNames_Static();
}

// XInitialization
void SAL_CALL AIAgentService::initialize(const uno::Sequence<uno::Any>& aArguments)
{
    if (m_bInitialized)
        return;
    
    SAL_INFO("sw.aiagent", "Initializing AIAgentService");
    
    // Extract frame reference from arguments
    for (const auto& arg : aArguments)
    {
        if (arg >>= m_xFrame)
        {
            SAL_INFO("sw.aiagent", "Frame reference obtained");
            break;
        }
    }
    
    if (!m_xFrame.is())
    {
        // Try to get current frame from desktop
        try
        {
            uno::Reference<uno::XComponentContext> xContext = comphelper::getProcessComponentContext();
            uno::Reference<frame::XDesktop2> xDesktop = frame::Desktop::create(xContext);
            m_xFrame = xDesktop->getCurrentFrame();
        }
        catch (const uno::Exception& e)
        {
            SAL_WARN("sw.aiagent", "Failed to get frame: " << e.Message);
            return;
        }
    }
    
    if (m_xFrame.is())
    {
        // Get the text document
        uno::Reference<uno::XInterface> xController = m_xFrame->getController();
        if (xController.is())
        {
            uno::Reference<frame::XModel> xModel(xController, uno::UNO_QUERY);
            if (xModel.is())
            {
                m_xTextDocument.set(xModel, uno::UNO_QUERY);
            }
        }
    }
    
    // Start the Python AI agent
    startPythonAgent();
    
    m_bInitialized = true;
    SAL_INFO("sw.aiagent", "AIAgentService initialized successfully");
}

void AIAgentService::startPythonAgent()
{
    SAL_INFO("sw.aiagent", "Starting Python AI agent");
    
    m_pPythonAgentThread = std::make_unique<std::thread>([this]() {
        try
        {
            // Get the path to the Python script
            OUString sLibreOfficePath;
            osl::Security aSecurity;
            aSecurity.getConfigDir(sLibreOfficePath);
            
            // Construct path to AI agent script
            OUString sPythonScript = sLibreOfficePath + "/sw/source/aiagent/ai_agent.py";
            
            // Convert to system path
            OUString sSystemPath;
            osl::FileBase::getSystemPathFromFileURL(sPythonScript, sSystemPath);
            
            // Create command line
            OUString sCommandLine = "python \"" + sSystemPath + "\" --port 8765";
            
            // Execute Python script
            oslProcess hProcess;
            oslProcessError eError = osl_executeProcess(
                sSystemPath.pData,
                nullptr, 0,
                osl_Process_HIDDEN | osl_Process_DETACHED,
                nullptr,
                nullptr,
                nullptr, 0,
                &hProcess
            );
            
            if (eError == osl_Process_E_None)
            {
                SAL_INFO("sw.aiagent", "Python AI agent started successfully");
            }
            else
            {
                SAL_WARN("sw.aiagent", "Failed to start Python AI agent: " << static_cast<int>(eError));
            }
        }
        catch (const std::exception& e)
        {
            SAL_WARN("sw.aiagent", "Exception starting Python agent: " << e.what());
        }
    });
    
    // Detach the thread
    if (m_pPythonAgentThread && m_pPythonAgentThread->joinable())
    {
        m_pPythonAgentThread->detach();
    }
}

void AIAgentService::stopPythonAgent()
{
    SAL_INFO("sw.aiagent", "Stopping Python AI agent");
    
    if (m_pPythonAgentThread)
    {
        // Note: In a production implementation, you would want to send a shutdown
        // command to the Python process instead of just detaching the thread
        m_pPythonAgentThread.reset();
    }
}

void AIAgentService::sendCommand(const OUString& sCommand)
{
    SAL_INFO("sw.aiagent", "Sending command to AI agent: " << sCommand);
    
    // Initialize Winsock
    WSADATA wsaData;
    int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0)
    {
        SAL_WARN("sw.aiagent", "WSAStartup failed: " << iResult);
        return;
    }
    
    // Create socket
    SOCKET ConnectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (ConnectSocket == INVALID_SOCKET)
    {
        SAL_WARN("sw.aiagent", "socket failed");
        WSACleanup();
        return;
    }
    
    // Setup address
    struct sockaddr_in server;
    server.sin_family = AF_INET;
    server.sin_port = htons(8765);
    inet_pton(AF_INET, "127.0.0.1", &server.sin_addr);
    
    // Connect to server
    iResult = connect(ConnectSocket, (SOCKADDR*)&server, sizeof(server));
    if (iResult == SOCKET_ERROR)
    {
        SAL_WARN("sw.aiagent", "connect failed");
        closesocket(ConnectSocket);
        WSACleanup();
        return;
    }
    
    // Prepare JSON message
    std::ostringstream jsonStream;
    jsonStream << "{\"command\":\"" << OUStringToOString(sCommand, RTL_TEXTENCODING_UTF8).getStr() << "\"}";
    std::string jsonMessage = jsonStream.str();
    
    // Send data
    iResult = send(ConnectSocket, jsonMessage.c_str(), static_cast<int>(jsonMessage.length()), 0);
    if (iResult == SOCKET_ERROR)
    {
        SAL_WARN("sw.aiagent", "send failed");
        closesocket(ConnectSocket);
        WSACleanup();
        return;
    }
    
    // Receive response
    char recvbuf[4096];
    iResult = recv(ConnectSocket, recvbuf, sizeof(recvbuf), 0);
    if (iResult > 0)
    {
        recvbuf[iResult] = '\0';
        SAL_INFO("sw.aiagent", "Received response: " << recvbuf);
    }
    else if (iResult == 0)
    {
        SAL_INFO("sw.aiagent", "Connection closed");
    }
    else
    {
        SAL_WARN("sw.aiagent", "recv failed");
    }
    
    // Cleanup
    closesocket(ConnectSocket);
    WSACleanup();
}

void AIAgentService::processTextSelection(const OUString& sOperation)
{
    SAL_INFO("sw.aiagent", "Processing text selection with operation: " << sOperation);
    sendCommand(sOperation);
}

bool AIAgentService::isAgentRunning() const
{
    return m_pPythonAgentThread != nullptr;
}

// Static methods
OUString AIAgentService::getImplementationName_Static()
{
    return "com.sun.star.comp.Writer.AIAgentService";
}

uno::Sequence<OUString> AIAgentService::getSupportedServiceNames_Static()
{
    return { "com.sun.star.text.AIAgent" };
}

uno::Reference<uno::XInterface> AIAgentService::create(
    const uno::Reference<uno::XComponentContext>& /*xContext*/)
{
    return static_cast<cppu::OWeakObject*>(new AIAgentService());
}

} // namespace sw::aiagent

extern "C" SAL_DLLPUBLIC_EXPORT uno::XInterface*
com_sun_star_comp_Writer_AIAgentService_get_implementation(
    uno::XComponentContext* /*pCtx*/,
    uno::Sequence<uno::Any> const& /*rSeq*/)
{
    return cppu::acquire(new sw::aiagent::AIAgentService());
}

/* vim:set shiftwidth=4 softtabstop=4 expandtab: */