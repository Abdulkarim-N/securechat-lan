import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_URL } from '../config'

export default function FingerprintScreen({ onVerified }) {
    const [fingerprint, setFingerprint] = useState("")
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    useEffect(() => {
        // wait 3 seconds for both peers to reach this screen
        const startDelay = setTimeout(() => {
            axios.post(`${API_URL}/handshake`)
        }, 3000)

        // poll for result every 2 seconds
        const interval = setInterval(async () => {
            try {
                const res = await axios.get(`${API_URL}/handshake/status`)
                if (res.data.status === "complete") {
                    setFingerprint(res.data.fingerprint)
                    setLoading(false)
                    clearInterval(interval)
                } else if (res.data.status === "error") {
                    setError(res.data.error)
                    setLoading(false)
                    clearInterval(interval)
                }
            } catch {
                setError("Could not reach backend")
                setLoading(false)
                clearInterval(interval)
            }
        }, 2000)

        return () => {
            clearTimeout(startDelay)
            clearInterval(interval)
        }
    }, [])

    async function confirmFingerprint() {
        await axios.post(`${API_URL}/verify`, { confirmed: true })
        onVerified()
    }

    return (
        <div>
            <h1>Verify Peer Fingerprint</h1>

            {loading && (
                <>
                    <p>Performing handshake...</p>
                    <p>Waiting for both peers — this may take a few seconds</p>
                </>
            )}

            {error && (
                <>
                    <p style={{ color: "red" }}>{error}</p>
                    <button onClick={() => window.location.reload()}>
                        Try Again
                    </button>
                </>
            )}

            {fingerprint && (
                <>
                    <p>Compare this fingerprint with your peer out of band:</p>
                    <h2 style={{ fontFamily: "monospace", wordBreak: "break-all" }}>
                        {fingerprint}
                    </h2>
                    <p>If both fingerprints match, your connection is secure.</p>
                    <button onClick={confirmFingerprint}>
                        Confirm and Continue
                    </button>
                </>
            )}
        </div>
    )
}