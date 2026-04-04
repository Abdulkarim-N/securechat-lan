import { useState, useEffect } from 'react'
import axios from 'axios'

export default function TestComponent() {
    const [status, setStatus] = useState(null)

    useEffect(() => {
        axios.get('http://localhost:8000/status')
            .then(res => setStatus(res.data))
    }, [])

    return (
        <div>
            <h1>SecureChat LAN</h1>
            <p>Status: {status ? JSON.stringify(status) : 'loading...'}</p>
        </div>
    )
}