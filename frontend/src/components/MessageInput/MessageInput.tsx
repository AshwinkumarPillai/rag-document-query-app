import React, { useState, useCallback } from "react";
import "./MessageInput.css";

interface MessageInputProps {
  onSendMessage: (text: string) => void;
  disabled?: boolean;
  fileUploaded?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled = false,
  fileUploaded = false,
}) => {
  const [inputValue, setInputValue] = useState<string>("");

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = useCallback(
    (event?: React.FormEvent<HTMLFormElement>) => {
      event?.preventDefault();
      if (!inputValue.trim() || disabled) return;

      onSendMessage(inputValue);
      setInputValue(""); // Clear input after sending
    },
    [inputValue, onSendMessage, disabled]
  );

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form className="message-input-form" onSubmit={handleSubmit}>
      <input
        type="text"
        className="message-input"
        value={inputValue}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        placeholder={
          disabled ? (fileUploaded ? "Agent is typing..." : "Upload a file to begin") : "Type your message..."
        }
        aria-label="Chat message input"
        disabled={disabled}
      />
      <button type="submit" className="send-button" disabled={!inputValue.trim() || disabled}>
        Send
      </button>
    </form>
  );
};

export default MessageInput;
