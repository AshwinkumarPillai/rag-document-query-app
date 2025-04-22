import { useState, useEffect, useCallback } from "react";
import { Message } from "./types";
import ChatWindow from "./components/ChatWindow/ChatWindow";
import MessageInput from "./components/MessageInput/MessageInput";
import ChatControls from "./components/ChatControls/ChatControls";
import FileUpload from "./components/FileUpload/FileUpload";

import "./App.css";
import { queryIndex } from "./api/api";

const STORAGE_KEY = "chatHistory";

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);

  useEffect(() => {
    const storedHistory = localStorage.getItem(STORAGE_KEY);
    if (storedHistory) {
      try {
        const parsed = JSON.parse(storedHistory);
        if (Array.isArray(parsed)) setMessages(parsed);
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  useEffect(() => {
    messages.length > 0
      ? localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
      : localStorage.removeItem(STORAGE_KEY);
  }, [messages]);

  const handleFileUploadComplete = (filename: string) => {
    setFileUploaded(true);
    setMessages([
      {
        id: `sys-${Date.now()}`,
        text: `✅ File "${filename}" uploaded successfully! You can now start chatting.`,
        sender: "agent",
        timestamp: Date.now(),
      },
    ]);
  };

  const queryLLM = useCallback(async (userInput: string) => {
    setIsAgentTyping(true);
    try {
      const response = await queryIndex(userInput);
      const agentMessage: Message = {
        id: `agent-${Date.now()}`,
        text: response.answer,
        sender: "agent",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: `agent-error-${Date.now()}`,
          text: "⚠️ Sorry, something went wrong. Please try again.",
          sender: "agent",
          timestamp: Date.now(),
        },
      ]);
    } finally {
      setIsAgentTyping(false);
    }
  }, []);

  const handleSendMessage = useCallback(
    (text: string) => {
      if (!text.trim()) return;

      const userMessage: Message = {
        id: `user-${Date.now()}`,
        text: text,
        sender: "user",
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, userMessage]);
      queryLLM(text);
    },
    [queryLLM]
  );

  const handleNewChat = useCallback(() => {
    setMessages([]);
    setFileUploaded(false);
  }, []);

  return (
    <div className="app-container">
      <h1>Interactive Agent</h1>
      <div className="chat-area">
        <ChatControls onNewChat={handleNewChat} onClearChat={() => setMessages([])} />
        {!fileUploaded && <FileUpload onUploadComplete={handleFileUploadComplete} />}
        <ChatWindow messages={messages} isAgentTyping={isAgentTyping} />
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={!fileUploaded || isAgentTyping}
          fileUploaded={fileUploaded}
        />
      </div>
    </div>
  );
}

export default App;
