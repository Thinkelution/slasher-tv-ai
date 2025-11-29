import { ToastType } from '../App'
import './ResultPanel.css'

interface ResultPanelProps {
  videoUrl: string
  stockNumber: string
  onRegenerate: () => void
  isRegenerating: boolean
  showToast: (message: string, type: ToastType) => void
}

function ResultPanel({ videoUrl, stockNumber, onRegenerate, isRegenerating }: ResultPanelProps) {
  return (
    <div className="result-panel">
      <div className="result-header">
        <h3>Generated Video</h3>
        <span className="stock-badge">{stockNumber}</span>
      </div>

      <div className="video-container">
        <video 
          controls 
          autoPlay
          className="video-player"
          key={videoUrl}
        >
          <source src={videoUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>

      <div className="result-actions">
        <button 
          className="btn btn-regenerate"
          onClick={onRegenerate}
          disabled={isRegenerating}
        >
          {isRegenerating ? (
            <>
              <div className="spinner"></div>
              Regenerating...
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Regenerate Video
            </>
          )}
        </button>
        
        <a 
          href={videoUrl} 
          download={`${stockNumber}_video.mp4`}
          className="btn btn-secondary"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download
        </a>
      </div>

      <p className="result-hint">
        Not satisfied with the result? Click "Regenerate Video" to create a new version.
      </p>
    </div>
  )
}

export default ResultPanel

