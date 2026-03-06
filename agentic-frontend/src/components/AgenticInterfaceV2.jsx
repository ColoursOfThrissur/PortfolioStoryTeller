import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, TrendingUp, CheckCircle, Clock } from 'lucide-react';
import './CompleteAgenticInterface.css';

function AgenticInterfaceV2() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [progress, setProgress] = useState({ completed_steps: 0, total_steps: 8, percentage: 0 });
  const [ws, setWs] = useState(null);
  
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    createSession();
    return () => {
      if (ws) ws.close();
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const createSession = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/session/create', {
        method: 'POST'
      });
      const data = await response.json();
      setSessionId(data.session_id);
      
      addMessage('assistant', 'Welcome! I can help you generate portfolio reports. What would you like to do?');
      
      // Connect WebSocket
      connectWebSocket(data.session_id);
    } catch (error) {
      addMessage('assistant', `Error creating session: ${error.message}`);
    }
  };

  const connectWebSocket = (sid) => {
    const websocket = new WebSocket(`ws://localhost:8001/ws/chat/${sid}`);
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
    };
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    websocket.onclose = () => {
      console.log('WebSocket closed');
    };
    
    setWs(websocket);
  };

  const handleWebSocketMessage = (data) => {
    setIsLoading(false);
    
    if (data.type === 'connected') {
      return;
    }
    
    if (data.type === 'response' || data.type === 'error') {
      addMessage('assistant', data.message);
    } else if (data.type === 'result') {
      addMessage('assistant', data.message, data.data);
    } else if (data.type === 'complete') {
      addMessage('assistant', data.message, { sections: data.sections });
    }
    
    if (data.progress) {
      setProgress(data.progress);
    }
  };

  const addMessage = (type, content, data = null) => {
    setMessages(prev => [...prev, {
      type,
      content,
      data,
      timestamp: new Date()
    }]);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsLoading(true);
    addMessage('user', `Uploading ${file.name}...`);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8001/api/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        // Send message via WebSocket with file path
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: 'message',
            content: `I've uploaded the portfolio file: ${file.name}`,
            file_path: result.file_path
          }));
        }
      } else {
        addMessage('assistant', `Upload failed: ${result.detail}`);
        setIsLoading(false);
      }
    } catch (error) {
      addMessage('assistant', `Upload error: ${error.message}`);
      setIsLoading(false);
    }
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim() || isLoading || !ws) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    addMessage('user', userMessage);

    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'message',
        content: userMessage
      }));
    } else {
      addMessage('assistant', 'Connection lost. Please refresh the page.');
      setIsLoading(false);
    }
  };

  const renderMessage = (message, index) => {
    const isUser = message.type === 'user';
    
    return (
      <div key={index} className={`message ${isUser ? 'user' : 'assistant'}`}>
        <div className="message-content">
          <div className="message-text">{message.content}</div>
          
          {message.data?.section && (
            <div className="section-result">
              <div className="section-title">✅ {message.data.section.replace(/_/g, ' ').toUpperCase()}</div>
              
              {/* Performance Summary */}
              {message.data.section === 'performance_summary' && message.data.performance_table && (
                <div className="performance-tables">
                  <div className="table-title">Household Summary</div>
                  <table className="performance-table">
                    <thead>
                      <tr>
                        <th></th>
                        {message.data.performance_table.periods.map((p, i) => (
                          <th key={i}>{p}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td><strong>Portfolio</strong></td>
                        {message.data.performance_table.portfolio.map((v, i) => (
                          <td key={i}>{v ? v.toFixed(2) + '%' : 'N/A'}</td>
                        ))}
                      </tr>
                      <tr>
                        <td><strong>Benchmark</strong></td>
                        {message.data.performance_table.benchmark.map((v, i) => (
                          <td key={i}>{v ? v.toFixed(2) + '%' : 'N/A'}</td>
                        ))}
                      </tr>
                      <tr>
                        <td><strong>+/-</strong></td>
                        {message.data.performance_table.difference.map((v, i) => (
                          <td key={i} style={{color: v > 0 ? 'green' : v < 0 ? 'red' : 'inherit'}}>
                            {v ? (v > 0 ? '+' : '') + v.toFixed(2) + '%' : 'N/A'}
                          </td>
                        ))}
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}
              
              {/* Allocation Overview */}
              {message.data.section === 'allocation_overview' && message.data.allocation_table && (
                <div className="allocation-display">
                  <div className="table-title">Asset Allocation</div>
                  <table className="performance-table">
                    <thead>
                      <tr>
                        <th>Asset Class</th>
                        <th>% of Portfolio</th>
                        <th>$ Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {message.data.allocation_table.map((item, i) => (
                        <tr key={i}>
                          <td>{item.asset_class}</td>
                          <td>{item.percentage.toFixed(1)}%</td>
                          <td>${item.value.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              
              {/* Holdings Detail */}
              {message.data.section === 'holdings_detail' && message.data.holdings_table && (
                <div className="holdings-display">
                  <div className="table-title">Holdings Detail ({message.data.total_positions} positions)</div>
                  <table className="performance-table">
                    <thead>
                      <tr>
                        <th>Security</th>
                        <th>Shares</th>
                        <th>Price</th>
                        <th>Value</th>
                        <th>% Portfolio</th>
                        <th>QTD Return</th>
                      </tr>
                    </thead>
                    <tbody>
                      {message.data.holdings_table.slice(0, 10).map((h, i) => (
                        <tr key={i}>
                          <td><strong>{h.security}</strong></td>
                          <td>{h.shares.toFixed(0)}</td>
                          <td>${h.price.toFixed(2)}</td>
                          <td>${h.value.toLocaleString()}</td>
                          <td>{h.percentage.toFixed(1)}%</td>
                          <td style={{color: h.qtd_return > 0 ? 'green' : 'red'}}>
                            {h.qtd_return > 0 ? '+' : ''}{h.qtd_return.toFixed(2)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              
              {/* Market Commentary */}
              {message.data.section === 'market_commentary' && message.data.commentary && (
                <div className="commentary-display">
                  <div className="commentary-section">
                    <strong>Market Summary:</strong>
                    <p>{message.data.market_summary}</p>
                  </div>
                  <div className="commentary-section">
                    <strong>Portfolio Impact:</strong>
                    <p>{message.data.portfolio_impact}</p>
                  </div>
                  <div className="commentary-section">
                    <strong>Outlook:</strong>
                    <p>{message.data.outlook}</p>
                  </div>
                </div>
              )}
              
              {/* Planning Notes */}
              {message.data.section === 'planning_notes' && message.data.recommendations && (
                <div className="planning-display">
                  <div className="commentary-section">
                    <strong>Recommendations:</strong>
                    <p>{message.data.recommendations}</p>
                  </div>
                  {message.data.action_items && (
                    <div className="action-items">
                      <strong>Action Items:</strong>
                      <ul>
                        {message.data.action_items.map((item, i) => (
                          <li key={i}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              
              {/* Output/Complete */}
              {message.data.section === 'output' && message.data.report && (
                <div className="report-complete">
                  <div className="complete-badge">🎉 Complete Report Generated!</div>
                  <div className="report-summary">
                    <p><strong>Client:</strong> {message.data.report.cover_page.client_name}</p>
                    <p><strong>Period:</strong> {message.data.report.cover_page.period}</p>
                    <p><strong>Sections:</strong> {message.data.report.total_sections}</p>
                  </div>
                </div>
              )}
            </div>
          )}
          
          <div className="message-timestamp">
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="complete-agentic-interface">
      <div className="chat-container">
        {/* Header */}
        <div className="chat-header">
          <h1>Agentic Portfolio Report Generator v2</h1>
          <p>AI-powered conversational report generation • Gemini 2.5 Flash</p>
          
          {/* Progress Bar */}
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progress.percentage}%` }}
              />
            </div>
            <div className="progress-text">
              {progress.completed_steps}/{progress.total_steps} sections complete ({progress.percentage}%)
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="messages-container">
          {messages.map(renderMessage)}
          {isLoading && (
            <div className="loading-indicator">
              <div className="loading-content">
                <div className="spinner"></div>
                <span className="loading-text">Processing...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-flex">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="upload-button"
              disabled={isLoading}
            >
              <Upload size={16} />
              <span>Upload</span>
            </button>
            
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type your request (e.g., 'Generate Q4 2025 report for John Mitchell')"
              className="message-input"
              disabled={isLoading}
            />
            
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="send-button"
            >
              <Send size={16} />
              <span>Send</span>
            </button>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.csv"
            onChange={handleFileUpload}
            className="file-input"
          />
        </div>
      </div>

      {/* Sidebar - Completed Sections */}
      {progress.completed_sections && progress.completed_sections.length > 0 && (
        <div className="sidebar">
          <div className="sidebar-header">
            <h2 className="sidebar-title">Completed Sections</h2>
          </div>
          
          <div className="sections-container">
            {progress.completed_sections.map((section, idx) => (
              <div key={idx} className="section-item">
                <CheckCircle size={16} className="section-icon-complete" />
                <span>{section.replace(/_/g, ' ').toUpperCase()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AgenticInterfaceV2;
