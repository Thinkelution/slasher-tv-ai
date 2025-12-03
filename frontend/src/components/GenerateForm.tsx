import { useState, useEffect } from 'react'
import { ToastType } from '../App'
import ResultPanel from './ResultPanel'
import './GenerateForm.css'

interface GenerateFormProps {
  showToast: (message: string, type: ToastType) => void
}

export interface FormData {
  stock_number: string
  vin: string
  year: string
  make: string
  model: string
  price: string
  condition: string
  color: string
  odometer: string
  engine_displacement: string
  voice_style: string
  listing_url: string
  description: string
  photo_urls: string
  background_music: string
  music_volume: number
}

// Music track from Jamendo API
interface MusicTrack {
  id: string
  name: string
  artist_name: string
  duration: number
  audio: string
}

// Jamendo API client ID (free tier)
const JAMENDO_CLIENT_ID = '2c9a11b9'

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

interface GenerationResult {
  stockNumber: string
  assets: GenerationAssets
}

const initialFormData: FormData = {
  stock_number: '',
  vin: '',
  year: '',
  make: 'Harley-Davidson',
  model: '',
  price: '',
  condition: 'Used',
  color: '',
  odometer: '',
  engine_displacement: '',
  voice_style: 'aggressive',
  listing_url: '',
  description: '',
  photo_urls: '',
  background_music: 'none',
  music_volume: 30
}

// Processing steps for the overlay
const PROCESSING_STEPS = [
  { id: 'download', label: 'Downloading Images', icon: '📥' },
  { id: 'background', label: 'Cleaning Background', icon: '🖼️' },
  { id: 'script', label: 'Generating Script', icon: '📝' },
  { id: 'voiceover', label: 'Generating Voiceover', icon: '🎙️' },
  { id: 'qr', label: 'Creating QR Code', icon: '📱' },
  { id: 'upload', label: 'Uploading to Cloud', icon: '☁️' },
  { id: 'complete', label: 'Finalizing Assets', icon: '✨' }
]

