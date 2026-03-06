import { User, Bot } from 'lucide-react'

function MessageBubble({ message }) {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className={`message-bubble ${message.type}`}>
      <div className="message-content">
        {message.content}
      </div>
      <div className="message-timestamp">
        {formatTime(message.timestamp)}
      </div>
    </div>
  )
}

export default MessageBubble