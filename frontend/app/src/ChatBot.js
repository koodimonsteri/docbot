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
  const [messages, setMessages] = useState([])

  const generateMessageId = (() => {
    let messageId = 0;
  
    return (messages) => {
      if (!Array.isArray(messages) || messages.length === 0) {
        messageId += 1;
      } else {
        const maxId = messages.reduce((max, message) => (message.id > max ? message.id : max), 0);
        messageId = maxId + 1;
      }
  
      return messageId;
    };
  })();

  useEffect(() => {
    const generatedUserId = uuidv4();
    setUserId(generatedUserId);

    const ws = new WebSocket(`ws://localhost:8000/chat/ws/${generatedUserId}`);

    ws.onopen = () => {
      console.log('WebSocket connection opened');
    };

    ws.onmessage = event => {
      const partialResponse = JSON.parse(event.data);
      console.log('partial response:', partialResponse)
      setMessages((prevMessages) => {
        const existingMessageIndex = prevMessages.findIndex((msg) => msg && msg.id === partialResponse.id);
        if (existingMessageIndex !== -1) {
          return prevMessages.map((msg) =>
            msg.id === partialResponse.id
              ? {
                  ...msg,
                  text: `${msg.text || ''}${partialResponse.text ? `${partialResponse.text}` : ''}`,
                }
              : msg
          );
        } else {
          return [...prevMessages, partialResponse];
      }
    });
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
      const response = await fetch('http://localhost:8000/files');
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
        await fetch('http://localhost:8000/files', {
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
    console.log(selected)
    setSelectedFile(selected);
  };

  const handleSendMessage = () => {
    console.log('Attempting to send message');
    console.log('websocket:', websocket);
    console.log('newMessage:', newMessage);
    const messageId = generateMessageId(messages);
    if (websocket && newMessage.trim() !== '') {
      const messageItem = {
        id: messageId,
        text: newMessage,
        type: 'user',
        file_name: selectedFile?.name || '',
      };
      console.log('Sending message:', messageItem);
      setMessages(prevHistory => [...prevHistory, messageItem]);
      websocket.send(JSON.stringify(messageItem));
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
            <h2 className="centered-header">DocBot</h2>
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
                {messages.map((entry) => (
                    <li key={entry.id} className={`message ${entry.type}`}>
                    {entry.type === 'user' ? (
                        <span className="indicator">User</span>
                    ) : (
                        <span className="indicator">Bot</span>
                    )}
                    {entry.text !== undefined ? entry.text : ''}
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