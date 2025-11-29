import { ToastState } from '../App'
import './Toast.css'

interface ToastProps {
  toast: ToastState
}

function Toast({ toast }: ToastProps) {
  if (!toast.show) return null

  return (
    <div className={`toast ${toast.type}`}>
      <span>{toast.message}</span>
    </div>
  )
}

export default Toast
