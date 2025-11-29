import { useState } from 'react'
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
}

interface GenerationResult {
  videoUrl: string
  stockNumber: string
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
  photo_urls: ''
}

function GenerateForm({ showToast }: GenerateFormProps) {
  const [formData, setFormData] = useState<FormData>(initialFormData)
  const [isLoading, setIsLoading] = useState(false)
  const [isRegenerating, setIsRegenerating] = useState(false)
  const [result, setResult] = useState<GenerationResult | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const generateVideo = async () => {
    const payload = {
      ...formData,
      year: parseInt(formData.year),
      price: parseFloat(formData.price),
      odometer: formData.odometer ? parseInt(formData.odometer) : null
    }

    const response = await fetch('/api/generate', {
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

    try {
      const data = await generateVideo()
      
      // Expecting backend to return { video_url: "https://cloudinary.com/..." }
      setResult({
        videoUrl: data.video_url,
        stockNumber: formData.stock_number
      })
      
      showToast('Video generated successfully!', 'success')
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Generation failed', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRegenerate = async () => {
    setIsRegenerating(true)

    try {
      const data = await generateVideo()
      
      setResult({
        videoUrl: data.video_url,
        stockNumber: formData.stock_number
      })
      
      showToast('Video regenerated successfully!', 'success')
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Regeneration failed', 'error')
    } finally {
      setIsRegenerating(false)
    }
  }

  const clearForm = () => {
    setFormData(initialFormData)
    setResult(null)
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          New Video Generation
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
                Generate Video
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
          videoUrl={result.videoUrl}
          stockNumber={result.stockNumber}
          onRegenerate={handleRegenerate}
          isRegenerating={isRegenerating}
          showToast={showToast}
        />
      )}
    </div>
  )
}

export default GenerateForm
