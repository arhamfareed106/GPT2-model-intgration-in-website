import { useState, useEffect, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import Header from './components/Header';

const API_BASE = "http://127.0.0.1:5000";

function App() {
  const [messages, setMessages] = useState([]);
  const [isServerOnline, setIsServerOnline] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Check server health on component mount
  useEffect(() => {
    checkServerHealth();
    const interval = setInterval(checkServerHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Scroll to bottom of chat when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const checkServerHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      const data = await response.json();
      setIsServerOnline(data.status === "ok");
    } catch (error) {
      setIsServerOnline(false);
    }
  };

  const sendMessage = async (prompt) => {
    if (!prompt.trim() || !isServerOnline) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: prompt,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call the backend API
      const response = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Add AI response to chat
      const aiMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'ai',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I encountered an error processing your request.",
        sender: 'ai',
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Header 
        isServerOnline={isServerOnline} 
        onClearChat={clearChat} 
      />
      
      <main className="flex-1 overflow-hidden flex flex-col">
        <ChatWindow 
          messages={messages} 
          isLoading={isLoading}
          messagesEndRef={messagesEndRef}
        />
        
        <ChatInput 
          onSend={sendMessage} 
          disabled={!isServerOnline || isLoading}
        />
      </main>
    </div>
  );
}

export default App;