import { useState } from 'react'
import ConnectionScreen from './components/ConnectionScreen'
import WaitingScreen from './components/WaitingScreen'
import FingerprintScreen from './components/FingerprintScreen'
import ChatScreen from './components/ChatScreen'

export default function App() {
    const [screen, setScreen] = useState("connection")

    if (screen === "waiting") return (
        <WaitingScreen onConnected={() => setScreen("fingerprint")} />
    )
    if (screen === "fingerprint") return (
        <FingerprintScreen onVerified={() => setScreen("chat")} />
    )
    if (screen === "chat") return (
        <ChatScreen />
    )
    return (
        <ConnectionScreen
            onHost={() => setScreen("waiting")}
            onConnect={() => setScreen("fingerprint")}
        />
    )
}