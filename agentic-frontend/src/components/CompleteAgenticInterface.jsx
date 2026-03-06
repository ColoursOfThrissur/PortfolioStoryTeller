import React, { useState, useRef, useEffect } from 'react';
import { Upload, Send, FileText, TrendingUp, PieChart, Building, MessageSquare, Activity, FileCheck, Shield, User } from 'lucide-react';
import './CompleteAgenticInterface.css';

const SECTION_ICONS = {
  cover_page: User,
  executive_summary: FileCheck,
  performance_summary: TrendingUp,
  allocation_overview: PieChart,
  holdings_detail: Building,
  market_commentary: MessageSquare,
  activity_summary: Activity,
  planning_notes: FileText,
  disclosures: Shield
};

const SECTION_NAMES = {
  cover_page: "Cover Page",
  executive_summary: "Executive Summary", 
  performance_summary: "Performance Summary",
  allocation_overview: "Allocation Overview",
  holdings_detail: "Holdings Detail",
  market_commentary: "Market Commentary",
  activity_summary: "Activity Summary",
  planning_notes: "Planning Notes",
  disclosures: "Disclosures"
};

function CompleteAgenticInterface() {
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: 'Welcome! I\'m your Complete Agentic Portfolio Analyst. I can generate comprehensive reports with all 9 sections. Upload your portfolio file to begin!',
      timestamp: new Date()
    }
  ]);
  
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [portfolioData, setPortfolioData] = useState(null);
  const [periodData, setPeriodData] = useState(null);
  const [reportResults, setReportResults] = useState(null);
  const [activeSection, setActiveSection] = useState(null);
  
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

      const response = await fetch('http://localhost:8001/api/upload-portfolio', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        // File uploaded, now trigger agent parsing
        addMessage('assistant', 'File uploaded! Let me parse it intelligently...');
        
        // Convert file to base64 for agent parsing
        const reader = new FileReader();
        reader.onload = async () => {
          const base64Content = reader.result.split(',')[1];
          
          // Trigger agent parsing
          const parseResponse = await fetch('http://localhost:8001/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message: `Parse this portfolio file: ${file.name}`,
              file_content: base64Content,
              filename: file.name
            })
          });
          
          const parseResult = await parseResponse.json();
          
          if (parseResult.portfolio_data) {
            setPortfolioData(parseResult.portfolio_data);
            addMessage('assistant', parseResult.message, {
              type: 'portfolio_uploaded',
              portfolio: parseResult.portfolio_data
            });
          } else {
            addMessage('assistant', parseResult.message || 'Parsing completed');
          }
        };
        
        reader.readAsDataURL(file);
      } else {
        addMessage('assistant', `Upload failed: ${result.detail}`);
      }
    } catch (error) {
      addMessage('assistant', `Upload error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    addMessage('user', userMessage);

    try {
      // Parse period if provided
      let period = periodData;
      if (!period && userMessage.match(/Q[1-4]-\d{4}|YTD-\d{4}|\d{4}/)) {
        const periodMatch = userMessage.match(/(Q[1-4]-\d{4}|YTD-\d{4}|\d{4})/);
        if (periodMatch) {
          period = parsePeriod(periodMatch[1]);
          setPeriodData(period);
        }
      }

      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          portfolio_data: portfolioData,
          period_data: period
        }),
      });

      const result = await response.json();

      if (result.type === 'analysis_complete') {
        setReportResults(result.results);
        addMessage('assistant', result.message, {
          type: 'complete_report',
          results: result.results
        });
      } else {
        addMessage('assistant', result.message, result);
      }

    } catch (error) {
      addMessage('assistant', `Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const parsePeriod = (periodStr) => {
    const currentYear = new Date().getFullYear();
    
    if (periodStr.startsWith('Q4-')) {
      const year = parseInt(periodStr.split('-')[1]);
      return {
        name: periodStr,
        start_date: `${year}-10-01`,
        end_date: `${year}-12-31`
      };
    } else if (periodStr.startsWith('YTD-')) {
      const year = parseInt(periodStr.split('-')[1]);
      return {
        name: periodStr,
        start_date: `${year}-01-01`,
        end_date: `${year}-12-31`
      };
    }
    
    return {
      name: periodStr,
      start_date: `${currentYear}-01-01`,
      end_date: `${currentYear}-12-31`
    };
  };

  const renderMessage = (message, index) => {
    const isUser = message.type === 'user';
    
    return (
      <div key={index} className={`message ${isUser ? 'user' : 'assistant'}`}>
        <div className="message-content">
          <div className="message-text">{message.content}</div>
          
          {message.data?.type === 'portfolio_uploaded' && (
            <div className="portfolio-summary">
              <div className="portfolio-summary-title">Portfolio Summary:</div>
              <div className="portfolio-summary-details">
                Client: {message.data.portfolio?.client_name || 'Unknown'}<br/>
                Holdings: {message.data.portfolio?.holdings?.length || 0} positions<br/>
                Tickers: {message.data.portfolio?.holdings?.map(h => h.ticker).join(', ') || 'None'}
              </div>
            </div>
          )}
          
          {message.data?.type === 'complete_report' && (
            <CompleteReportDisplay results={message.data.results} />
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
      {/* Main Chat Area */}
      <div className="chat-container">
        {/* Header */}
        <div className="chat-header">
          <h1>Complete Agentic Portfolio Analyst</h1>
          <p>AI-powered analysis with all 9 report sections • 11 MCP tools available</p>
        </div>

        {/* Messages */}
        <div className="messages-container">
          {messages.map(renderMessage)}
          {isLoading && (
            <div className="loading-indicator">
              <div className="loading-content">
                <div className="loading-flex">
                  <div className="spinner"></div>
                  <span className="loading-text">Analyzing...</span>
                </div>
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
              placeholder="Type your request (e.g., 'Generate full report for Q4-2025')"
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

      {/* Sidebar - Report Sections */}
      {reportResults && (
        <div className="sidebar">
          <div className="sidebar-header">
            <h2 className="sidebar-title">Report Sections</h2>
            <p className="sidebar-subtitle">
              {Object.keys(reportResults.sections).length} sections generated
            </p>
          </div>
          
          <div className="sections-container">
            {Object.entries(reportResults.sections).map(([sectionKey, sectionData]) => {
              const IconComponent = SECTION_ICONS[sectionKey] || FileText;
              const isActive = activeSection === sectionKey;
              
              return (
                <button
                  key={sectionKey}
                  onClick={() => setActiveSection(isActive ? null : sectionKey)}
                  className={`section-button ${isActive ? 'active' : ''}`}
                >
                  <div className="section-header">
                    <IconComponent size={16} className="section-icon" />
                    <div className="section-info">
                      <div className="section-name">
                        {SECTION_NAMES[sectionKey] || sectionKey}
                      </div>
                      <div className="section-status">
                        {sectionData.status === 'complete' ? '✅ Complete' : '❌ Error'}
                      </div>
                    </div>
                  </div>
                  
                  {isActive && sectionData.status === 'complete' && (
                    <div className="section-preview">
                      <SectionPreview sectionKey={sectionKey} data={sectionData} />
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function CompleteReportDisplay({ results }) {
  return (
    <div className="report-display">
      <div className="report-title">📊 Complete Report Generated</div>
      <div className="report-details">
        <div>Client: {results.client_name}</div>
        <div>Period: {results.period}</div>
        <div>Sections: {results.total_sections}</div>
        <div>Generated: {new Date(results.generation_time).toLocaleString()}</div>
      </div>
      
      <div className="sections-grid">
        {Object.entries(results.sections).map(([key, data]) => (
          <div key={key} className={`section-status-badge ${
            data.status === 'complete' ? 'complete' : 'error'
          }`}>
            {SECTION_NAMES[key] || key}
          </div>
        ))}
      </div>
    </div>
  );
}

function SectionPreview({ sectionKey, data }) {
  switch (sectionKey) {
    case 'performance_summary':
      return (
        <div>
          <div>Portfolio Value: ${data.portfolio_value?.toLocaleString()}</div>
          <div>QTD Return: {data.key_metrics?.qtd_return?.toFixed(2)}%</div>
          <div>YTD Return: {data.key_metrics?.ytd_return?.toFixed(2)}%</div>
        </div>
      );
    
    case 'allocation_overview':
      return (
        <div>
          <div>Total Positions: {data.total_positions}</div>
          <div>Diversification Score: {data.diversification_score?.toFixed(1)}</div>
          <div>Top Sector: {Object.entries(data.sector_allocation || {})[0]?.[0]}</div>
        </div>
      );
    
    case 'holdings_detail':
      return (
        <div>
          <div>Holdings Analyzed: {data.total_positions}</div>
          <div>Largest Position: {data.largest_position?.ticker}</div>
          <div>Avg Rating: {data.avg_analyst_rating}</div>
        </div>
      );
    
    default:
      return <div>Section completed successfully</div>;
  }
}

export default CompleteAgenticInterface;