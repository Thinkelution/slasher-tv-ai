import { useState } from 'react'
import './App.css'

export type ToastType = 'success' | 'error' | 'info'

export interface ToastState {
  show: boolean
  message: string
  type: ToastType
}

function App() {
  const [activeTab, setActiveTab] = useState<'generate' | 'listings'>('generate')
  const [_toast, setToast] = useState<ToastState>({ show: false, message: '', type: 'success' })

  const showToast = (message: string, type: ToastType = 'success') => {
    setToast({ show: true, message, type })
    setTimeout(() => setToast(prev => ({ ...prev, show: false })), 4000)
  }

  return (
    <div className="container">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">S</div>
          <div>
            <h1>SLASHER TV AI</h1>
            <span>Video Generation Admin Panel</span>
          </div>
        </div>
      </header>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'generate' ? 'active' : ''}`}
          onClick={() => setActiveTab('generate')}
        >
          Generate New
        </button>
        <button 
          className={`tab ${activeTab === 'listings' ? 'active' : ''}`}
          onClick={() => { setActiveTab('listings'); showToast('Listings tab - coming soon', 'info') }}
        >
          Existing Listings
        </button>
      </div>

      <div className="card">
        <p style={{ color: 'var(--text-secondary)' }}>
          {activeTab === 'generate' ? 'Generate form coming next...' : 'Listings table coming soon...'}
        </p>
      </div>
    </div>
  )
}

export default App
