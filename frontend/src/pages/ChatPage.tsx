import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import ChatMessages from '../components/ChatMessages'
import ChatInput from '../components/ChatInput'
import WelcomeScreen from '../components/WelcomeScreen'
import client from '../services/client'

interface Message {
    role: 'user' | 'assistant'
    content: string
    created_at: string
}

function ChatPage() {
    const navigate = useNavigate()
    const [messages, setMessages] = useState<Message[]>([])
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState<string | null>(null)
    const [refreshTrigger, setRefreshTrigger] = useState(0)

    const handleNewChat = () => {
        setMessages([])
        setSessionId(null)
        setRefreshTrigger(prev => prev + 1)
    }

    // Redirect αν δεν είναι logged in
    useEffect(() => {
        const token = localStorage.getItem('token')
        if (!token) navigate('/login')
    }, [])

    // Δημιούργησε νέο chat session
    const createSession = async (): Promise<string> => {
        const response = await client.post('/chat/session', {
            title: 'New chat'
        })
        setRefreshTrigger(prev => prev + 1)
        return response.data.id
    }



    const handleSend = async (message: string) => {
        setLoading(true)

        // Πρόσθεσε user message αμέσως
        const userMessage: Message = {
            role: 'user',
            content: message,
            created_at: new Date().toISOString()
        }
        setMessages(prev => [...prev, userMessage])

        try {
            // Δημιούργησε session αν δεν υπάρχει
            let currentSessionId = sessionId
            if (!currentSessionId) {
                currentSessionId = await createSession()
                setSessionId(currentSessionId)
            }

            // Στείλε μήνυμα στον agent
            const response = await client.post(
                `/chat/session/${currentSessionId}/send_message`,
                { content: message }
            )

            // Πρόσθεσε agent response
            const agentMessage: Message = {
                role: 'assistant',
                content: response.data.content,
                created_at: response.data.created_at
            }
            setMessages(prev => [...prev, agentMessage])

        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, something went wrong. Please try again.',
                created_at: new Date().toISOString()
            }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
            <Sidebar
                onNewChat={handleNewChat}
                currentSessionId={sessionId}
                onSelectChat={(id) => setSessionId(id)}
                refreshTrigger={refreshTrigger}
            />

            <div style={{
                flex: 1, display: 'flex', flexDirection: 'column',
                background: 'white', overflow: 'hidden'
            }}>
                {messages.length === 0
                    ? <WelcomeScreen onSuggestion={handleSend} />
                    : <ChatMessages messages={messages} loading={loading} />
                }
                <ChatInput onSend={handleSend} loading={loading} />
            </div>
        </div>
    )
}

export default ChatPage