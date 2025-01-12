import React, { useState } from 'react';
import './Sidebar.css';
import { assets } from '../../../assets/assets';
import Button from '../Button';
import { HelpIcon, MinusIcon, MoreIcon, PlusIcon, SettingsIcon } from "../../icons"

export default function Sidebar({ hidden, setHidden }) {

    // const [hidden, setHidden] = useState(false);
    const [recentChats, setRecentChats] = useState([
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
        {
            title: "What is React ???"
        },
    ]);

    return (
        <aside className={`sidebar ${hidden ? 'hide__sidebar' : ''}`}>
            <div className="sidebar__header">
                <div className="sidebar__header-logo">
                    <img src={assets.logo} alt="" />
                </div>
                <div className="sidebar__header-icon">
                    <MinusIcon onClick={() => setHidden(true)
                    } />
                </div>
            </div>
            <div className="sidebar__button-container">
                <Button size='sm' className="sidebar__button">
                    <PlusIcon />
                    {"New Chat"}</Button>
            </div>
            {/* <div className="sidebar__chat-list-container"> */}
            <div className="sidebar__chat-list">
                <div className="sidebar__chat-header">{"Recent Chats"}</div>
                <div className="sidebar__chat-items">
                    {
                        recentChats.map((chat, index) => {
                            return (
                                <div className="sidebar__chat-item" key={index}>
                                    <span>{chat.title}</span>
                                    <Button variant='ghost' size='sm' className="sidebar__chat-item-button"><MoreIcon /></Button>
                                </div>
                            )
                        })
                    }
                </div>
            </div>
            {/* </div> */}
            <div className="sidebar__footer">
                <Button variant='ghost' size='sm' className="sidebar__footer-button"><SettingsIcon />{"Settings"}</Button>
                <Button variant='ghost' size='sm' className="sidebar__footer-button"><HelpIcon />{"Help & FAQs"}</Button>
            </div>
        </aside>
    )
}

// const Sidebar = () => {

//     const [extended, setExtended] = useState(false)
//     return (
//         <div className={`sidebar ${extended ? 'extended' : ''}`}>
//             <div className="top">
//                 <img onClick={() => setExtended(prev => !prev)} className="menu" src={assets.menu_icon} alt="" />
//                 <div className="new-chat">
//                     <img src={assets.plus_icon} alt="" />
//                     {extended ? <p>New Chat</p> : null}
//                 </div>
//                 {extended ?
//                     <div className="recent">
//                         <p className="recent-title">Recent Chats</p>
//                         <div className="recent-entry">
//                             <img src={assets.message_icon} alt="" />
//                             <p>What is React ????</p>
//                         </div>
//                     </div>
//                     : null
//                 }
//             </div>
//             <div className="bottom">
//                 <div className="bottom-item recent-entry">
//                     <img src={assets.question_icon} alt="" />
//                     {extended ? <p>Help</p> : null}
//                 </div>
//                 <div className="bottom-item recent-entry">
//                     <img src={assets.history_icon} alt="" />
//                     {extended ? <p>Activity</p> : null}
//                 </div>
//                 <div className="bottom-item recent-entry">
//                     <img src={assets.setting_icon} alt="" />
//                     {extended ? <p>Settings</p> : null}
//                 </div>
//             </div>
//         </div>
//     );
// };

// export default Sidebar;
