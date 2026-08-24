import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
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
    const [streamingText, setStreamingText] = useState<string | null>(null)
    const streamRef = useRef<ReturnType<typeof setInterval> | null>(null)

    useEffect(() => () => {
        if (streamRef.current) clearInterval(streamRef.current)
    }, [])

    const handleNewChat = () => {
        if (streamRef.current) { clearInterval(streamRef.current); streamRef.current = null }
        setStreamingText(null)
        setMessages([])
        setSessionId(null)
        setRefreshTrigger(prev => prev + 1)
    }

    // Redirect αν δεν είναι logged in
    useEffect(() => {
        const token = localStorage.getItem('token')
        if (!token) navigate('/login')
    }, [])

    // Intercept browser back button with logout confirmation
    useEffect(() => {
        window.history.pushState(null, '', '/chat')
        const handlePopState = () => {
            if (window.confirm('Are you sure you want to log out?')) {
                localStorage.removeItem('token')
                window.location.href = '/'
            } else {
                window.history.pushState(null, '', '/chat')
            }
        }
        window.addEventListener('popstate', handlePopState)
        return () => window.removeEventListener('popstate', handlePopState)
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
            let currentSessionId = sessionId
            if (!currentSessionId) {
                currentSessionId = await createSession()
                setSessionId(currentSessionId)
            }

            const response = await client.post(
                `/chat/session/${currentSessionId}/send_message`,
                { content: message }
            )

            const fullContent = response.data.content
            const createdAt = response.data.created_at
            setLoading(false)

            // Typewriter streaming effect
            let i = 0
            setStreamingText('')
            streamRef.current = setInterval(() => {
                i = Math.min(i + 1, fullContent.length)
                setStreamingText(fullContent.slice(0, i))
                if (i >= fullContent.length) {
                    clearInterval(streamRef.current!)
                    streamRef.current = null
                    setStreamingText(null)
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: fullContent,
                        created_at: createdAt
                    }])
                }
            }, 18)

            // Auto-generate title after the first message
            if (!sessionId) {
                client.post(`/chat/session/${currentSessionId}/generate_title`)
                    .then(() => setRefreshTrigger(prev => prev + 1))
                    .catch(() => {})
            }

        } catch (err) {
            setLoading(false)
            const backendMessage = axios.isAxiosError(err)
                ? (err.response?.data?.detail ?? err.response?.data?.message)
                : null

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: typeof backendMessage === 'string' && backendMessage.trim().length > 0
                    ? backendMessage
                    : 'Sorry, something went wrong. Please try again.',
                created_at: new Date().toISOString()
            }])
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
                {messages.length === 0 && streamingText === null
                    ? <WelcomeScreen onSuggestion={handleSend} />
                    : <ChatMessages messages={messages} loading={loading} streamingText={streamingText} />
                }
                <ChatInput onSend={handleSend} loading={loading || streamingText !== null} />
            </div>
        </div>
    )
}

export default ChatPage