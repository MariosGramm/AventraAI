import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import Sidebar from '../components/Sidebar'
import ChatMessages from '../components/ChatMessages'
import ChatInput from '../components/ChatInput'
import SearchForm from '../components/SearchForm'
import type { SearchFormData } from '../components/SearchForm'
import WelcomeScreen from '../components/WelcomeScreen'
import OnboardingTour from '../components/OnboardingTour'
import client from '../services/client'
import { useAuthContext } from '../context/AuthContext'
import { useIsMobile } from '../hooks/useIsMobile'

interface Message {
    role: 'user' | 'assistant'
    content: string
    created_at: string
}

function ChatPage() {
    const navigate = useNavigate()
    const { user, setUser } = useAuthContext()
    const isMobile = useIsMobile()
    const [sidebarOpen, setSidebarOpen] = useState(false)

    const userInitials = user ? `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase() : 'U'

    const [messages, setMessages] = useState<Message[]>([])
    const [loading, setLoading] = useState(false)
    const [sessionId, setSessionId] = useState<string | null>(null)
    const [refreshTrigger, setRefreshTrigger] = useState(0)
    const [streamingText, setStreamingText] = useState<string | null>(null)
    const streamRef = useRef<ReturnType<typeof setInterval> | null>(null)
    const abortRef = useRef<AbortController | null>(null)
    const [showSearchForm, setShowSearchForm] = useState(false)
    const [searchLoading, setSearchLoading] = useState(false)
    const [showTour, setShowTour] = useState(false)

    useEffect(() => {
        if (user && !user.has_seen_onboarding) {
            const timer = setTimeout(() => setShowTour(true), 1500)
            return () => clearTimeout(timer)
        }
    }, [user])

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

    const skipNextFetch = useRef(false)

    useEffect(() => {
        if (!sessionId) return
        if (skipNextFetch.current) {
            skipNextFetch.current = false
            return
        }
        client.get(`/chat/session/${sessionId}/messages`)
            .then(res => {
                const msgs = (res.data.data || []).reverse()
                setMessages(msgs.map((m: any) => ({ role: m.role, content: m.content, created_at: m.created_at })))
            })
            .catch(() => {})
    }, [sessionId])

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
        if (abortRef.current) abortRef.current.abort()
        if (streamRef.current) { clearInterval(streamRef.current); streamRef.current = null }
        setStreamingText(null)
        setLoading(false)
        setMessages(prev => prev.slice(0, index))
        handleSend(newContent)
    }

    const handleSend = async (message: string) => {
        setLoading(true)
        const controller = new AbortController()
        abortRef.current = controller

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
                skipNextFetch.current = true
                setSessionId(currentSessionId)
                isFirstMessage = true
            }

            const response = await client.post(
                `/chat/session/${currentSessionId}/send_message`,
                { content: message },
                { signal: controller.signal }
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

        const userContent = `Generate a travel package for ${data.destination} (${data.date_from.slice(0, 10)} → ${data.date_to.slice(0, 10)}, ${data.adults} adults${data.children ? `, ${data.children} children` : ''}${data.budget ? `, budget: ${data.budget} ${data.currency}` : ''})`

        setMessages(prev => [...prev, {
            role: 'user' as const,
            content: userContent,
            created_at: new Date().toISOString()
        }])

        setLoading(true)

        try {
            let currentSessionId = sessionId
            if (!currentSessionId) {
                currentSessionId = await createSession()
                skipNextFetch.current = true
                setSessionId(currentSessionId)
            }

            await client.post(`/chat/session/${currentSessionId}/save_message`, { role: 'user', content: userContent })

            const response = await client.post('/travel/searches', data)
            setLoading(false)

            const packages = response.data.travel_packages || []
            const searchSessionId = response.data.id
            const packageContent = `__PACKAGE__${JSON.stringify({ packages, searchSessionId, destination: data.destination, dateFrom: data.date_from, dateTo: data.date_to })}`

            setMessages(prev => [...prev, {
                role: 'assistant' as const,
                content: packageContent,
                created_at: new Date().toISOString()
            }])

            await client.post(`/chat/session/${currentSessionId}/save_message`, { role: 'assistant', content: packageContent })

            if (!sessionId) {
                client.post(`/chat/session/${currentSessionId}/generate_title`)
                    .then(() => setRefreshTrigger(prev => prev + 1))
                    .catch(() => {})
            }

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
            {/* Mobile sidebar overlay */}
            {isMobile && sidebarOpen && (
                <div
                    onClick={() => setSidebarOpen(false)}
                    style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', zIndex: 998 }}
                />
            )}

            <div style={{
                ...(isMobile ? {
                    position: 'fixed', left: sidebarOpen ? 0 : -260, top: 0, bottom: 0,
                    zIndex: 999, transition: 'left 0.25s ease',
                } : {}),
            }}>
                <Sidebar
                    onNewChat={() => { handleNewChat(); if (isMobile) setSidebarOpen(false) }}
                    currentSessionId={sessionId}
                    onSelectChat={(id) => { setSessionId(id); if (isMobile) setSidebarOpen(false) }}
                    refreshTrigger={refreshTrigger}
                />
            </div>

            <div style={{
                flex: 1, display: 'flex', flexDirection: 'column',
                background: 'white', overflow: 'hidden', minWidth: 0,
            }}>
                {/* Mobile hamburger */}
                {isMobile && (
                    <div style={{ padding: '8px 12px', borderBottom: '0.5px solid #e8e6f0', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <button
                            onClick={() => setSidebarOpen(true)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '4px', display: 'flex' }}
                        >
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#7F77DD" strokeWidth="2" strokeLinecap="round">
                                <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
                            </svg>
                        </button>
                        <span style={{ fontSize: '14px', fontWeight: 500, color: '#7F77DD' }}>AventraAI</span>
                    </div>
                )}
                {showSearchForm ? (
                    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px', overflow: 'auto' }}>
                        <SearchForm onSubmit={handleSearch} onClose={() => setShowSearchForm(false)} loading={searchLoading} />
                    </div>
                ) : (
                    <>
                        {messages.length === 0 && streamingText === null && !loading
                            ? <WelcomeScreen onSuggestion={handleSend} />
                            : <ChatMessages messages={messages} loading={loading} streamingText={streamingText} onEdit={handleEdit} userInitials={userInitials} />
                        }
                    </>
                )}
                <ChatInput onSend={handleSend} loading={loading || streamingText !== null} isStreaming={streamingText !== null} onStop={stopStreaming} onSearchToggle={() => setShowSearchForm(prev => !prev)} />
            </div>

            {showTour && (
                <OnboardingTour onComplete={() => {
                    setShowTour(false)
                    client.post('/users/me/onboarding-complete').catch(() => {})
                }} />
            )}
        </div>
    )
}

export default ChatPage