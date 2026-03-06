import { useState } from 'react'
import { Upload, FileText } from 'lucide-react'

function FileUploadMessage({ onFileUpload, loading }) {
  const [dragOver, setDragOver] = useState(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFile(files[0])
    }
  }

  const handleFileSelect = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      handleFile(files[0])
    }
  }

  const handleFile = (file) => {
    const validTypes = [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv'
    ]
    
    if (!validTypes.includes(file.type)) {
      alert('Please upload an Excel (.xlsx, .xls) or CSV file')
      return
    }
    
    onFileUpload(file)
  }

  return (
    <div className="file-upload-message">
      <div 
        className={`file-upload-area ${dragOver ? 'dragover' : ''}`}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => document.getElementById('file-input').click()}
      >
        <div className="upload-icon">
          <Upload size={32} />
        </div>
        <div className="upload-text">
          {loading ? 'Processing file...' : 'Upload Portfolio File'}
        </div>
        <div className="upload-subtext">
          Drop your Excel or CSV file here, or click to browse
        </div>
        
        <input
          id="file-input"
          type="file"
          accept=".xlsx,.xls,.csv"
          onChange={handleFileSelect}
          disabled={loading}
          className="file-input"
        />
      </div>
    </div>
  )
}

export default FileUploadMessage