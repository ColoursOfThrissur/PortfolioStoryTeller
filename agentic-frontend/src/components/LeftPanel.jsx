import { X, Clock, CheckCircle, AlertCircle } from 'lucide-react'

function LeftPanel({ isOpen, onClose, agentHistory }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="status-icon success" />
      case 'error':
        return <AlertCircle size={16} className="status-icon error" />
      default:
        return <Clock size={16} className="status-icon pending" />
    }
  }

  return (
    <div className={`panel left ${isOpen ? 'open' : 'closed'}`}>
      <div className="panel-header">
        <h3>Agent History</h3>
        <button className="panel-close" onClick={onClose}>
          <X size={16} />
        </button>
      </div>
      
      <div className="panel-content">
        <div className="history-list">
          {agentHistory.map((session) => (
            <div key={session.id} className="history-item">
              <div className="history-header">
                <span className="client-name">{session.client}</span>
                {getStatusIcon(session.status)}
              </div>
              <div className="history-details">
                <span className="period">{session.period}</span>
                <span className="date">{new Date(session.date).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
        
        {agentHistory.length === 0 && (
          <div className="empty-state">
            <Clock size={32} className="empty-icon" />
            <p>No previous sessions</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default LeftPanel