import { createContext, useState, useRef } from "react";

// Create the context
export const ChatContext = createContext();

// Provide the context
export const ChatProvider = ({ children }) => {
  const fileRef = useRef(null);
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [messages, setMessages] = useState([]);

  return (
    <ChatContext.Provider value={{ fileRef, projects, setProjects, currentProject, setCurrentProject, messages, setMessages }}>
      {children}
    </ChatContext.Provider>
  );
};