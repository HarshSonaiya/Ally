import { useState, useRef, useEffect } from "react";
import "./PlaygroundPage.css";
import { ChevronRight, ChevronLeft, CornerDownLeft } from "lucide-react";
import Button from "../../components/ui/Button";
import Select from "react-select";
import { playgroundQuery } from "../../Api/handlers/chatHandler";
import Markdown from "react-markdown";

const models = [
  { value: "llama-3.1-8b-instant", label: "Llama 3.1 8B Instant" },
  { value: "llama-3.3-70b-specdec", label: "Llama 3.3 70B SpecDec" },
  { value: "llama-3.3-70b-versatile", label: "Llama 3.3 70B Versatile" },
  { value: "llama-3.2-3b-preview", label: "Llama 3.2 3B Preview" },
];

const PlaygroundPage = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [currentModel, setCurrentModel] = useState(models[0]);
  const [settings, setSettings] = useState({
    model: currentModel,
    temperature: 0.7,
    maxTokens: 5000,
    topP: 1,
    topK: 50,
  });
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const [currentMode, setCurrentMode] = useState("user");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputMessage]);

  const handleModeToggle = () => {
    setCurrentMode((prev) => (prev === "user" ? "assistant" : "user"));
    setInputMessage(currentMode === "user" ? "" : "");
  };

  const handleSend = async () => {
    const trimmedMessage = inputMessage.trim();
    if (!trimmedMessage) return;

    const userMessage = {
      role: currentMode,
      type: "user",
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsStreaming(true);

    const query = {
      model_name: currentModel.value,
      query_data: {
        [currentMode]: trimmedMessage,
      },
      max_tokens: settings.maxTokens,
      temperature: settings.temperature,
    }

    console.log("query: ", query);


    const response = await playgroundQuery(query);

    console.log("response: ", response);

    if (response.success) {
      const aiMessage = {
        role: "assistant",
        type: "assistant",
        content: response.data,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMessage]);
      setIsStreaming(false);
    } else {
      console.error("Error sending message: ", response.error);

      const aiMessage = {
        role: "assistant",
        type: "assistant",
        content: "Error sending message. Please try again.",
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMessage]);

      setIsStreaming(false);
    }


    // Simulate AI response
    // setTimeout(() => {
    //   const aiMessage = {
    //     role: "assistant",
    //     type: "assistant",
    //     content:
    //       "This is a simulated response. Replace with actual Groq API integration. THis is me whate i need to do is just a classsification ins the situaikon wiehtou aannhy tThis is a simulated response. Replace with actual Groq API integration. THis is me whate i need to do is just a classsification ins the situaikon wiehtou aannhy t",
    //     timestamp: new Date().toISOString(),
    //   };
    //   setMessages((prev) => [...prev, aiMessage]);
    //   setIsStreaming(false);
    // }, 1000);
  };

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="playground-container">
      <main className={`chat-main ${!isSidebarOpen ? "sidebar-closed" : ""}`}>
        <div className="chat-messages">
          {messages.length > 0 ? messages.map((message, index) => (
            <div key={index} className={`pg-message ${message.type}`}>
              <div className="message-content"><Markdown>{message.content}</Markdown></div>
              {message.type === "user" && (
                <div className="message-header">
                  <span className="message-role">{message.role}</span>
                  <span className="message-time">{new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
              )}
              {/* {message.metrics && (
                  <div className="message-metrics">
                    <span>First token: {message.metrics.timeToFirstToken}</span>
                    <span>Total time: {message.metrics.totalTime}</span>
                    <span>Tokens: {message.metrics.tokensGenerated}</span>
                  </div>
                )} */}
            </div>
          )) : (
            <div className="pg-center-message">
              <h1>{"Welcome, to the Playground"}</h1>
              <p className="subtitle">{"play around settings to get the desired response."}</p>
            </div>
          )}
          {isStreaming && (
            <div className="message assistant streaming">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <Button variant="outline" onClick={handleModeToggle}>
            {currentMode}
          </Button>
          {/* <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => {
              setInputMessage(e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="User Message..."
            rows={1}
          /> */}
          <div className="pg-input-wrapper">
            <div className="pg-input-container">
              <textarea
                // className="chat-input"
                placeholder="Send a message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                rows={1}
                ref={textareaRef}
                onKeyDown={handleKeyDown}
              />
            </div>
          </div>
          <Button onClick={handleSend} disabled={isStreaming || !inputMessage.trim()}>
            Send <span style={{ marginLeft: "0.5rem", marginTop: "0.2rem" }}><CornerDownLeft size={15} /></span>
          </Button>
        </div>
        {/* <div className={`chat-input-wrapper ${!messages.length ? "center-position" : ""}`}>
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
          </div>
        </div> */}
      </main>

      <aside className={`settings-sidebar ${!isSidebarOpen ? "closed" : ""}`}>
        <div className="sidebar-header">
          <h2>Model Settings</h2>
          <Button variant="ghost" size="icon" className="toggle-button" onClick={toggleSidebar}>
            <ChevronRight size={20} />
          </Button>
        </div>

        <div className="settings-content">
          <div className="setting-group">
            <label>Model</label>
            {/* <select value={settings.model} onChange={(e) => setSettings({ ...settings, model: e.target.value })}>
              {models.map((model) => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select> */}
            <Select
              options={models}
              defaultValue={models[0]}
              onChange={setCurrentModel}
              placeholder="Select Project"
              styles={{
                control: (provided) => ({
                  ...provided,
                  width: '100%',
                  height: 30,
                  borderRadius: 5,
                  border: "1px solid #E5E7EB",
                  fontSize: 16,
                  color: "#4B5563",
                  backgroundColor: "#F3F4F6",
                  boxShadow: "none",
                  "&:hover": {
                    border: "1px solid #E5E7EB",
                  },
                }),
              }}
            />
          </div>

          <div className="setting-group">
            <label>Temperature: {settings.temperature}</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={settings.temperature}
              onChange={(e) => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
            />
          </div>

          <div className="setting-group">
            <label>Max Tokens: {settings.maxTokens}</label>
            <input
              type="range"
              min="1"
              max="5000"
              step="1"
              value={settings.maxTokens}
              onChange={(e) => setSettings({ ...settings, maxTokens: parseInt(e.target.value) })}
            />
          </div>

          {/* <div className="setting-group">
            <label>System Prompt</label>
            <textarea value={settings.systemPrompt} onChange={(e) => setSettings({ ...settings, systemPrompt: e.target.value })} rows={4} />
          </div> */}
        </div>
      </aside>

      <div className="vertical-container">
        <Button variant="ghost" size="sm" className="toggle-button" onClick={toggleSidebar}>
          <ChevronLeft size={20} />
        </Button>
      </div>
    </div>
  );
};

export default PlaygroundPage;
