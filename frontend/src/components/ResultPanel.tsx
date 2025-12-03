import { useRef, useEffect } from 'react'
import { ToastType } from '../App'
import './ResultPanel.css'

interface R2Asset {
  url: string
  key: string
  content_type: string
  size_bytes: number
}

interface GenerationAssets {
  images_downloaded: number
  images_processed: number
  script_generated: boolean
  script?: string
  voiceover_generated: boolean
  qr_generated: boolean
  uploaded_to_r2: boolean
  r2_urls?: {
    processed_images: R2Asset[]
    voiceover: R2Asset | null
    qr_code: R2Asset | null
  }
}

interface ResultPanelProps {
  stockNumber: string
  assets: GenerationAssets
  onRegenerate: () => void
  isRegenerating: boolean
  showToast: (message: string, type: ToastType) => void
}

function ResultPanel({ stockNumber, assets, onRegenerate, isRegenerating, showToast }: ResultPanelProps) {
  const audioRef = useRef<HTMLAudioElement>(null)

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    showToast(`${label} copied to clipboard!`, 'success')
  }

  // Reset audio to beginning when it ends
  const handleAudioEnded = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0
      audioRef.current.load() // Reload to ensure proper reset
    }
  }

  // Handle regenerate with audio reset
  const handleRegenerate = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    onRegenerate()
  }

  // Reset audio when voiceover URL changes (after regeneration)
  useEffect(() => {
    if (audioRef.current && assets.r2_urls?.voiceover) {
      audioRef.current.load()
      audioRef.current.currentTime = 0
    }
  }, [assets.r2_urls?.voiceover?.url])

  return (
    <div className="result-panel">
      <div className="result-header">
        <div className="result-title-row">
          <h3>Assets Generated for Review.</h3>
          <button 
            className="btn btn-regenerate"
            onClick={handleRegenerate}
            disabled={isRegenerating}
          >
            {isRegenerating ? (
              <>
                <div className="spinner"></div>
                Regenerating...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Regenerate
              </>
            )}
          </button>
        </div>
        <span className="stock-badge">{stockNumber}</span>
      </div>

      {/* Summary Stats */}
      <div className="result-stats">
        <div className="stat">
          <span className="stat-value">{assets.images_processed}</span>
          <span className="stat-label">Images Processed</span>
        </div>
        <div className="stat">
          <span className="stat-icon">{assets.script_generated ? '✓' : '✗'}</span>
          <span className="stat-label">Script</span>
        </div>
        <div className="stat">
          <span className="stat-icon">{assets.voiceover_generated ? '✓' : '✗'}</span>
          <span className="stat-label">Voiceover</span>
        </div>
        <div className="stat">
          <span className="stat-icon">{assets.qr_generated ? '✓' : '✗'}</span>
          <span className="stat-label">QR Code</span>
        </div>
      </div>

      {/* Processed Images */}
      {assets.r2_urls?.processed_images && assets.r2_urls.processed_images.length > 0 && (
        <div className="result-section">
          <h4>📸 Processed Images (Background Removed)</h4>
          <div className="images-grid">
            {assets.r2_urls.processed_images.map((img, idx) => (
              <div key={idx} className="image-card">
                <img src={img.url} alt={`Processed ${idx + 1}`} />
                <button 
                  className="btn-copy-url"
                  onClick={() => copyToClipboard(img.url, 'Image URL')}
                  title="Copy URL"
                >
                  📋
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Voiceover */}
      {assets.r2_urls?.voiceover && (
        <div className="result-section">
          <h4>🎙️ Voiceover</h4>
          <div className="audio-player-container">
            <audio 
              key={assets.r2_urls.voiceover.url}
              ref={audioRef}
              controls 
              className="audio-player"
              onEnded={handleAudioEnded}
            >
              <source src={assets.r2_urls.voiceover.url} type="audio/mpeg" />
              Your browser does not support the audio element.
            </audio>
            <button 
              className="btn-copy-url"
              onClick={() => copyToClipboard(assets.r2_urls!.voiceover!.url, 'Voiceover URL')}
              title="Copy URL"
            >
              📋 Copy URL
            </button>
          </div>
        </div>
      )}

      {/* Script */}
      {assets.script && (
        <div className="result-section">
          <h4>📝 Generated Script</h4>
          <div className="script-container">
            <p className="script-text">{assets.script}</p>
            <button 
              className="btn-copy-url"
              onClick={() => copyToClipboard(assets.script!, 'Script')}
            >
              📋 Copy Script
            </button>
          </div>
        </div>
      )}

      {/* QR Code */}
      {assets.r2_urls?.qr_code && (
        <div className="result-section">
          <h4>📱 QR Code</h4>
          <div className="qr-container">
            <img src={assets.r2_urls.qr_code.url} alt="QR Code" className="qr-image" />
            <button 
              className="btn-copy-url"
              onClick={() => copyToClipboard(assets.r2_urls!.qr_code!.url, 'QR Code URL')}
            >
              📋 Copy URL
            </button>
          </div>
        </div>
      )}

      {/* Confirm Assets Button */}
      <div className="result-actions">
        <button 
          className="btn btn-confirm-assets"
          onClick={() => {}}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Confirm Assets for Video Generation
        </button>
      </div>

      <p className="result-hint">
        All assets uploaded to cloud storage. Click 📋 to copy URLs.
      </p>
    </div>
  )
}

export default ResultPanel
