// src/components/ChatWindow/ChatWindow.tsx
import React, { useEffect, useRef } from "react";
import { Message } from "../../types";
import "./ChatWindow.css";

interface ChatWindowProps {
  messages: Message[];
  isAgentTyping: boolean;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isAgentTyping }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isAgentTyping]);

  return (
    <div className="chat-window">
      {messages.map((msg) => (
        <div key={msg.id} className={`message ${msg.sender}`}>
          <p className="message-text">{msg.text}</p>
          <span className="message-timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</span>
        </div>
      ))}
      {isAgentTyping && (
        <div className="message agent typing">
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}
      {/* Empty div at the end to help scrolling to the very bottom */}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;
