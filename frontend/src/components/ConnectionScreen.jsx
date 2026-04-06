import { useState } from 'react'
import axios from 'axios'
import { API_URL } from '../config'

export default function ConnectionScreen({ onHost, onConnect }) {
    const [ip, setIp] = useState("")
    const [error, setError] = useState("")

    async function startHost() {
        try {
            await axios.post(`${API_URL}/connect/host`)
            onHost()
        } catch {
            setError("Failed to start host")
        }
    }

    async function connectClient(e) {
        e.preventDefault()
        if (ip.trim() === "") {
            setError("Please enter an IP address")
            return
        }
        try {
            const response = await axios.post(`${API_URL}/connect/client`, { ip })
            if (response.data.status === "failed") {
                setError("Could not connect — is the host running?")
            } else {
                setError("")
                onConnect()
            }
        } catch {
            setError("Could not reach host — check the IP and try again")
        }
    }
console.log("API URL:", import.meta.env.VITE_API_URL)
    return (
        <div>
            <h1>SecureChat LAN</h1>
            <button onClick={startHost}>Start Hosting</button>
            <br /><br />
            <form onSubmit={connectClient}>
                <input
                    type="text"
                    placeholder="Host IP"
                    value={ip}
                    onChange={e => setIp(e.target.value)}
                />
                <button type="submit">Connect to Peer</button>
            </form>
            {error && <p style={{ color: "red" }}>{error}</p>}
        </div>
    )
}