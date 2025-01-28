import { useRef, useState } from 'react';
import useAutosize from '../../hooks/useAutosize';
import { GlobeIcon, PaperclipIcon, SendIcon } from '../icons';
import Button from '../ui/Button';
import "./chatInput.css";
import PropTypes from 'prop-types';

function ChatInput({ newMessage, setNewMessage, messages, isLoading, submitNewMessage }) {

    const [isWebSearch, setIsWebSearch] = useState(false);

    const textareaRef = useAutosize(newMessage);
    const fileRef = useRef(null);

    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
            e.preventDefault();
            submitNewMessage();
        }
    }

    return (
        // <div className='sticky bottom-0 bg-white py-4'>
        //     <div className='p-1.5 bg-primary-blue/35 rounded-3xl z-50 font-mono origin-bottom animate-chat duration-400'>
        //         <div className='pr-0.5 bg-white relative shrink-0 rounded-3xl overflow-hidden ring-primary-blue ring-1 focus-within:ring-2 transition-all'>
        //             <textarea
        //                 className='block w-full max-h-[140px] py-2 px-4 pr-11 bg-white rounded-3xl resize-none placeholder:text-primary-blue placeholder:leading-4 placeholder:-translate-y-1 sm:placeholder:leading-normal sm:placeholder:translate-y-0 focus:outline-none'
        //                 ref={textareaRef}
        //                 rows='1'
        //                 value={newMessage}
        //                 onChange={e => setNewMessage(e.target.value)}
        //                 onKeyDown={handleKeyDown}
        //             />
        //             <button
        //                 className='absolute top-1/2 -translate-y-1/2 right-3 p-1 rounded-md hover:bg-primary-blue/20'
        //                 onClick={submitNewMessage}
        //             >
        //                 <SendIcon height='20' width='20' />
        //             </button>
        //         </div>
        //     </div>
        // </div>
        <div className={`chat-input-wrapper ${!messages.length ? "center-position" : ""}`}>
            <div className="chat-input-container">
                <textarea
                    className="chat-input"
                    placeholder="Send a message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    rows={1}
                    ref={textareaRef}
                    onKeyDown={handleKeyDown}
                />
                <div className="send-button-wrapper">

                    <div className="button-group">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="attachment-button"
                        >
                            <label htmlFor="file-upload">
                                <input
                                    type="file"
                                    id="file-upload"
                                    accept=".pdf, .mp4, .wav"
                                    style={{ display: 'none' }}
                                    ref={fileRef}
                                />
                                <PaperclipIcon height='20' width='20' />
                            </label>
                        </Button>

                        <Button variant="ghost" size="icon" onClick={() => setIsWebSearch(!isWebSearch)} className={`web-search-button ${isWebSearch ? 'active' : ''}`} >
                            <GlobeIcon height="20" width="20" style={{ stroke: isWebSearch ? '#3F00FF' : '#000000' }} />
                        </Button>

                    </div>

                    <Button
                        variant="ghost"
                        size="icon"
                        className="send-button"
                        onClick={submitNewMessage}
                        type="submit"
                    >
                        <SendIcon height='20' width='20' />
                    </Button>
                </div>
            </div>
        </div>
    );
}
ChatInput.propTypes = {
    newMessage: PropTypes.string.isRequired,
    messages: PropTypes.array.isRequired,
    isLoading: PropTypes.bool.isRequired,
    setNewMessage: PropTypes.func.isRequired,
    submitNewMessage: PropTypes.func.isRequired,
};

export default ChatInput;