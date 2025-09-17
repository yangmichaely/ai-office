/* -*- Mode: C++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
/*
 * This file is part of the LibreOffice project.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

#ifndef INCLUDED_SW_SOURCE_AIAGENT_AIAGENTSERVICE_HXX
#define INCLUDED_SW_SOURCE_AIAGENT_AIAGENTSERVICE_HXX

#include <com/sun/star/lang/XServiceInfo.hpp>
#include <com/sun/star/uno/XInterface.hpp>
#include <com/sun/star/lang/XInitialization.hpp>
#include <com/sun/star/frame/XFrame.hpp>
#include <com/sun/star/text/XTextDocument.hpp>
#include <com/sun/star/beans/XPropertySet.hpp>
#include <cppuhelper/implbase.hxx>
#include <cppuhelper/supportsservice.hxx>
#include <rtl/ustring.hxx>

#include <memory>
#include <thread>

namespace sw::aiagent {

class AIAgentService : public cppu::WeakImplHelper<
    css::lang::XServiceInfo,
    css::lang::XInitialization>
{
private:
    css::uno::Reference<css::frame::XFrame> m_xFrame;
    css::uno::Reference<css::text::XTextDocument> m_xTextDocument;
    std::unique_ptr<std::thread> m_pPythonAgentThread;
    bool m_bInitialized;
    
    void startPythonAgent();
    void stopPythonAgent();
    
public:
    AIAgentService();
    virtual ~AIAgentService() override;
    
    // XServiceInfo
    virtual OUString SAL_CALL getImplementationName() override;
    virtual sal_Bool SAL_CALL supportsService(const OUString& rServiceName) override;
    virtual css::uno::Sequence<OUString> SAL_CALL getSupportedServiceNames() override;
    
    // XInitialization
    virtual void SAL_CALL initialize(const css::uno::Sequence<css::uno::Any>& aArguments) override;
    
    // Service registration
    static OUString getImplementationName_Static();
    static css::uno::Sequence<OUString> getSupportedServiceNames_Static();
    static css::uno::Reference<css::uno::XInterface> create(
        const css::uno::Reference<css::uno::XComponentContext>& xContext);
    
    // AI Agent functionality
    void sendCommand(const OUString& sCommand);
    void processTextSelection(const OUString& sOperation);
    bool isAgentRunning() const;
};

} // namespace sw::aiagent

#endif

/* vim:set shiftwidth=4 softtabstop=4 expandtab: */