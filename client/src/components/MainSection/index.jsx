import PropTypes from "prop-types";
import { useContext, useEffect, useState } from "react";
import Select from "react-select";
import { toast } from "react-toastify";
// import { parseSSEStream } from "../../utils/utils";
import { chatQuery, createProject, getProjects, webSearchQuery } from "../../Api/handlers/chatHandler";
import Button from "../ui/Button";
import {
  PopoverRoot,
  PopoverTrigger,
  PopoverContent,
  Popover,
  PopoverFooter,
  PopoverAction,
  PopoverTitle,
} from "../../components/ui/Popover"; // Import components from your popover file
import ChatInput from "../ChatInput";
import ChatMessages from "../ChatMessages";
import SidepanelIcon from "../icons/SidepanelIcon";
// import PlusIcon from '../icons/PlusIcon';
import "./mainSection.css";
import { ChatContext } from "../../context/ChatContext.jsx";
import PlusIcon from "../icons/PlusIcon.jsx";

export default function MainSection({ hidden, setHidden }) {
  // const [chatId, setChatId] = useState(null);
  // const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [projectName, setProjectName] = useState("");

  const { messages, setMessages } = useContext(ChatContext);

  const { projects, setProjects, currentProject, setCurrentProject } =
    useContext(ChatContext);

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage(isWebSearch) {

    if (isWebSearch) {
      const trimmedMessage = newMessage.trim();
      if (!trimmedMessage || isLoading) return;

      setMessages((prev) => [
        ...prev,
        { role: "user", content: trimmedMessage },
        { role: "assistant", content: "", sources: [], loading: true },
      ]);
      setNewMessage("");

      const response = await webSearchQuery(newMessage);

      if (response.status_code == 200) {
        setMessages((draft) => {
          const updatedMessages = [...draft];
          updatedMessages[updatedMessages.length - 1].content = response.data.result;
          return updatedMessages;
        });

        setMessages((draft) => {
          const updatedMessages = [...draft];
          updatedMessages[updatedMessages.length - 1].loading = false;
          return updatedMessages;
        })
      }
      return;
    }

    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: trimmedMessage },
      { role: "assistant", content: "", sources: [], loading: true },
    ]);
    setNewMessage("");

    const response = await chatQuery(newMessage);

    if (response.status_code == 200) {
      setMessages((draft) => {
        const updatedMessages = [...draft];
        updatedMessages[updatedMessages.length - 1].content = response.data.result;
        return updatedMessages;
      });

      setMessages((draft) => {
        const updatedMessages = [...draft];
        updatedMessages[updatedMessages.length - 1].loading = false;
        return updatedMessages;
      })
    }
  }

  // TODO: replace with actual API call

  useEffect(() => {
    async function fetchProjects() {
      const response = await getProjects();

      const projectOptions = response.map((project) => ({
        value: project,
        label: project,
      }));

      setProjects(projectOptions);

      if (projectOptions.length > 0) {
        const timer = setTimeout(
          () => setCurrentProject(projectOptions[0]),
          1000
        );

        return () => clearTimeout(timer); // Cleanup function to clear timeout
      }

      toast.info("No projects found. Create a new project to get started!");
    }

    fetchProjects();
  }, []);

  async function handleCreateProject() {
    const response = await createProject({ workspace_name: projectName });

    console.log("Response: ", response);

    if (response.status_code === 200) {
      toast.success("Project created successfully!");
      setProjects((prev) => [
        ...prev,
        { value: projectName, label: projectName },
      ]);
      setIsOpen(false);
      setProjectName("");
    }

    // console.log("Creating project...");
  }

  return (
    <section className="main-section">
      <div className="composer-parent">
        <div className="composer-header">
          {!!hidden && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setHidden(() => false)}
            >
              <SidepanelIcon className="sidepanel-icon" />
            </Button>
          )}

          {
            <Select
              options={projects}
              defaultValue={projects[0]}
              onChange={setCurrentProject}
              placeholder="Select Project"
              styles={{
                control: (provided) => ({
                  ...provided,
                  width: 200,
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
          }

          <PopoverRoot>
            <PopoverTrigger onClick={() => setIsOpen(!isOpen)}>
              <Button size="sm">{"New Project"}</Button>
            </PopoverTrigger>

            <Popover
              visible={isOpen}
              onClose={() => setIsOpen(false)}
              align="top-right"
              offset={50}
              className="mainSection-popover"
            >
              <PopoverContent className="mainSection-popover-content">
                <PopoverTitle>Create a New Project</PopoverTitle>
                <input
                  type="text"
                  placeholder="Enter project name"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="input-field"
                />
              </PopoverContent>

              <PopoverFooter className="mainSection-popover-footer">
                <PopoverAction onClick={handleCreateProject}>
                  <Button size="sm">Create Project</Button>
                </PopoverAction>
              </PopoverFooter>
            </Popover>
          </PopoverRoot>
        </div>
        <ChatMessages messages={messages} isLoading={isLoading} />
      </div>
      <ChatInput
        newMessage={newMessage}
        setNewMessage={setNewMessage}
        messages={messages}
        isLoading={isLoading}
        submitNewMessage={submitNewMessage}
      />
    </section>
  );
}

MainSection.propTypes = {
  hidden: PropTypes.bool.isRequired,
  setHidden: PropTypes.func.isRequired,
};
