import { useState, useEffect } from 'react'
import axios from 'axios'
import { API_URL } from '../config'

export default function WaitingScreen({ onConnected }) {
    const [ip, setIp] = useState("")

    useEffect(() => {
        axios.get(`${API_URL}/status`)
            .then(res => setIp(res.data.peer_ip))

        const interval = setInterval(async () => {
            const response = await axios.get(`${API_URL}/status`)
            if (response.data.connected === true) {
                clearInterval(interval)
                onConnected()
            }
        }, 2000)

        return () => clearInterval(interval)
    }, [])

    return (
        <div>
            <h1>Waiting for Peer...</h1>
            <p>Share your IP address with your peer:</p>
            <h2>{ip || "loading..."}</h2>
            <p>Listening for incoming connection...</p>
        </div>
    )
}