import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import './ChatBot.css';

const ChatBot = () => {
  const [chatHistory, setChatHistory] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [websocket, setWebsocket] = useState(null);
  const [userId, setUserId] = useState('');
  //const [uploadedFiles, setUploadedFiles] = useState([]);
  //const [selectedFile, setSelectedFile] = useState(null);


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

    return () => {
      ws.close();
    };
  }, []);

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
    // If Enter key is pressed, submit the message
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-history">
        <ul>
          {chatHistory.map((entry, index) => (
            <li key={index} className={`message ${entry.type}`}>
              {entry.type === 'sent' ? (
                <span className="indicator">User:</span>
              ) : (
                <span className="indicator">Bot:</span>
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
  );
};


export default ChatBot;