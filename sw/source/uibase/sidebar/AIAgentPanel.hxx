/* -*- Mode: C++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
/*
 * This file is part of the LibreOffice project.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

#ifndef INCLUDED_SW_SOURCE_AIAGENT_AIAGENTPANEL_HXX
#define INCLUDED_SW_SOURCE_AIAGENT_AIAGENTPANEL_HXX

#include <sfx2/sidebar/PanelLayout.hxx>
#include <sfx2/sidebar/ControllerItem.hxx>
#include <com/sun/star/frame/XFrame.hpp>
#include <vcl/weld.hxx>
#include <memory>

namespace sw::aiagent { class AIAgentService; }

namespace sw::sidebar {

class AIAgentPanel final : public PanelLayout,
                          public ::sfx2::sidebar::ControllerItem::ItemUpdateReceiverInterface
{
public:
    static std::unique_ptr<PanelLayout> Create(
        weld::Widget* pParent,
        const css::uno::Reference<css::frame::XFrame>& rxFrame,
        SfxBindings* pBindings);

    AIAgentPanel(
        weld::Widget* pParent,
        const css::uno::Reference<css::frame::XFrame>& rxFrame,
        SfxBindings* pBindings);

    virtual ~AIAgentPanel() override;

    // From ControllerItem::ItemUpdateReceiverInterface
    virtual void NotifyItemUpdate(const sal_uInt16 nSId, const SfxItemState eState,
                                 const SfxPoolItem* pState) override;

    virtual void GetControlState(const sal_uInt16 /*nSId*/,
                                boost::property_tree::ptree& /*rState*/) override {}

private:
    css::uno::Reference<css::frame::XFrame> m_xFrame;
    SfxBindings* m_pBindings;
    
    // UI controls
    std::unique_ptr<weld::TextView> m_xChatHistory;
    std::unique_ptr<weld::Entry> m_xCommandEntry;
    std::unique_ptr<weld::Button> m_xSendButton;
    std::unique_ptr<weld::Button> m_xClearButton;
    std::unique_ptr<weld::Label> m_xStatusLabel;
    
    // Quick action buttons
    std::unique_ptr<weld::Button> m_xRewriteButton;
    std::unique_ptr<weld::Button> m_xSummarizeButton;
    std::unique_ptr<weld::Button> m_xExpandButton;
    std::unique_ptr<weld::Button> m_xCorrectButton;
    
    // AI Agent service
    css::uno::Reference<css::uno::XInterface> m_xAIAgentService;
    
    void Initialize();
    void setupUIControls();
    void connectEventHandlers();
    
    // Event handlers
    DECL_LINK(SendCommandHdl, weld::Button&, void);
    DECL_LINK(ClearHistoryHdl, weld::Button&, void);
    DECL_LINK(CommandEntryActivateHdl, weld::Entry&, bool);
    DECL_LINK(RewriteHdl, weld::Button&, void);
    DECL_LINK(SummarizeHdl, weld::Button&, void);
    DECL_LINK(ExpandHdl, weld::Button&, void);
    DECL_LINK(CorrectHdl, weld::Button&, void);
    
    void sendCommand();
    void executeQuickCommand(const OUString& sCommand);
    void addToHistory(const OUString& sMessage, bool bIsUser = true);
    void updateStatus(const OUString& sStatus);
    void clearHistory();
};

} // end of namespace sw::sidebar

#endif

/* vim:set shiftwidth=4 softtabstop=4 expandtab: */