function GenerateForm({ showToast }: GenerateFormProps) {
  const [formData, setFormData] = useState<FormData>(initialFormData)
  const [isLoading, setIsLoading] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [musicTracks, setMusicTracks] = useState<MusicTrack[]>([])
  const [isMusicLoading, setIsMusicLoading] = useState(true)
  const [previewAudio, setPreviewAudio] = useState<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [showOverlay, setShowOverlay] = useState(false)

  // Fetch music tracks from Jamendo API
  useEffect(() => {
    const fetchMusic = async () => {
      try {
        const response = await fetch(
          `https://api.jamendo.com/v3.0/tracks/?client_id=${JAMENDO_CLIENT_ID}&format=json&limit=15&tags=energetic+rock&include=musicinfo&groupby=artist_id`
        )
        const data = await response.json()
        
        if (data.results) {
          const tracks: MusicTrack[] = data.results.map((track: any) => ({
            id: track.id,
            name: track.name,
            artist_name: track.artist_name,
            duration: track.duration,
            audio: track.audio
          }))
          setMusicTracks(tracks)
        }
      } catch (error) {
        console.error('Failed to fetch music:', error)
        showToast('Failed to load music tracks', 'error')
      } finally {
        setIsMusicLoading(false)
      }
    }

    fetchMusic()
  }, [])

  // Handle music preview toggle (play/pause)
  const handleMusicPreview = (audioUrl: string) => {
    // If currently playing the same track, pause it
    if (previewAudio && isPlaying) {
      previewAudio.pause()
      setIsPlaying(false)
      return
    }
    
    // If different track or not playing, start new
    if (previewAudio) {
      previewAudio.pause()
    }
    
    if (audioUrl && audioUrl !== 'none') {
      const audio = new Audio(audioUrl)
      audio.volume = 0.3
      audio.play()
      setPreviewAudio(audio)
      setIsPlaying(true)
      
      // When track ends, reset playing state
      audio.onended = () => {
        setIsPlaying(false)
      }
    }
  }

  // Stop preview when music selection changes
  useEffect(() => {
    if (previewAudio) {
      previewAudio.pause()
      setIsPlaying(false)
    }
  }, [formData.background_music])

  // Stop preview on unmount
  useEffect(() => {
    return () => {
      if (previewAudio) {
        previewAudio.pause()
      }
    }
  }, [previewAudio])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const generateVideo = async () => {
    // Send data as strings (API expects strings for year, price, odometer)
    const payload = {
      ...formData,
      music_volume: formData.music_volume
    }

    // Use relative URL - works with both dev proxy and production subdirectory
    const apiBase = import.meta.env.PROD ? '/slasher/api' : '/api'
    const response = await fetch(`${apiBase}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Generation failed')
    }

    const data = await response.json()
    return data
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setResult(null)
    setShowOverlay(true)
    setCurrentStep(0)

    // Simulate step progression while API processes
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < PROCESSING_STEPS.length - 1) {
          return prev + 1
        }
        return prev
      })
    }, 2500) // Change step every 2.5 seconds

    try {
      const data = await generateVideo()
      
      // Complete all steps
      setCurrentStep(PROCESSING_STEPS.length - 1)
      
      // Small delay to show completion
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Backend returns { success, stock_number, listing_dir, assets, message }
      setResult({
        stockNumber: data.stock_number,
        assets: data.assets
      })
      
      showToast('Assets generated successfully!', 'success')
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Generation failed', 'error')
    } finally {
      clearInterval(stepInterval)
      setIsLoading(false)
      setShowOverlay(false)
    }
  }

  const handleRegenerate = async () => {
    setIsRegenerating(true)
    setShowOverlay(true)
    setCurrentStep(0)

    // Simulate step progression while API processes
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < PROCESSING_STEPS.length - 1) {
          return prev + 1
        }
        return prev
      })
    }, 2500)

    try {
      const data = await generateVideo()
      
      // Complete all steps
      setCurrentStep(PROCESSING_STEPS.length - 1)
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setResult({
        stockNumber: data.stock_number,
        assets: data.assets
      })
      
      showToast('Assets regenerated successfully!', 'success')
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Regeneration failed', 'error')
    } finally {
      clearInterval(stepInterval)
      setIsRegenerating(false)
      setShowOverlay(false)
    }
  }

  const clearForm = () => {
    setFormData(initialFormData)
    setResult(null)
  }

  return (
    <div className="card">
      {/* Processing Overlay */}
      {showOverlay && (
        <div className="processing-overlay">
          <div className="processing-modal">
            <div className="processing-spinner"></div>
            <h3 className="processing-title">Generating Assets</h3>
            <div className="processing-steps">
              {PROCESSING_STEPS.map((step, index) => (
                <div 
                  key={step.id} 
                  className={`processing-step ${index < currentStep ? 'completed' : ''} ${index === currentStep ? 'active' : ''}`}
                >
                  <span className="step-icon">{step.icon}</span>
                  <span className="step-label">{step.label}</span>
                  {index < currentStep && <span className="step-check">✓</span>}
                  {index === currentStep && <span className="step-dots">...</span>}
                </div>
              ))}
            </div>
            <p className="processing-hint">Please wait while we process your request</p>
          </div>
        </div>
      )}

      <div className="card-header">
        <h2 className="card-title">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Enter Details <span className="title-hint">(Represents 1 row of Sample CSV)</span>
        </h2>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="stock_number">Stock Number *</label>
            <input type="text" id="stock_number" name="stock_number" value={formData.stock_number} onChange={handleChange} required placeholder="e.g., 123456BB" />
          </div>

          <div className="form-group">
            <label htmlFor="vin">VIN *</label>
            <input type="text" id="vin" name="vin" value={formData.vin} onChange={handleChange} required placeholder="Vehicle ID Number" />
          </div>

          <div className="form-group">
            <label htmlFor="year">Year *</label>
            <input type="number" id="year" name="year" value={formData.year} onChange={handleChange} required placeholder="2024" min="1900" max="2030" />
          </div>

          <div className="form-group">
            <label htmlFor="make">Make *</label>
            <input type="text" id="make" name="make" value={formData.make} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label htmlFor="model">Model *</label>
            <input type="text" id="model" name="model" value={formData.model} onChange={handleChange} required placeholder="e.g., Low Rider ST" />
          </div>

          <div className="form-group">
            <label htmlFor="price">Price *</label>
            <input type="number" id="price" name="price" value={formData.price} onChange={handleChange} required placeholder="19999" min="0" />
          </div>

          <div className="form-group">
            <label htmlFor="condition">Condition</label>
            <select id="condition" name="condition" value={formData.condition} onChange={handleChange}>
              <option value="Used">Used</option>
              <option value="New">New</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="color">Color</label>
            <input type="text" id="color" name="color" value={formData.color} onChange={handleChange} placeholder="e.g., Vivid Black" />
          </div>

          <div className="form-group">
            <label htmlFor="odometer">Mileage</label>
            <input type="number" id="odometer" name="odometer" value={formData.odometer} onChange={handleChange} placeholder="e.g., 5000" min="0" />
          </div>

          <div className="form-group">
            <label htmlFor="engine_displacement">Engine</label>
            <input type="text" id="engine_displacement" name="engine_displacement" value={formData.engine_displacement} onChange={handleChange} placeholder="e.g., Milwaukee-Eight 117" />
          </div>

          <div className="form-group">
            <label htmlFor="voice_style">Voice Style</label>
            <select id="voice_style" name="voice_style" value={formData.voice_style} onChange={handleChange}>
              <option value="aggressive">Aggressive (High Energy)</option>
              <option value="smooth">Smooth (Sophisticated)</option>
              <option value="professional">Professional (Clear)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="background_music">Background Music {isMusicLoading && '(Loading...)'}</label>
            <div className="music-select-container">
              <select 
                id="background_music" 
                name="background_music" 
                value={formData.background_music} 
                onChange={handleChange}
                disabled={isMusicLoading}
              >
                <option value="none">No Music - Voiceover only</option>
                {musicTracks.map(track => (
                  <option key={track.id} value={track.audio}>
                    {track.name} - {track.artist_name} ({Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')})
                  </option>
                ))}
              </select>
              <button
                type="button"
                className={`btn-preview ${isPlaying ? 'playing' : ''}`}
                onClick={() => handleMusicPreview(formData.background_music)}
                disabled={formData.background_music === 'none' || !formData.background_music}
                title={isPlaying ? "Pause preview" : "Play preview"}
              >
                {isPlaying ? '⏸' : '▶'}
              </button>
            </div>
            <span className="music-hint">Royalty-free music from Jamendo</span>
          </div>

          <div className="form-group">
            <label htmlFor="music_volume">Music Volume: {formData.music_volume}%</label>
            <div className="volume-slider-container">
              <span className="volume-icon">🔈</span>
              <input
                type="range"
                id="music_volume"
                name="music_volume"
                min="0"
                max="100"
                value={formData.music_volume}
                onChange={handleChange}
                className="volume-slider"
              />
              <span className="volume-icon">🔊</span>
            </div>
            <span className="volume-hint">Lower = voiceover dominant, Higher = music dominant</span>
          </div>

          <div className="form-group">
            <label htmlFor="listing_url">Listing URL</label>
            <input type="url" id="listing_url" name="listing_url" value={formData.listing_url} onChange={handleChange} placeholder="https://..." />
          </div>

          <div className="form-group full-width">
            <label htmlFor="description">Description</label>
            <textarea id="description" name="description" value={formData.description} onChange={handleChange} placeholder="Enter vehicle description..." />
          </div>

          <div className="form-group full-width">
            <label htmlFor="photo_urls">Photo URLs (comma separated)</label>
            <textarea id="photo_urls" name="photo_urls" value={formData.photo_urls} onChange={handleChange} placeholder="https://example.com/photo1.jpg, https://example.com/photo2.jpg" />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={isLoading || isRegenerating}>
            {isLoading ? (
              <>
                <div className="spinner"></div>
                Generating...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Generate Assets
              </>
            )}
          </button>
          <button type="button" className="btn btn-secondary" onClick={clearForm}>
            Clear Form
          </button>
        </div>
      </form>

      {result && (
        <ResultPanel
          stockNumber={result.stockNumber}
          assets={result.assets}
          onRegenerate={handleRegenerate}
          isRegenerating={isRegenerating}
          showToast={showToast}
        />
      )}
    </div>
  )
}

export default GenerateForm
