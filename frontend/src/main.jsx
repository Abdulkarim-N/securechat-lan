import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import TestComponent from './testcomponent.jsx'
import ConnectionScreen from './components/ConnectionScreen.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <h1>test</h1>
    <TestComponent />
    <ConnectionScreen />
  </StrictMode>,
)
