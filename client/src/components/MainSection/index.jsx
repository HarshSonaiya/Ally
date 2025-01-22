import SidepanelIcon from '../icons/SidepanelIcon';
import PlusIcon from '../icons/PlusIcon';
import { useEffect, useState } from "react";
import Button from "../ui/Button";
import "./mainSection.css";
import PropTypes from 'prop-types';
import ChatInput from '../ChatInput';
import ChatMessages from '../ChatMessages';

export default function MainSection({ hidden, setHidden }) {
  const [chatId, setChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages(prev => [...prev,
    { role: 'user', content: trimmedMessage },
    { role: 'assistant', content: '', sources: [], loading: true }
    ]);
    setNewMessage('');


    // let chatIdOrNew = chatId;
    // try {
    // if (!chatId) {
    //   const { id } = await api.createChat();
    //   setChatId(id);
    //   chatIdOrNew = id;
    // }

    setTimeout(() => {
      console.log(messages);

      setMessages(draft => {
        const updatedMessages = [...draft];
        updatedMessages[updatedMessages.length - 1].content = "Hello, how can I help you today?";
        return updatedMessages;
      });

      setMessages(draft => {
        const updatedMessages = [...draft];
        updatedMessages[updatedMessages.length - 1].loading = false;
        return updatedMessages;
      });

      // setMessages(prev => {
      //   prev[prev.length - 1].content = "Hello, how can I help you today?";
      // });
      // setMessages(prev => {
      //   prev[prev.length - 1].loading = false;
      // });
    }, 2000);
    // } catch (err) {
    //   console.log(err);
    //   setMessages(draft => {
    //     draft[draft.length - 1].loading = false;
    //     draft[draft.length - 1].error = true;
    //   });
    // }
  }

  useEffect(() => {
    console.log(messages);

  }, [messages]);

  // TODO: replace with actual API call
  /*
    async function submitNewMessage() {
      const trimmedMessage = newMessage.trim();
      if (!trimmedMessage || isLoading) return;
  
      setMessages(draft => [...draft,
      { role: 'user', content: trimmedMessage },
      { role: 'assistant', content: '', sources: [], loading: true }
      ]);
      setNewMessage('');
  
      // TODO: replace with actual API call
      let chatIdOrNew = chatId;
      try {
        if (!chatId) {
          const { id } = await api.createChat();
          setChatId(id);
          chatIdOrNew = id;
        }
  
        const stream = await api.sendChatMessage(chatIdOrNew, trimmedMessage);
        for await (const textChunk of parseSSEStream(stream)) {
          setMessages(draft => {
            draft[draft.length - 1].content += textChunk;
          });
        }
        setMessages(draft => {
          draft[draft.length - 1].loading = false;
        });
      } catch (err) {
        console.log(err);
        setMessages(draft => {
          draft[draft.length - 1].loading = false;
          draft[draft.length - 1].error = true;
        });
      }
    }
  */
  return (
    <section className="main-section">
      <div className="composer-parent">
        <div className="composer-header">
          {!!hidden && <Button variant="ghost" size='icon' onClick={() => setHidden(() => false)}>
            <SidepanelIcon className="sidepanel-icon" />
          </Button>}
          <h1>Chat with us</h1>
          <Button variant="ghost" size='icon'>
            <PlusIcon />
          </Button>
        </div>
        <ChatMessages messages={messages} isLoading={isLoading} />
      </div>
      <ChatInput newMessage={newMessage} setNewMessage={setNewMessage} messages={messages} isLoading={isLoading} submitNewMessage={submitNewMessage} />
    </section>
  );
}

MainSection.propTypes = {
  hidden: PropTypes.bool.isRequired,
  setHidden: PropTypes.func.isRequired,
};

/*
      <div className={`chat-input-wrapper ${!messages.length ? "center-position" : ""}`}>
        <form onSubmit={handleSubmit} className="chat-input-container">
          <textarea
            className="chat-input styled-textarea"
            placeholder="Send a message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            rows={1}
            style={{ height: !messages.length ? "60px" : "auto" }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
              }
            }}
          />
          <Button variant="ghost" size="icon" className="send-button" onClick={handleSubmit} type="submit">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </Button>
        </form>
      </div>
*/

/*
        <div className={`chat-content ${!messages.length ? "center-content" : ""}`}>
          {messages.length === 0 ? (
            <div className="welcome-container">
              <h1>How can I help you today?</h1>
              <p className="subtitle">Ask me anything...</p>
            </div>
          ) : (
            <div className="messages-container">
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.type}`}>
                  {message.text}
                </div>
              ))}
            </div>
          )}
        </div>
*/