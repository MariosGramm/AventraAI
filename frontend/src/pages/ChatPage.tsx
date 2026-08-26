import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Sidebar from '../components/Sidebar'
import ChatMessages from '../components/ChatMessages'
import ChatInput from '../components/ChatInput'
import SearchForm from '../components/SearchForm'
import type { SearchFormData } from '../components/SearchForm'
import WelcomeScreen from '../components/WelcomeScreen'
import client from '../services/client'
import { useAuthContext } from '../context/AuthContext'

interface Message {
    role: 'user' | 'assistant'
    content: string
    created_at: string
}

function ChatPage() {
    const navigate = useNavigate()
    const { user, setUser } = useAuthContext()

    const userInitials = user ? `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase() : 'U'

    const [messages, setMessages] = useState<Message[]>([])
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState<string | null>(null)
    const [refreshTrigger, setRefreshTrigger] = useState(0)
    const [streamingText, setStreamingText] = useState<string | null>(null)
    const streamRef = useRef<ReturnType<typeof setInterval> | null>(null)
    const [showSearchForm, setShowSearchForm] = useState(false)
    const [searchLoading, setSearchLoading] = useState(false)

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

    useEffect(() => {
        const token = localStorage.getItem('token')
        if (!token) navigate('/login', { replace: true })
    }, [])

    const createSession = async (): Promise<string> => {
        const response = await client.post('/chat/session', {
            title: 'New chat'
        })
        setRefreshTrigger(prev => prev + 1)
        return response.data.id
    }



    const stopStreaming = () => {
        if (streamRef.current) {
            clearInterval(streamRef.current)
            streamRef.current = null
        }
        if (streamingText !== null) {
            const partial = streamingText
            setStreamingText(null)
            if (partial) {
                setMessages(prev => [...prev, {
                    role: 'assistant' as const,
                    content: partial,
                    created_at: new Date().toISOString()
                }])
            }
        }
    }

    const handleEdit = (index: number, newContent: string) => {
        if (!newContent.trim()) return
        setMessages(prev => prev.slice(0, index))
        handleSend(newContent)
    }

    const handleSend = async (message: string) => {
        setLoading(true)

        setMessages(prev => [...prev, {
            role: 'user' as const, content: message, created_at: new Date().toISOString()
        }])

        try {
            let fullContent: string
            let createdAt: string

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

            setLoading(false)

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

    const handleSearch = async (data: SearchFormData) => {
        setSearchLoading(true)
        setShowSearchForm(false)

        setMessages(prev => [...prev, {
            role: 'user' as const,
            content: `Generate a travel package for ${data.destination} (${data.date_from.slice(0, 10)} → ${data.date_to.slice(0, 10)}, ${data.adults} adults${data.children ? `, ${data.children} children` : ''}${data.budget ? `, budget: ${data.budget} ${data.currency}` : ''})`,
            created_at: new Date().toISOString()
        }])

        setLoading(true)

        try {
            const response = await client.post('/travel/searches', data)
            setLoading(false)

            const packages = response.data.travel_packages || []
            const searchSessionId = response.data.id

            setMessages(prev => [...prev, {
                role: 'assistant' as const,
                content: `__PACKAGE__${JSON.stringify({ packages, searchSessionId, destination: data.destination, dateFrom: data.date_from, dateTo: data.date_to })}`,
                created_at: new Date().toISOString()
            }])

            client.get('/users/me').then(res => setUser(res.data)).catch(() => {})
        } catch (err) {
            setLoading(false)
            const detail = axios.isAxiosError(err) ? err.response?.data?.detail : null
            setMessages(prev => [...prev, {
                role: 'assistant' as const,
                content: typeof detail === 'string' ? detail : 'Failed to generate travel package. Please try again.',
                created_at: new Date().toISOString()
            }])
        } finally {
            setSearchLoading(false)
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
                {showSearchForm ? (
                    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px', overflow: 'auto' }}>
                        <SearchForm onSubmit={handleSearch} onClose={() => setShowSearchForm(false)} loading={searchLoading} />
                    </div>
                ) : (
                    <>
                        {messages.length === 0 && streamingText === null
                            ? <WelcomeScreen onSuggestion={handleSend} />
                            : <ChatMessages messages={messages} loading={loading} streamingText={streamingText} onEdit={handleEdit} userInitials={userInitials} />
                        }
                    </>
                )}
                <ChatInput onSend={handleSend} loading={loading || streamingText !== null} isStreaming={streamingText !== null} onStop={stopStreaming} onSearchToggle={() => setShowSearchForm(prev => !prev)} />
            </div>
        </div>
    )
}

export default ChatPage