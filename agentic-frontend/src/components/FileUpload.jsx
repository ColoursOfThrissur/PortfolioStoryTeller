import { useRef } from 'react'

function FileUpload({ onUpload, disabled }) {
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      onUpload(file)
    }
  }

  return (
    <div className="file-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.xls,.csv"
        onChange={handleFileChange}
        disabled={disabled}
        style={{ display: 'none' }}
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={disabled}
        className="btn-upload"
      >
        📁 Upload Portfolio
      </button>
    </div>
  )
}

export default FileUpload
