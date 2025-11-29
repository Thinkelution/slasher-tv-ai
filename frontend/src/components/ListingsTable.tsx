import { useState, useEffect } from 'react'
import { ToastType } from '../App'
import './ListingsTable.css'

interface ListingsTableProps {
  showToast: (message: string, type: ToastType) => void
}

interface Listing {
  stock_number: string
  dealer_id: string
  year: number
  make: string
  model: string
  price: number
  color: string
  has_script: boolean
  has_voiceover: boolean
  has_qr: boolean
  image_count: number
}

function ListingsTable({ showToast }: ListingsTableProps) {
  const [listings, setListings] = useState<Listing[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [regeneratingId, setRegeneratingId] = useState<string | null>(null)

  const loadListings = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/listings')
      const data = await response.json()
      setListings(data.listings || [])
    } catch {
      showToast('Failed to load listings', 'error')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadListings()
  }, [])

  const handleRegenerate = async (stockNumber: string) => {
    if (!confirm(`Regenerate video assets for ${stockNumber}?`)) return

    setRegeneratingId(stockNumber)
    try {
      const response = await fetch(`/api/regenerate/${stockNumber}`, {
        method: 'POST'
      })

      if (!response.ok) throw new Error('Regeneration failed')

      showToast(`Regeneration started for ${stockNumber}`, 'success')
      setTimeout(loadListings, 5000)
    } catch {
      showToast('Regeneration failed', 'error')
    } finally {
      setRegeneratingId(null)
    }
  }

  if (isLoading) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
            Existing Listings
          </h2>
        </div>
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading listings...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
          Existing Listings
        </h2>
        <button className="btn btn-secondary btn-sm" onClick={loadListings}>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {listings.length === 0 ? (
        <div className="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p>No listings found</p>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Stock #</th>
                <th>Year</th>
                <th>Model</th>
                <th>Price</th>
                <th>Images</th>
                <th>Script</th>
                <th>Voice</th>
                <th>QR</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {listings.map((listing) => (
                <tr key={listing.stock_number}>
                  <td><strong>{listing.stock_number}</strong></td>
                  <td>{listing.year}</td>
                  <td>{listing.make} {listing.model}</td>
                  <td className="price">${listing.price?.toLocaleString() || 'N/A'}</td>
                  <td>{listing.image_count} photos</td>
                  <td>{listing.has_script ? <span className="badge badge-success">✓</span> : <span className="badge badge-warning">—</span>}</td>
                  <td>{listing.has_voiceover ? <span className="badge badge-success">✓</span> : <span className="badge badge-warning">—</span>}</td>
                  <td>{listing.has_qr ? <span className="badge badge-success">✓</span> : <span className="badge badge-warning">—</span>}</td>
                  <td>
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleRegenerate(listing.stock_number)}
                      disabled={regeneratingId === listing.stock_number}
                    >
                      {regeneratingId === listing.stock_number ? <div className="spinner-sm"></div> : 'Regenerate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default ListingsTable
