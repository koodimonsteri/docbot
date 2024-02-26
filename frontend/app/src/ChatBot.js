import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import './ChatBot.css';

const ChatBot = () => {
  const [chatHistory, setChatHistory] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [websocket, setWebsocket] = useState(null);
  const [userId, setUserId] = useState('');
  const [existingFiles, setExistingFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadFile, setUploadFile] = useState(null)
  const [uploadStatus, setUploadStatus] = useState(null);

  useEffect(() => {
    const generatedUserId = uuidv4();
    setUserId(generatedUserId);

    const ws = new WebSocket(`ws://localhost:8000/chat/ws/${generatedUserId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connection opened');
    };

    ws.onmessage = event => {
      const message = event.data
      console.log('Received message:', message)
      updateChatHistory({ text: event.data, type: 'received' });
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    setWebsocket(ws);

    fetchExistingFiles();

    return () => {
      ws.close();
    };
  }, []);

  const fetchExistingFiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/upload/file');
      const existing_files = await response.json();
      
      const convertedFiles = existing_files.files.map((fileName, index) => ({
        id: index + 1,
        name: fileName,
      }));

      setExistingFiles(convertedFiles)
    } catch (error) {
      console.error('Error fetching uploaded files:', error);
    }
};

const handleFileUpload = async (e) => {
    const file = uploadFile
    if (uploadFile && uploadFile.type === 'application/pdf')  {
      console.log('Uploading pdf file:', file)
      const formData = new FormData();
      formData.append('file', file);
      try {
        await fetch('http://localhost:8000/upload/file', {
          method: 'POST',
          body: formData,
        });
        fetchExistingFiles();
      } catch (error) {
        console.error('Error uploading file:', error);
      }
      setUploadStatus('File uploaded successfully');
      const fileInput = document.querySelector('input[type="file"]');
      fileInput.value = '';
      setUploadFile(null);
    } else {
        // Optionally, you can provide feedback to the user that the file is invalid.
        setUploadStatus('Error uploading file. Please try again.');
        console.error('Invalid file type. Please choose a PDF file.');
  };
};
  const handleUploadFileChange = (e) => {
    console.log('file change', e.target.files[0])
    setUploadFile(e.target.files[0]);
  };

const handleDropDownFileSelect = (e) => {
    const fileId = e.target.value;
    const selected = existingFiles.find((file) => file.id === Number(fileId));
    setSelectedFile(selected);
  };

  const updateChatHistory = (message) => {
    setChatHistory(prevHistory => [...prevHistory, message]);
  };

  const handleSendMessage = () => {
    console.log('Attempting to send message');
    console.log('websocket:', websocket);
    console.log('newMessage:', newMessage);

    if (websocket && newMessage.trim() !== '') {
      const message = { text: newMessage, type: 'sent' };
      console.log('Sending message:', message);

      updateChatHistory(message);
      websocket.send(JSON.stringify({ text: newMessage }));
      setNewMessage('');
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chatbot-container">
        <div className="file-panel">
            <h2>DocBot</h2>
            <div className="file-upload">
            <p>Upload PDF file</p>
            <input type="file" onChange={handleUploadFileChange} />
            <button onClick={handleFileUpload} disabled={!uploadFile}>
                Upload
            </button>
            </div>
            <div className="file-dropdown">
            <p>Select file to be used in chat</p>
            <select onChange={handleDropDownFileSelect} value={selectedFile ? selectedFile.id : ''}>
                <option value="">Select a file</option>
                {existingFiles.map((file) => (
                <option key={file.id} value={file.id}>
                    {file.name}
                </option>
                ))}
            </select>
        </div>
        </div>
        <div className="chat-container">
            <div className="chat-history">
                <ul>
                {chatHistory.map((entry, index) => (
                    <li key={index} className={`message ${entry.type}`}>
                    {entry.type === 'sent' ? (
                        <span className="indicator">User</span>
                    ) : (
                        <span className="indicator">Bot</span>
                    )}
                    {entry.text}
                    </li>
                ))}
                </ul>
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                />
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    </div>
  );
};


export default ChatBot;