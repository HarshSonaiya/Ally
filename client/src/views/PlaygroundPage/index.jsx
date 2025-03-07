import { useState, useRef, useEffect } from "react";
import "./PlaygroundPage.css";
import { ChevronRight, ChevronLeft, CornerDownLeft } from "lucide-react";
import Button from "../../components/ui/Button";
import Select from "react-select";

const models = [
  { value: "llama-3.1-8b-instant", label: "Llama 3.1 8B Instant" },
  { value: "llama-3.3-70b-specdec", label: "Llama 3.3 70B SpecDec" },
  { value: "llama-3.3-70b-versatile", label: "Llama 3.3 70B Versatile" },
  { value: "llama-3.2-3b-preview", label: "Llama 3.2 3B Preview" },
];

const PlaygroundPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
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
  const [currentMode, setCurrentMode] = useState("User");

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
  }, [input]);

  const handleModeToggle = () => {
    setCurrentMode((prev) => (prev === "User" ? "Assistant" : "User"));
    setInput(currentMode === "User" ? "" : "");
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsStreaming(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage = {
        role: "assistant",
        content:
          "This is a simulated response. Replace with actual Groq API integration. THis is me whate i need to do is just a classsification ins the situaikon wiehtou aannhy tThis is a simulated response. Replace with actual Groq API integration. THis is me whate i need to do is just a classsification ins the situaikon wiehtou aannhy t",
        timestamp: new Date().toISOString(),
        metrics: {
          timeToFirstToken: "23ms",
          totalTime: "1.2s",
          tokensGenerated: 42,
        },
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsStreaming(false);
    }, 1000);
  };

  return (
    <div className="playground-container">
      <main className={`chat-main ${!isSidebarOpen ? "sidebar-closed" : ""}`}>
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`pg-message ${message.role}`}>
              {message.role === "assistant" && (
                <div className="message-header">
                  <span className="message-role">{message.role}</span>
                  <span className="message-time">{new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
              )}
              <div className="message-content">{message.content}</div>
              {message.metrics && (
                <div className="message-metrics">
                  <span>First token: {message.metrics.timeToFirstToken}</span>
                  <span>Total time: {message.metrics.totalTime}</span>
                  <span>Tokens: {message.metrics.tokensGenerated}</span>
                </div>
              )}
            </div>
          ))}
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
          <button onClick={handleModeToggle} className="mode-toggle-button">
            {currentMode}
          </button>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="User Message..."
            rows={1}
          />
          <button onClick={handleSend} disabled={isStreaming || !input.trim()} className="send-button">
            Send <CornerDownLeft />
          </button>
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
