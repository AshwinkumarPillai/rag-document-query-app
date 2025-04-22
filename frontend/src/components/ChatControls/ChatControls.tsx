import React from "react";
import "./ChatControls.css";

interface ChatControlsProps {
  onNewChat: () => void;
  onClearChat: () => void;
}

const ChatControls: React.FC<ChatControlsProps> = ({ onNewChat, onClearChat }) => {
  return (
    <div className="chat-controls">
      <button onClick={onNewChat} title="Start a new conversation (clears current)">
        New Chat
      </button>
      <button onClick={onClearChat} title="Clear current chat history">
        Clear Chat
      </button>
    </div>
  );
};

export default ChatControls;
