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
        const connectTimeout = setTimeout(() => {
            ws.current = new WebSocket(`${WS_URL}/ws/chat`)

            ws.current.onopen = () => setConnected(true)

            ws.current.onmessage = (event) => {
                const text = event.data
                const isSystem = text.startsWith("[File received")
                setMessages(prev => [...prev, {
                    text: text,
                    sender: isSystem ? "system" : "peer"
                }])
            }

            ws.current.onclose = () => {
                setConnected(false)
                setMessages(prev => [...prev, {
                    text: "Session ended — peer disconnected",
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
        setMessages(prev => [...prev, {
            text: input,
            sender: "me"
        }])
        setInput("")
    }

    function handleKeyDown(e) {
        if (e.key === "Enter") sendMessage()
    }

    async function sendFile(e) {
        const file = e.target.files[0]
        if (!file) return

        setMessages(prev => [...prev, {
            text: `Sending file: ${file.name}...`,
            sender: "system"
        }])

        const formData = new FormData()
        formData.append("file", file)

        try {
            const response = await axios.post(`${API_URL}/send/file`, formData, {
                headers: { "Content-Type": "multipart/form-data" }
            })
            if (response.data.status === "sent") {
                setMessages(prev => [...prev, {
                    text: `File sent: ${file.name}`,
                    sender: "system"
                }])
            } else {
                setFileError(`File transfer failed: ${response.data.error}`)
            }
            setFileError("")
        } catch (err) {
            setFileError(`File transfer failed: ${err.message}`)
        }

        e.target.value = ""
    }

    async function disconnect() {
        await axios.post(`${API_URL}/disconnect`)
        if (ws.current) ws.current.close()
        setMessages(prev => [...prev, {
            text: "You disconnected",
            sender: "system"
        }])
        setConnected(false)
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>

            {/* header */}
            <div style={{
                padding: "10px",
                borderBottom: "1px solid #ccc",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between"
            }}>
                <span>
                    Status: {connected
                        ? <span style={{ color: "green" }}>Connected</span>
                        : <span style={{ color: "red" }}>Disconnected</span>
                    }
                </span>
                <button onClick={disconnect} style={{ padding: "6px 12px" }}>
                    Disconnect
                </button>
            </div>

            {/* message area */}
            <div style={{ flex: 1, overflowY: "auto", padding: "10px" }}>
                {messages.map((msg, i) => (
                    <div key={i} style={{
                        textAlign: msg.sender === "me" ? "right" :
                                   msg.sender === "system" ? "center" : "left",
                        margin: "5px 0"
                    }}>
                        {msg.sender === "system" ? (
                            <span style={{
                                color: "gray",
                                fontSize: "12px",
                                fontStyle: "italic"
                            }}>
                                {msg.text}
                            </span>
                        ) : (
                            <span style={{
                                background: msg.sender === "me" ? "#0084ff" : "#e5e5ea",
                                color: msg.sender === "me" ? "white" : "black",
                                padding: "8px 12px",
                                borderRadius: "18px",
                                display: "inline-block",
                                maxWidth: "70%",
                                wordBreak: "break-word"
                            }}>
                                {msg.text}
                            </span>
                        )}
                    </div>
                ))}
                <div ref={messagesEnd} />
            </div>

            {/* file error */}
            {fileError && (
                <p style={{ color: "red", padding: "5px", textAlign: "center", margin: 0 }}>
                    {fileError}
                </p>
            )}

            {/* input area */}
            <div style={{
                padding: "10px",
                borderTop: "1px solid #ccc",
                display: "flex",
                gap: "8px",
                alignItems: "center"
            }}>
                <label style={{
                    cursor: "pointer",
                    padding: "8px",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    userSelect: "none"
                }}>
                    📎
                    <input
                        type="file"
                        style={{ display: "none" }}
                        onChange={sendFile}
                    />
                </label>
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type a message..."
                    style={{
                        flex: 1,
                        padding: "8px",
                        borderRadius: "4px",
                        border: "1px solid #ccc"
                    }}
                />
                <button
                    onClick={sendMessage}
                    style={{ padding: "8px 16px" }}
                >
                    Send
                </button>
            </div>
        </div>
    )
}