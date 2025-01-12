import SidepanelIcon from '../icons/SidepanelIcon';
import PlusIcon from '../icons/PlusIcon';
import { useState } from "react";
import Button from "../ui/Button";
import "./mainSection.css";
import PropTypes from 'prop-types';

export default function MainSection({ hidden, setHidden }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setMessages([...messages, { text: inputText, type: "user" }]);
    setInputText("");
  };

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
      </div>
      <div className={`chat-input-wrapper ${!messages.length ? "center-position" : ""}`}>
        <form onSubmit={handleSubmit} className="chat-input-container">
          <textarea
            className="chat-input styled-textarea"
            placeholder="Send a message..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
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
    </section>
  );
}

MainSection.propTypes = {
  hidden: PropTypes.bool.isRequired,
  setHidden: PropTypes.func.isRequired,
};