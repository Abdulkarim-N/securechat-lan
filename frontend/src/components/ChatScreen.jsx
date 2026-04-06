import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { API_URL, WS_URL } from '../config'

export default function ChatScreen() {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState("")
    const [connected, setConnected] = useState(false)
    const [fileError, setFileError] = useState("")
    const ws = useRef(null)
    const messagesEnd = useRef(null)

    useEffect(() => {
        // small delay to ensure backend is ready
        const connectTimeout = setTimeout(() => {
            ws.current = new WebSocket(`${WS_URL}/ws/chat`)

            ws.current.onopen = () => setConnected(true)

            ws.current.onmessage = (event) => {
                const text = event.data
                setMessages(prev => [...prev, {
                    text: text,
                    sender: "peer",
                    isFile: text.startsWith("[File received")
                }])
            }

            ws.current.onclose = () => {
                setConnected(false)
                setMessages(prev => [...prev, {
                    text: "Peer disconnected",
                    sender: "system"
                }])
            }

            ws.current.onerror = () => setConnected(false)
        }, 1000)

        return () => {
            clearTimeout(connectTimeout)
            if (ws.current) ws.current.close()
        }
    }, [])

    useEffect(() => {
        messagesEnd.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    function sendMessage() {
        if (input.trim() === "" || !ws.current) return
        ws.current.send(input)
        setMessages(prev => [...prev, { text: input, sender: "me" }])
        setInput("")
    }

    function handleKeyDown(e) {
        if (e.key === "Enter") sendMessage()
    }

    async function sendFile(e) {
        const file = e.target.files[0]
        if (!file) return

        const formData = new FormData()
        formData.append("file", file)

        try {
            await axios.post(`${API_URL}/send/file`, formData, {
                headers: { "Content-Type": "multipart/form-data" }
            })
            setMessages(prev => [...prev, {
                text: `File sent: ${file.name}`,
                sender: "system"
            }])
            setFileError("")
        } catch {
            setFileError("File transfer failed")
        }
    }

    async function disconnect() {
        await axios.post(`${API_URL}/disconnect`)
        if (ws.current) ws.current.close()
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
            <div style={{ padding: "10px", borderBottom: "1px solid #ccc" }}>
                <span>Status: {connected ? "Connected" : "Disconnected"}</span>
                <button onClick={disconnect} style={{ marginLeft: "10px" }}>
                    Disconnect
                </button>
            </div>

            <div style={{ flex: 1, overflowY: "auto", padding: "10px" }}>
                {messages.map((msg, i) => (
                    <div key={i} style={{
                        textAlign: msg.sender === "me" ? "right" : "left",
                        margin: "5px 0",
                        color: msg.sender === "system" ? "gray" : "black"
                    }}>
                        <span style={{
                            background: msg.sender === "me" ? "#0084ff" : "#e5e5ea",
                            color: msg.sender === "me" ? "white" : "black",
                            padding: "8px 12px",
                            borderRadius: "18px",
                            display: "inline-block",
                            maxWidth: "70%"
                        }}>
                            {msg.text}
                        </span>
                    </div>
                ))}
                <div ref={messagesEnd} />
            </div>

            {fileError && <p style={{ color: "red", padding: "5px" }}>{fileError}</p>}

            <div style={{ padding: "10px", borderTop: "1px solid #ccc", display: "flex", gap: "8px" }}>
                <label style={{ cursor: "pointer", padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }}>
                    📎
                    <input type="file" style={{ display: "none" }} onChange={sendFile} />
                </label>
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type a message..."
                    style={{ flex: 1, padding: "8px", borderRadius: "4px", border: "1px solid #ccc" }}
                />
                <button onClick={sendMessage} style={{ padding: "8px 16px" }}>
                    Send
                </button>
            </div>
        </div>
    )
}