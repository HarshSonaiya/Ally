import { useCallback, useContext, useRef, useState } from 'react';
import useAutosize from '../../hooks/useAutosize';
import { GlobeIcon, PaperclipIcon, SendIcon } from '../icons';
import Button from '../ui/Button';
import "./chatInput.css";
import PropTypes from 'prop-types';
import { X, FileText } from 'lucide-react';
import { Popover, PopoverRoot, PopoverTrigger } from '../ui/Popover';
import { ChatContext } from '../../context/ChatContext.jsx';
import { uploadFiles } from '../../Api/handlers/chatHandler.js';
import { toast } from 'react-toastify';

function ChatInput({ newMessage, setNewMessage, messages, isLoading, submitNewMessage }) {

    const [isWebSearch, setIsWebSearch] = useState(false);

    const textareaRef = useAutosize(newMessage);
    const { fileRef } = useContext(ChatContext);

    function handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
            e.preventDefault();
            submitNewMessage(isWebSearch);
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
                        {/* <Button
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
                        </Button> */}
                        <FileUpload fileRef={fileRef} />
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

function FileUpload({ fileRef }) {
    const [files, setFiles] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [error, setError] = useState('');

    const { currentProject } = useContext(ChatContext);

    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

    const handleFileChange = useCallback(async (event) => {
        const selectedFiles = Array.from(event.target.files);
        setError('');

        // Validate file size
        const oversizedFiles = selectedFiles.filter(file => file.size > MAX_FILE_SIZE);
        if (oversizedFiles.length > 0) {
            setError('Some files exceed the 10MB limit');
            return;
        }

        setFiles(prevFiles => [...prevFiles, ...selectedFiles]);
    }, []);

    const removeFile = useCallback((index) => {
        setFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
    }, []);

    const onFileSelect = useCallback((files) => {
        fileRef.current = files;
    }, []);

    console.log("Files: ", files);


    const handleSubmit = useCallback(async () => {
        onFileSelect(files);
        setIsOpen(false);
        setFiles([]);
        const response = await uploadFiles(files, currentProject.value);
        console.log("response: ", response);
        alert(response.data)

        if (response) {
            toast.success('Files uploaded successfully. Summary has been send to your email');
        } else {
            toast.error('Failed to upload files');
        }

    }, [files, onFileSelect]);

    return (
        <PopoverRoot className="file-upload__popover-root">
            <PopoverTrigger onClick={() => setIsOpen(!isOpen)}>
                <Button
                    variant="ghost"
                    size="icon"
                    className="file-upload__button"
                >
                    <PaperclipIcon height="20" width="20" />
                </Button>
            </PopoverTrigger>

            <Popover
                visible={isOpen}
                onClose={() => setIsOpen(false)}
                align="center"
                className="file-upload__popover"
            >
                <div className="file-upload__content">
                    <div className="file-upload__header">
                        <h3 className="file-upload__title">Upload Files</h3>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setIsOpen(false)}
                            className="file-upload__button-close"
                        >
                            <X className="file-upload__icon-close" />
                        </Button>
                    </div>

                    <div className="file-upload__body">
                        {/* {error && (
                            <Alert variant="destructive" className="file-upload__alert-error">
                                <AlertTitle>{error}</AlertTitle>
                            </Alert>
                        )} */}

                        <div className="file-upload__area">
                            <div className="file-upload__input">
                                <label className="file-upload__label">
                                    <div className="file-upload__icon-text">
                                        <PaperclipIcon height="20" width="20" />
                                        <p className="file-upload__upload-text">
                                            <span className="file-upload__upload-text-bold">Click to upload</span> or drag and drop
                                        </p>
                                        <p className="file-upload__upload-text-small">PDF, Images (max 10MB)</p>
                                    </div>
                                    <input
                                        type="file"
                                        className="file-upload__input-hidden"
                                        multiple
                                        accept=".mp4, .wav"
                                        onChange={handleFileChange}
                                    />
                                </label>
                            </div>

                            {files.length > 0 && (
                                <div className="file-upload__file-list">
                                    {files.map((file, index) => (
                                        <div
                                            key={index}
                                            className="file-upload__file-item"
                                        >
                                            <div className="file-upload__file-info">
                                                <FileText className="file-upload__icon" />
                                                <span className="file-upload__file-name">{file.name}</span>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => removeFile(index)}
                                                className="file-upload__button-remove"
                                            >
                                                <X className="file-upload__icon-remove" />
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="file-upload__footer">
                        <Button
                            variant="outline"
                            onClick={() => setIsOpen(false)}
                            size='sm'
                        // className="file-upload__button-cancel"
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handleSubmit}
                            disabled={files.length === 0}
                            size='sm'
                        // className="file-upload__button-upload"
                        >
                            Upload
                        </Button>
                    </div>
                </div>
            </Popover>
        </PopoverRoot>
    );
}

// function FileUpload({ fileRef }) {
//     const [isPopoverVisible, setPopoverVisible] = useState(false);

//     function handleOpenPopover() {
//         setPopoverVisible(true); // Show the popover when button is clicked
//     }

//     const handleClosePopover = () => {
//         setPopoverVisible(false); // Close popover when clicking outside or on close action
//     };

//     return (
//         <PopoverRoot>
//             <PopoverTrigger>
//                 <Button size="sm" onClick={handleOpenPopover}>
//                     {/* <PlusIcon /> */}
//                     <PaperclipIcon height='20' width='20' />
//                 </Button>
//             </PopoverTrigger>

//             <Popover
//                 isOpen={isPopoverVisible}
//                 onClose={handleClosePopover}
//                 align="top-right"
//                 offset={50}
//                 className="mainsection-popover"
//             >
//                 <PopoverContent className="mainsection-popover-content">
//                     <PopoverTitle>Create a New Project</PopoverTitle>
//                     <label htmlFor="file-upload">
//                         <input
//                             type="file"
//                             id="file-upload"
//                             accept=".pdf, .mp4, .wav"
//                             style={{ display: 'none' }}
//                             ref={fileRef}
//                         />
//                     </label>
//                 </PopoverContent>

//                 <PopoverFooter className="mainsection-popover-footer">
//                     <PopoverAction >
//                         <Button size='sm'>Create Project</Button>
//                     </PopoverAction>
//                 </PopoverFooter>
//             </Popover>
//         </PopoverRoot>
//     );
// }

export default ChatInput;