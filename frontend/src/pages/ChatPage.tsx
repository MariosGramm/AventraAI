import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
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

const GUEST_MAX_MESSAGES = 5

function ChatPage() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const isGuest = searchParams.get('guest') === 'true'

    const [messages, setMessages] = useState<Message[]>([])
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState<string | null>(null)
    const [refreshTrigger, setRefreshTrigger] = useState(0)
    const [streamingText, setStreamingText] = useState<string | null>(null)
    const streamRef = useRef<ReturnType<typeof setInterval> | null>(null)
    const [guestMessagesLeft, setGuestMessagesLeft] = useState(() => {
        const used = parseInt(localStorage.getItem('guest_messages_used') || '0')
        return Math.max(0, GUEST_MAX_MESSAGES - used)
    })

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

    // Redirect if not logged in and not guest
    useEffect(() => {
        const token = localStorage.getItem('token')
        if (!token && !isGuest) navigate('/login')
    }, [])

    // Intercept browser back button with logout confirmation (authenticated only)
    useEffect(() => {
        if (isGuest) return
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
        if (isGuest && guestMessagesLeft <= 0) {
            setMessages(prev => [...prev,
                { role: 'user' as const, content: message, created_at: new Date().toISOString() },
                { role: 'assistant' as const, content: 'You\'ve used all your guest messages. Sign up for free to continue chatting!', created_at: new Date().toISOString() }
            ])
            return
        }

        setLoading(true)

        setMessages(prev => [...prev, {
            role: 'user' as const, content: message, created_at: new Date().toISOString()
        }])

        try {
            let fullContent: string
            let createdAt: string

            if (isGuest) {
                const response = await client.post('/chat/guest/send_message', {
                    content: message,
                    history: messages.map(m => ({ role: m.role, content: m.content }))
                })
                fullContent = response.data.content
                createdAt = response.data.created_at

                const used = parseInt(localStorage.getItem('guest_messages_used') || '0')
                localStorage.setItem('guest_messages_used', String(used + 1))
                setGuestMessagesLeft(GUEST_MAX_MESSAGES - used - 1)
            } else {
                let currentSessionId = sessionId
                let isFirstMessage = false
                if (!currentSessionId) {
                    currentSessionId = await createSession()
                    setSessionId(currentSessionId)
                    isFirstMessage = true
                }

                const response = await client.post(
                    `/chat/session/${currentSessionId}/send_message`,
                    { content: message }
                )
                fullContent = response.data.content
                createdAt = response.data.created_at

                if (isFirstMessage) {
                    client.post(`/chat/session/${currentSessionId}/generate_title`)
                        .then(() => setRefreshTrigger(prev => prev + 1))
                        .catch(() => {})
                }
            }

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
                isGuest={isGuest}
                guestMessagesLeft={guestMessagesLeft}
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