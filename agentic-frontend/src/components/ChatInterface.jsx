import { useState, useRef, useEffect } from 'react'
import { Send, Upload, Play } from 'lucide-react'
import MessageBubble from './MessageBubble'
import FileUploadMessage from './FileUploadMessage'
import ReportResultsMessage from './ReportResultsMessage'
import axios from 'axios'
import './ChatInterface.css'

function ChatInterface({ 
  messages, 
  collectedData, 
  currentStep, 
  onAddMessage, 
  onUpdateData, 
  onUpdateStep 
}) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = {
      type: 'user',
      content: input.trim()
    }

    onAddMessage(userMessage)
    setInput('')

    // Process user input based on current step
    await processUserInput(input.trim())
  }

  const processUserInput = async (userInput) => {
    setLoading(true)

    try {
      if (currentStep === 'greeting') {
        // Check if user wants to generate a report
        const reportKeywords = ['report', 'performance', 'generate', 'create', 'analysis', 'portfolio']
        const wantsReport = reportKeywords.some(keyword => 
          userInput.toLowerCase().includes(keyword)
        )

        if (wantsReport) {
          onUpdateStep('collecting_client_name')
          onAddMessage({
            type: 'ai',
            content: 'Great! I\'ll help you create a performance report. I need to collect some information:\n\n**Required Information:**\n1. ❌ Client name\n2. ❌ Portfolio file (Excel/CSV)\n3. ❌ Report period (e.g., Q4-2025)\n\nLet\'s start with the client name. What\'s the client\'s name?'
          })
        } else {
          onAddMessage({
            type: 'ai',
            content: 'I can help you generate professional portfolio performance reports. Just say "generate report" or "create performance analysis" to get started!'
          })
        }
      } else if (currentStep === 'collecting_client_name') {
        // Extract client name
        const clientName = userInput.trim()
        onUpdateData('clientName', clientName)
        onUpdateStep('collecting_file')
        
        onAddMessage({
          type: 'ai',
          content: `✅ Client name: ${clientName}\n\nNow I need the portfolio file. Please upload an Excel or CSV file with your holdings.`,
          showFileUpload: true
        })
      } else if (currentStep === 'collecting_period') {
        // Extract period
        const period = userInput.trim()
        console.log('Setting period:', period)
        onUpdateData('period', period)
        onUpdateStep('ready_to_generate')
        
        onAddMessage({
          type: 'ai',
          content: `Perfect! Here's what I have:\n\n**Report Configuration:**\n✅ Client: ${collectedData.clientName}\n✅ Holdings: ${collectedData.holdings?.length || 0} securities\n✅ Period: ${period}\n\nReady to generate the performance summary?`,
          showGenerateButton: true
        })
      }
    } catch (error) {
      onAddMessage({
        type: 'ai',
        content: 'Sorry, I encountered an error. Please try again.'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (file) => {
    setLoading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post('http://localhost:8001/api/parse-portfolio', formData)
      
      if (response.data.success) {
        onUpdateData('portfolioFile', file.name)
        onUpdateData('holdings', response.data.holdings)
        onUpdateStep('collecting_period')
        
        const tickers = response.data.holdings.map(h => h.ticker).join(', ')
        
        onAddMessage({
          type: 'ai',
          content: `✅ Portfolio file uploaded: ${file.name}\n✅ Found ${response.data.count} holdings: ${tickers}\n\nFinally, what reporting period would you like? (e.g., Q4-2025, YTD-2025)`
        })
      }
    } catch (error) {
      onAddMessage({
        type: 'ai',
        content: `❌ Error parsing file: ${error.message}`
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    setLoading(true)
    
    console.log('Collected data:', collectedData)
    
    onAddMessage({
      type: 'ai',
      content: '🔄 Generating performance report...\n\n• Fetching market data\n• Calculating returns\n• Analyzing risk metrics\n• Creating visualizations'
    })

    try {
      // Parse period
      const period = collectedData.period
      console.log('Period from collectedData:', period)
      
      if (!period || !period.includes('-')) {
        throw new Error('Invalid period format. Use format like Q4-2025')
      }
      
      const [q, year] = period.split('-')
      const quarter = parseInt(q.replace('Q', ''))
      
      if (!year || isNaN(quarter) || quarter < 1 || quarter > 4) {
        throw new Error('Invalid period format. Use format like Q4-2025')
      }
      
      let start_date, end_date
      if (quarter === 1) {
        start_date = `${year}-01-01`
        end_date = `${year}-03-31`
      } else if (quarter === 2) {
        start_date = `${year}-04-01`
        end_date = `${year}-06-30`
      } else if (quarter === 3) {
        start_date = `${year}-07-01`
        end_date = `${year}-09-30`
      } else {
        start_date = `${year}-10-01`
        end_date = `${year}-12-31`
      }

      const response = await axios.post('http://localhost:8001/api/generate-performance', {
        portfolio_data: {
          client_name: collectedData.clientName,
          holdings: collectedData.holdings
        },
        period: {
          name: period,
          start_date,
          end_date
        }
      })

      if (response.data.status === 'complete') {
        onAddMessage({
          type: 'ai',
          content: `✅ Performance report generated successfully!\n\n**Performance Summary for ${collectedData.clientName} - ${collectedData.period}**`,
          reportData: response.data
        })
        onUpdateStep('complete')
      } else {
        throw new Error(response.data.error || 'Generation failed')
      }
    } catch (error) {
      onAddMessage({
        type: 'ai',
        content: `❌ Error generating report: ${error.response?.data?.error || error.message}`
      })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id}>
            <MessageBubble message={message} />
            
            {message.showFileUpload && (
              <FileUploadMessage onFileUpload={handleFileUpload} loading={loading} />
            )}
            
            {message.showGenerateButton && (
              <div className="action-message">
                <button 
                  className="generate-button"
                  onClick={handleGenerate}
                  disabled={loading}
                >
                  <Play size={16} />
                  Generate Performance Report
                </button>
              </div>
            )}
            
            {message.reportData && (
              <ReportResultsMessage data={message.reportData} />
            )}
          </div>
        ))}
        
        {loading && (
          <div className="loading-message">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={loading}
            rows={1}
            className="message-input"
          />
          <button 
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="send-button"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface