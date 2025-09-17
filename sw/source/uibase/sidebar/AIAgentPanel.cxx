/* -*- Mode: C++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
/*
 * This file is part of the LibreOffice project.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

#include "AIAgentPanel.hxx"
#include "../aiagent/AIAgentService.hxx"

#include <comphelper/processfactory.hxx>
#include <sfx2/bindings.hxx>
#include <sfx2/sidebar/ControllerFactory.hxx>
#include <vcl/svapp.hxx>
#include <vcl/settings.hxx>
#include <sal/log.hxx>

using namespace css;

namespace sw::sidebar {

std::unique_ptr<PanelLayout> AIAgentPanel::Create(
    weld::Widget* pParent,
    const css::uno::Reference<css::frame::XFrame>& rxFrame,
    SfxBindings* pBindings)
{
    if (pParent == nullptr)
        throw lang::IllegalArgumentException("no parent Window given to AIAgentPanel::Create", nullptr, 0);
    if (!rxFrame.is())
        throw lang::IllegalArgumentException("no XFrame given to AIAgentPanel::Create", nullptr, 1);
    if (pBindings == nullptr)
        throw lang::IllegalArgumentException("no SfxBindings given to AIAgentPanel::Create", nullptr, 2);

    return std::make_unique<AIAgentPanel>(pParent, rxFrame, pBindings);
}

AIAgentPanel::AIAgentPanel(
    weld::Widget* pParent,
    const css::uno::Reference<css::frame::XFrame>& rxFrame,
    SfxBindings* pBindings)
    : PanelLayout(pParent, "AIAgentPanel", "sw/ui/aiagentpanel.ui")
    , m_xFrame(rxFrame)
    , m_pBindings(pBindings)
{
    SAL_INFO("sw.sidebar", "AIAgentPanel constructor");
    Initialize();
}

AIAgentPanel::~AIAgentPanel()
{
    SAL_INFO("sw.sidebar", "AIAgentPanel destructor");
}

void AIAgentPanel::Initialize()
{
    setupUIControls();
    connectEventHandlers();
    
    // Initialize AI Agent Service
    try
    {
        uno::Reference<uno::XComponentContext> xContext = comphelper::getProcessComponentContext();
        m_xAIAgentService = sw::aiagent::AIAgentService::create(xContext);
        
        if (m_xAIAgentService.is())
        {
            // Initialize the service with frame
            uno::Reference<lang::XInitialization> xInit(m_xAIAgentService, uno::UNO_QUERY);
            if (xInit.is())
            {
                uno::Sequence<uno::Any> aArgs(1);
                aArgs[0] <<= m_xFrame;
                xInit->initialize(aArgs);
            }
            
            updateStatus(u"AI Agent ready"_ustr);
        }
        else
        {
            updateStatus(u"Failed to initialize AI Agent"_ustr);
        }
    }
    catch (const uno::Exception& e)
    {
        SAL_WARN("sw.sidebar", "Exception initializing AI Agent: " << e.Message);
        updateStatus(u"AI Agent initialization error"_ustr);
    }
}

void AIAgentPanel::setupUIControls()
{
    m_xChatHistory = m_xBuilder->weld_text_view("chat_history");
    m_xCommandEntry = m_xBuilder->weld_entry("command_entry");
    m_xSendButton = m_xBuilder->weld_button("send_button");
    m_xClearButton = m_xBuilder->weld_button("clear_button");
    m_xStatusLabel = m_xBuilder->weld_label("status_label");
    
    // Quick action buttons
    m_xRewriteButton = m_xBuilder->weld_button("rewrite_button");
    m_xSummarizeButton = m_xBuilder->weld_button("summarize_button");
    m_xExpandButton = m_xBuilder->weld_button("expand_button");
    m_xCorrectButton = m_xBuilder->weld_button("correct_button");
    
    // Configure chat history
    if (m_xChatHistory)
    {
        m_xChatHistory->set_editable(false);
        m_xChatHistory->set_wrap(true);
        m_xChatHistory->set_size_request(-1, 200);
    }
    
    // Configure command entry
    if (m_xCommandEntry)
    {
        m_xCommandEntry->set_placeholder_text(u"Enter AI command (e.g., 'rewrite in simpler words')"_ustr);
    }
    
    // Set initial status
    updateStatus(u"Initializing AI Agent..."_ustr);
}

void AIAgentPanel::connectEventHandlers()
{
    if (m_xSendButton)
        m_xSendButton->connect_clicked(LINK(this, AIAgentPanel, SendCommandHdl));
    
    if (m_xClearButton)
        m_xClearButton->connect_clicked(LINK(this, AIAgentPanel, ClearHistoryHdl));
    
    if (m_xCommandEntry)
        m_xCommandEntry->connect_activate(LINK(this, AIAgentPanel, CommandEntryActivateHdl));
    
    // Quick action buttons
    if (m_xRewriteButton)
        m_xRewriteButton->connect_clicked(LINK(this, AIAgentPanel, RewriteHdl));
    
    if (m_xSummarizeButton)
        m_xSummarizeButton->connect_clicked(LINK(this, AIAgentPanel, SummarizeHdl));
    
    if (m_xExpandButton)
        m_xExpandButton->connect_clicked(LINK(this, AIAgentPanel, ExpandHdl));
    
    if (m_xCorrectButton)
        m_xCorrectButton->connect_clicked(LINK(this, AIAgentPanel, CorrectHdl));
}

IMPL_LINK_NOARG(AIAgentPanel, SendCommandHdl, weld::Button&, void)
{
    sendCommand();
}

IMPL_LINK_NOARG(AIAgentPanel, ClearHistoryHdl, weld::Button&, void)
{
    clearHistory();
}

IMPL_LINK_NOARG(AIAgentPanel, CommandEntryActivateHdl, weld::Entry&, bool)
{
    sendCommand();
    return true;
}

IMPL_LINK_NOARG(AIAgentPanel, RewriteHdl, weld::Button&, void)
{
    executeQuickCommand(u"rewrite this text to be clearer and better"_ustr);
}

IMPL_LINK_NOARG(AIAgentPanel, SummarizeHdl, weld::Button&, void)
{
    executeQuickCommand(u"summarize this text"_ustr);
}

IMPL_LINK_NOARG(AIAgentPanel, ExpandHdl, weld::Button&, void)
{
    executeQuickCommand(u"expand this text with more details"_ustr);
}

IMPL_LINK_NOARG(AIAgentPanel, CorrectHdl, weld::Button&, void)
{
    executeQuickCommand(u"correct grammar and spelling in this text"_ustr);
}

void AIAgentPanel::sendCommand()
{
    if (!m_xCommandEntry || !m_xAIAgentService.is())
        return;
    
    OUString sCommand = m_xCommandEntry->get_text().trim();
    if (sCommand.isEmpty())
        return;
    
    // Clear the entry
    m_xCommandEntry->set_text(u""_ustr);
    
    executeQuickCommand(sCommand);
}

void AIAgentPanel::executeQuickCommand(const OUString& sCommand)
{
    if (!m_xAIAgentService.is())
        return;
    
    // Add user command to history
    addToHistory(u"User: "_ustr + sCommand, true);
    
    // Update status
    updateStatus(u"Processing command..."_ustr);
    
    try
    {
        // Send command to AI Agent Service
        uno::Reference<sw::aiagent::AIAgentService> xAgent(m_xAIAgentService, uno::UNO_QUERY);
        if (xAgent.is())
        {
            xAgent->sendCommand(sCommand);
            
            // Add response placeholder to history
            addToHistory(u"AI: Command sent to agent. Check document for changes."_ustr, false);
            updateStatus(u"Command processed"_ustr);
        }
        else
        {
            addToHistory(u"AI: Error - Agent service not available"_ustr, false);
            updateStatus(u"Agent service error"_ustr);
        }
    }
    catch (const uno::Exception& e)
    {
        OUString sError = u"AI: Error processing command: "_ustr + e.Message;
        addToHistory(sError, false);
        updateStatus(u"Command failed"_ustr);
        SAL_WARN("sw.sidebar", "Exception sending command: " << e.Message);
    }
}

void AIAgentPanel::addToHistory(const OUString& sMessage, bool bIsUser)
{
    if (!m_xChatHistory)
        return;
    
    // Get current text
    OUString sCurrentText = m_xChatHistory->get_text();
    
    // Add timestamp
    css::util::DateTime aDateTime;
    // For simplicity, just add the message without timestamp for now
    OUString sFormattedMessage = sMessage + u"\n\n"_ustr;
    
    // Append to history
    if (!sCurrentText.isEmpty())
        sCurrentText += sFormattedMessage;
    else
        sCurrentText = sFormattedMessage;
    
    m_xChatHistory->set_text(sCurrentText);
    
    // Scroll to bottom
    m_xChatHistory->select_region(sCurrentText.getLength(), sCurrentText.getLength());
}

void AIAgentPanel::updateStatus(const OUString& sStatus)
{
    if (m_xStatusLabel)
        m_xStatusLabel->set_label(sStatus);
}

void AIAgentPanel::clearHistory()
{
    if (m_xChatHistory)
        m_xChatHistory->set_text(u""_ustr);
}

void AIAgentPanel::NotifyItemUpdate(const sal_uInt16 /*nSId*/, const SfxItemState /*eState*/,
                                   const SfxPoolItem* /*pState*/)
{
    // Handle item updates if needed
}

} // end of namespace sw::sidebar

/* vim:set shiftwidth=4 softtabstop=4 expandtab: */