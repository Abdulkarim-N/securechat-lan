import { useState } from 'react'
import axios from 'axios'

export default function ConnectionScreen() {
    const [ip, setIp] = useState("")
    const [error, setError] = useState("")

    async function startHost() {
        const response = await axios.post("http://127.0.0.1:8000/connect/host")
        console.log(response.data)
    }

    async function connectClient(e) {
        e.preventDefault()
        
        if (ip.trim() === "") { // if ip is empty
            setError("Please enter an IP address")
            return
        }
        
        try {
            const response = await axios.post("http://127.0.0.1:8000/connect/client", {
                ip: ip
            })
            if (response.data.status === "failed") {
                setError("Could not connect — is the host running?")
            } else {
                setError("")
                console.log(response.data)
            }
        } catch (err) {
            setError("Could not reach host — check the IP and try again")
        }
    }

    return <>
        <div>
            <button onClick={startHost}>Start Hosting</button>
        </div>
        <div>
            <form onSubmit={connectClient}>
                <input
                    type="text"
                    placeholder="Host IP"
                    value={ip}
                    onChange={e => setIp(e.target.value)}
                />
                <button type="submit">Connect to Peer</button>
            </form>
        </div>
        {error && <p style={{color: "red"}}>{error}</p>}
    </>
}