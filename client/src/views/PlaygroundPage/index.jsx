import { useState, useRef, useEffect } from "react";
import "./PlaygroundPage.css";
import { ChevronRight, ChevronLeft, CornerDownLeft } from "lucide-react";

const PlaygroundPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [settings, setSettings] = useState({
    model: "mixtral-8x7b",
    temperature: 0.7,
    maxTokens: 5000,
    topP: 1,
    topK: 50,
  });
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const [currentMode, setCurrentMode] = useState("User");

  const models = [
    { value: "mixtral-8x7b", label: "Mixtral 8x7B" },
    { value: "llama2-70b", label: "Llama 2 70B" },
  ];

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
            <div key={index} className={`message ${message.role}`}>
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
      </main>

      <aside className={`settings-sidebar ${!isSidebarOpen ? "closed" : ""}`}>
        <div className="sidebar-header">
          <h2>Model Settings</h2>
          <button className="toggle-button" onClick={toggleSidebar}>
            <ChevronRight size={20} />
          </button>
        </div>

        <div className="settings-content">
          <div className="setting-group">
            <label>Model</label>
            <select value={settings.model} onChange={(e) => setSettings({ ...settings, model: e.target.value })}>
              {models.map((model) => (
                <option key={model.value} value={model.value}>
                  {model.label}
                </option>
              ))}
            </select>
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
        <button className="toggle-button" onClick={toggleSidebar}>
          <ChevronLeft size={20} />
        </button>
      </div>
    </div>
  );
};

export default PlaygroundPage;
