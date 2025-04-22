// src/components/FileUpload/FileUpload.tsx
import React, { useRef, useState } from "react";
import { uploadDocument } from "../../api/api";

interface FileUploadProps {
  onUploadComplete: (filename: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const response = await uploadDocument(file);
      onUploadComplete(response.filename);
    } catch (err) {
      console.error("Upload error:", err);
      setError("Failed to upload file. Please try again.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="file-upload">
      <label htmlFor="upload-input">Upload a .pdf or .txt file to begin:</label>
      <input
        type="file"
        accept=".pdf,.txt"
        ref={fileInputRef}
        onChange={handleFileChange}
        disabled={uploading}
      />
      {uploading && <p>Uploading...</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default FileUpload;
