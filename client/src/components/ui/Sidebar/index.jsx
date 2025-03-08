import React, { useContext, useEffect, useState } from 'react';
import './Sidebar.css';
import { assets } from '../../../assets/assets';
import Button from '../Button';
import { HelpIcon, MinusIcon, MoreIcon, PlusIcon, SettingsIcon } from "../../icons"
import { useNavigate } from 'react-router-dom';
import { logout } from '../../../Api/handlers/authHandler';
import { ChatContext } from '../../../context/ChatContext';
import { listFiles } from '../../../Api/handlers/chatHandler';
import { toast } from 'react-toastify';

export default function Sidebar({ hidden, setHidden }) {

    const { files, setFiles, currentProject } = useContext(ChatContext)

    const navigate = useNavigate();

    async function handleLogout() {
        const response = await logout();

        console.log('response: ', response);

        if (response.error) {
            localStorage.removeItem('access_token');
            navigate('/');
            toast.error('Failed to logout. You have been logged out automatically');
        }

        if (!response.success) {
            localStorage.removeItem('access_token');
            navigate('/');
            toast.error('Failed to logout. You have been logged out automatically');
        }

        localStorage.removeItem('access_token');
        navigate('/');
        toast.success('Logged out successfully!');

    }

    // const [hidden, setHidden] = useState(false);

    useEffect(() => {
        async function list() {

            if (!currentProject) {
                return;
            }

            const response = await listFiles(currentProject.value);

            console.log("file response: ", response.data);
            

            if (response.success) {
                setFiles(() => response.data);
            }
        }

        list()
    }, [currentProject]);

    useEffect(() => {
        console.log('files: ', files);
        
    }, [files])

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
            {/* <div className="sidebar__button-container">
                <Button size='sm' className="sidebar__button">
                    <PlusIcon />
                    {"New Chat"}</Button>
            </div> */}
            {/* <div className="sidebar__chat-list-container"> */}
            {/* <div className="sidebar__chat-list">
                <div className="sidebar__chat-header">{"Recent Chats"}</div>
                <div className="sidebar__chat-items">
                    {
                        recentChats?.length > 0 ?
                            recentChats.map((chat, index) => {
                                return (
                                    <div className="sidebar__chat-item" key={index}>
                                        <span>{chat.title}</span>
                                        <Button variant='ghost' size='sm' className="sidebar__chat-item-button"><MoreIcon /></Button>
                                    </div>
                                )
                            }) : null
                    }
                </div>
            </div> */}
            <div className="sidebar__chat-list">
                <div className="sidebar__chat-header">{"Uploaded Files"}</div>
                <div className="sidebar__chat-items">
                    {files?.length > 0 ?
                        files.map((file, index) => {
                            return (
                                <div className="sidebar__chat-item" key={index}>
                                    <span>{file}</span>
                                    <Button variant='ghost' size='sm' className="sidebar__chat-item-button"><MoreIcon /></Button>
                                </div>
                            )
                        }) : <span className='file-err-msg'>No files found. Upload files to chat with them or use General chat.</span>
                    }
                </div>
            </div>
            {/* </div> */}
            <div className="sidebar__footer">
                <Button variant='ghost' size='sm' onClick={handleLogout} className="sidebar__footer-button">{"Logout"}</Button>
                <Button variant='ghost' size='sm' className="sidebar__footer-button" onClick={() => navigate('/')}>{"Home"}</Button>
                <Button variant='ghost' size='sm' className="sidebar__footer-button" onClick={() => navigate('/playground')}>{"Playground"}</Button>
                {/* <Button variant='ghost' size='sm' className="sidebar__footer-button"><HelpIcon />{"Help & FAQs"}</Button> */}
            </div>
        </aside >
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
