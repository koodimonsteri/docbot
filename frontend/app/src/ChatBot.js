// src/ChatPage.js
import React, { useState, useEffect } from 'react';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [websocket, setWebsocket] = useState(null);

  useEffect(() => {
    // Establish a WebSocket connection when the component mounts
    const ws = new WebSocket('ws://localhost:8000/chat');

    ws.onopen = () => {
      console.log('WebSocket connection opened');
    };

    ws.onmessage = event => {
      // Handle incoming messages from the WebSocket
      const message = JSON.parse(event.data);
      setMessages(prevMessages => [...prevMessages, message]);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    setWebsocket(ws);

    // Cleanup the WebSocket connection when the component unmounts
    return () => {
      ws.close();
    };
  }, []);

  const handleSendMessage = () => {
    // Send a new message to the WebSocket
    if (websocket && newMessage.trim() !== '') {
      websocket.send(JSON.stringify({ text: newMessage }));
      setNewMessage('');
    }
  };

  return (
    <div>
      <h1>Chat Page</h1>
      <ul>
        {messages.map((message, index) => (
          <li key={index}>{message.text}</li>
        ))}
      </ul>
      <div>
        <input
          type="text"
          value={newMessage}
          onChange={e => setNewMessage(e.target.value)}
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default ChatPage;