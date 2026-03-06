import { X, User, FileText, Calendar, CheckCircle, Circle } from 'lucide-react'

function RightPanel({ isOpen, onClose, collectedData, currentStep }) {
  const getStepStatus = (step, current) => {
    const steps = ['greeting', 'collecting_client_name', 'collecting_file', 'collecting_period', 'ready_to_generate', 'complete']
    const currentIndex = steps.indexOf(current)
    const stepIndex = steps.indexOf(step)
    
    if (stepIndex < currentIndex) return 'completed'
    if (stepIndex === currentIndex) return 'current'
    return 'pending'
  }

  const StatusIcon = ({ status }) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="status-icon success" />
      case 'current':
        return <Circle size={16} className="status-icon current" />
      default:
        return <Circle size={16} className="status-icon pending" />
    }
  }

  return (
    <div className={`panel right ${isOpen ? 'open' : 'closed'}`}>
      <div className="panel-header">
        <h3>Collected Details</h3>
        <button className="panel-close" onClick={onClose}>
          <X size={16} />
        </button>
      </div>
      
      <div className="panel-content">
        <div className="details-list">
          <div className="detail-item">
            <div className="detail-header">
              <User size={16} />
              <span>Client Name</span>
              <StatusIcon status={getStepStatus('collecting_client_name', currentStep)} />
            </div>
            <div className="detail-value">
              {collectedData.clientName || 'Not provided'}
            </div>
          </div>

          <div className="detail-item">
            <div className="detail-header">
              <FileText size={16} />
              <span>Portfolio File</span>
              <StatusIcon status={getStepStatus('collecting_file', currentStep)} />
            </div>
            <div className="detail-value">
              {collectedData.portfolioFile || 'Not uploaded'}
            </div>
            {collectedData.holdings && (
              <div className="detail-subtext">
                {collectedData.holdings.length} holdings found
              </div>
            )}
          </div>

          <div className="detail-item">
            <div className="detail-header">
              <Calendar size={16} />
              <span>Report Period</span>
              <StatusIcon status={getStepStatus('collecting_period', currentStep)} />
            </div>
            <div className="detail-value">
              {collectedData.period || 'Not specified'}
            </div>
          </div>
        </div>

        {collectedData.holdings && (
          <div className="holdings-section">
            <h4>Holdings Summary</h4>
            <div className="holdings-list">
              {collectedData.holdings.slice(0, 10).map((holding, i) => (
                <div key={i} className="holding-item">
                  <span className="ticker">{holding.ticker}</span>
                  <span className="shares">{holding.shares} shares</span>
                </div>
              ))}
              {collectedData.holdings.length > 10 && (
                <div className="holdings-more">
                  +{collectedData.holdings.length - 10} more
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default RightPanel