import PropTypes from 'prop-types';
import useAutoScroll from '../../hooks/useAutoScroll';
import { CircleErrorIcon, CircleUserIcon, Spinner } from '../icons';
import './chatMessages.css';
import Markdown from 'react-markdown';

function ChatMessages({ messages, isLoading }) {
    const scrollContentRef = useAutoScroll(isLoading);

    return (
        <div className={`chat-content ${!messages.length ? "center-content" : ""}`}>
            {messages.length === 0 ? (
                <div className="welcome-container">
                    <h1>How can I help you today?</h1>
                    <p className="subtitle">Ask me anything...</p>
                </div>
            ) : (
                <div ref={scrollContentRef} className='scroll-content'>
                    {messages.map(({ role, content, loading, error }, idx) => (
                        <div key={idx} className={`message`}>
                            {/* {role === 'user' && <CircleUserIcon />} */}
                            {/* <div> */}
                            {/* <div>
                                {(loading && !content) ? <Spinner size='40' />
                                    : (role === 'assistant')
                                        ? <div>{content}</div>
                                        : <div className='whitespace-pre-line'>{content}</div>
                                }
                            </div> */}
                            {
                                role === 'user' ? (
                                    <div className='user-message'>
                                        {content}
                                    </div>
                                ) : role === 'assistant' ? (
                                    (loading && !content) ? <Spinner color='#007bff' /> : <div className='assistant-message'>
                                        <Markdown>{content}</Markdown>
                                    </div>
                                ) : null
                            }
                            {error && (
                                <div className={`error ${content && 'mt-2'}`}>
                                    <CircleErrorIcon />
                                    <span>Error generating the response</span>
                                </div>
                            )}
                        </div>
                        // </div>
                    ))}
                </div>
            )
            }
        </div >

    );
}

ChatMessages.propTypes = {
    messages: PropTypes.arrayOf(
        PropTypes.shape({
            role: PropTypes.string.isRequired,
            content: PropTypes.string,
            loading: PropTypes.bool,
            error: PropTypes.bool,
        })
    ).isRequired,
    isLoading: PropTypes.bool.isRequired,
};

export default ChatMessages;