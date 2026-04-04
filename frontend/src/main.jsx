import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import TestComponent from './testcomponent.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    
    <TestComponent />
  </StrictMode>,
)
