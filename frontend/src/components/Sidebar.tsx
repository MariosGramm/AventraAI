import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthContext } from '../context/AuthContext'
import client from '../services/client'

interface ChatSession {
    id: string
    title: string
    created_at: string
    is_pinned: boolean
}

interface SidebarProps {
    onNewChat: () => void
    currentSessionId: string | null
    onSelectChat: (sessionId: string) => void
    refreshTrigger: number
    isGuest?: boolean
    guestMessagesLeft?: number
}

const MAX_PINNED = 3

function Sidebar({ onNewChat, currentSessionId, onSelectChat, refreshTrigger, isGuest, guestMessagesLeft }: SidebarProps) {
    const navigate = useNavigate()
    const { user } = useAuthContext()
    const [search, setSearch] = useState('')
    const [sessions, setSessions] = useState<ChatSession[]>([])
    const [pinned, setPinned] = useState<ChatSession[]>([])
    const [contextMenu, setContextMenu] = useState<{ sessionId: string, x: number, y: number } | null>(null)

    const getInitials = () => {
        if (!user) return '?'
        return `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase()
    }

    const loadSessions = async () => {
        try {
            const response = await client.get('/chat/sessions')
            const allSessions: ChatSession[] = response.data.chat_sessions || []
            setPinned(allSessions.filter(s => s.is_pinned))
            setSessions(allSessions.filter(s => !s.is_pinned))
        } catch (err) {
            console.error('Failed to load sessions', err)
        }
    }

    useEffect(() => {
        if (!isGuest) loadSessions()
    }, [refreshTrigger])

    const filtered = sessions.filter(s =>
        s.title.toLowerCase().includes(search.toLowerCase())
    )

    const [pinError, setPinError] = useState<string | null>(null)

    const handlePin = async (sessionId: string) => {
        const isPinned = pinned.some(s => s.id === sessionId)
        if (!isPinned && pinned.length >= MAX_PINNED) {
            setPinError(`You can pin up to ${MAX_PINNED} chats.`)
            setTimeout(() => setPinError(null), 3000)
            setContextMenu(null)
            return
        }
        try {
            await client.patch(`/chat/session/${sessionId}/pin`)
            setContextMenu(null)
            loadSessions()
        } catch (err) {
            console.error('Failed to pin session', err)
        }
    }

    const [renaming, setRenaming] = useState<{ sessionId: string, title: string } | null>(null)

    const handleRename = (sessionId: string) => {
        const session = [...pinned, ...sessions].find(s => s.id === sessionId)
        setRenaming({ sessionId, title: session?.title || '' })
        setContextMenu(null)
    }

    const submitRename = async () => {
        if (!renaming || !renaming.title.trim()) { setRenaming(null); return }
        try {
            await client.patch(`/chat/session/${renaming.sessionId}/rename`, { title: renaming.title.trim() })
            loadSessions()
        } catch (err) {
            console.error('Failed to rename session', err)
        }
        setRenaming(null)
    }

    const handleDelete = async (_sessionId: string) => {
        setContextMenu(null)
        loadSessions()
    }


    return (
        <div
            style={{ width: '240px', background: '#f8f8ff', borderRight: '0.5px solid #e0e0e0', display: 'flex', flexDirection: 'column', height: '100vh', flexShrink: 0, position: 'relative' }}
            onClick={() => setContextMenu(null)}
        >
            {/* Pin limit toast */}
            {pinError && (
                <div style={{
                    position: 'absolute', top: '12px', left: '12px', right: '12px',
                    background: '#fff0f0', border: '0.5px solid #ffcccc', borderRadius: '8px',
                    padding: '8px 12px', fontSize: '12px', color: '#cc0000',
                    zIndex: 1001, textAlign: 'center'
                }}>
                    {pinError}
                </div>
            )}

            {/* Logo */}
            <div style={{ padding: '16px 12px 8px' }}>
                <div
                    onClick={() => navigate('/')}
                    style={{ fontSize: '14px', fontWeight: 500, color: '#7F77DD', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px', cursor: 'pointer' }}
                >
                    ✈️ AventraAI
                </div>

                <button
                    onClick={onNewChat}
                    style={{ width: '100%', padding: '8px 12px', border: '0.5px solid #e0e0e0', borderRadius: '8px', background: 'transparent', cursor: 'pointer', fontSize: '13px', color: '#6c757d', display: 'flex', alignItems: 'center', gap: '8px' }}
                >
                    + New chat
                </button>
            </div>

            {/* Search */}
            {!isGuest && (
            <div style={{ padding: '8px 12px' }}>
                <input
                    type="text"
                    placeholder="Search chats..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    style={{ width: '100%', padding: '6px 10px', border: '0.5px solid #e0e0e0', borderRadius: '8px', background: 'white', fontSize: '13px', boxSizing: 'border-box' as const, outline: 'none' }}
                />
            </div>
            )}

            {/* Pinned */}
            {!isGuest && pinned.length > 0 && (
                <div style={{ padding: '4px 12px' }}>
                    <div style={{ fontSize: '11px', color: '#aaa', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Pinned</div>
                    {pinned.map(session => (
                        <ChatItem
                            key={session.id}
                            session={session}
                            isActive={currentSessionId === session.id}
                            onSelect={() => onSelectChat(session.id)}
                            onContextMenu={(e) => {
                                e.stopPropagation()
                                setContextMenu({ sessionId: session.id, x: e.clientX, y: e.clientY })
                            }}
                            isPinned
                            renaming={renaming}
                            onRenameChange={t => setRenaming(prev => prev ? { ...prev, title: t } : null)}
                            onRenameSubmit={submitRename}
                            onRenameCancel={() => setRenaming(null)}
                        />
                    ))}
                </div>
            )}

            {!isGuest && pinned.length > 0 && <div style={{ height: '0.5px', background: '#e0e0e0', margin: '4px 12px' }} />}

            {/* Recent */}
            {!isGuest ? (
            <div style={{ padding: '4px 12px', flex: 1, overflowY: 'auto' as const }}>
                <div style={{ fontSize: '11px', color: '#aaa', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Recent</div>
                {filtered.map(session => (
                    <ChatItem
                        key={session.id}
                        session={session}
                        isActive={currentSessionId === session.id}
                        onSelect={() => onSelectChat(session.id)}
                        onContextMenu={(e) => {
                            e.stopPropagation()
                            setContextMenu({ sessionId: session.id, x: e.clientX, y: e.clientY })
                        }}
                        renaming={renaming}
                        onRenameChange={t => setRenaming(prev => prev ? { ...prev, title: t } : null)}
                        onRenameSubmit={submitRename}
                        onRenameCancel={() => setRenaming(null)}
                    />
                ))}
            </div>
            ) : (
                <div style={{ padding: '16px 12px', flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#aaa', fontSize: '13px', textAlign: 'center' }}>
                    <div style={{ fontSize: '24px', marginBottom: '8px' }}>💬</div>
                    Sign up to save your chats
                </div>
            )}

            {/* Context Menu */}
            {contextMenu && (
                <div style={{
                    position: 'fixed', top: contextMenu.y, left: contextMenu.x,
                    background: 'white', border: '0.5px solid #e0e0e0', borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)', zIndex: 1000, minWidth: '140px'
                }}>
                    {[
                        { label: 'Rename', action: () => handleRename(contextMenu.sessionId) },
                        {
                            label: pinned.some(s => s.id === contextMenu.sessionId) ? 'Unpin' : 'Pin',
                            action: () => handlePin(contextMenu.sessionId)
                        },
                        { label: 'Delete', action: () => handleDelete(contextMenu.sessionId) },
                    ].map((item, i) => (
                        <div
                            key={i}
                            onClick={item.action}
                            style={{ padding: '8px 14px', fontSize: '13px', cursor: 'pointer', color: i === 2 ? '#cc0000' : '#26215C' }}
                        >
                            {item.label}
                        </div>
                    ))}
                </div>
            )}

            {/* Profile */}
            <div style={{ padding: '12px', borderTop: '0.5px solid #e0e0e0' }}>
                {isGuest ? (
                    <>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px' }}>
                            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#EEEDFE', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', flexShrink: 0 }}>
                                👤
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontSize: '13px', fontWeight: 500, color: '#26215C' }}>Guest</div>
                                <div style={{ fontSize: '11px', color: '#aaa' }}>
                                    {guestMessagesLeft} messages left
                                </div>
                            </div>
                        </div>
                        <button
                            onClick={() => navigate('/register')}
                            style={{ width: '100%', marginTop: '4px', padding: '8px', background: '#7F77DD', color: 'white', border: 'none', borderRadius: '8px', fontSize: '13px', cursor: 'pointer' }}
                        >
                            Sign up for free →
                        </button>
                    </>
                ) : (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px', borderRadius: '8px', cursor: 'pointer' }}
                     onClick={() => navigate('/profile')}
                >
                    <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#EEEDFE', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 500, color: '#534AB7', flexShrink: 0 }}>
                        {getInitials()}
                    </div>
                    <div style={{ flex: 1, overflow: 'hidden' }}>
                        <div style={{ fontSize: '13px', fontWeight: 500, color: '#26215C', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {user ? `${user.first_name} ${user.last_name}` : ''}
                        </div>
                        <div style={{ fontSize: '11px', color: '#aaa' }}>
                            {user?.subscription_tier === 'paid'
                                ? 'Pro'
                                : `Free tier · ${Math.max(0, 3 - (user?.monthly_searches_used || 0))}/3 searches left`}
                        </div>
                    </div>
                    <span style={{ fontSize: '13px', color: '#aaa' }}>→</span>
                </div>
                )}
            </div>
        </div>
    )
}

interface ChatItemProps {
    session: ChatSession
    isActive: boolean
    onSelect: () => void
    onContextMenu: (e: React.MouseEvent) => void
    isPinned?: boolean
    renaming?: { sessionId: string, title: string } | null
    onRenameChange?: (title: string) => void
    onRenameSubmit?: () => void
    onRenameCancel?: () => void
}

function ChatItem({ session, isActive, onSelect, onContextMenu, isPinned, renaming, onRenameChange, onRenameSubmit, onRenameCancel }: ChatItemProps) {
    const [hovered, setHovered] = useState(false)
    const [displayTitle, setDisplayTitle] = useState(session.title)
    const prevTitleRef = useRef(session.title)

    useEffect(() => {
        if (prevTitleRef.current === 'New chat' && session.title !== 'New chat') {
            let i = 0
            const full = session.title
            setDisplayTitle('')
            const interval = setInterval(() => {
                i = Math.min(i + 1, full.length)
                setDisplayTitle(full.slice(0, i))
                if (i >= full.length) clearInterval(interval)
            }, 45)
            prevTitleRef.current = session.title
            return () => clearInterval(interval)
        }
        setDisplayTitle(session.title)
        prevTitleRef.current = session.title
    }, [session.title])

    return (
        <div
            onClick={onSelect}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
            style={{
                padding: '8px 10px', borderRadius: '8px', cursor: 'pointer',
                fontSize: '13px', display: 'flex', alignItems: 'center',
                gap: '8px', marginBottom: '2px',
                background: isActive ? '#EEEDFE' : hovered ? '#f0f0f8' : 'transparent',
                color: isActive ? '#534AB7' : '#6c757d'
            }}
        >
            {isPinned
                ? <div style={{ width: '6px', height: '6px', background: '#7F77DD', borderRadius: '50%', flexShrink: 0 }} />
                : <span style={{ fontSize: '13px', color: '#aaa' }}></span>
            }
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {renaming?.sessionId === session.id ? (
                    <input
                        autoFocus
                        value={renaming.title}
                        onChange={e => onRenameChange?.(e.target.value)}
                        onKeyDown={e => {
                            if (e.key === 'Enter') onRenameSubmit?.()
                            if (e.key === 'Escape') onRenameCancel?.()
                        }}
                        onBlur={() => onRenameSubmit?.()}
                        onClick={e => e.stopPropagation()}
                        style={{
                            width: '100%', border: 'none', outline: 'none',
                            background: 'transparent', fontSize: '13px',
                            color: '#26215C', fontFamily: 'inherit', padding: 0
                        }}
                    />
                ) : displayTitle}
            </span>
            {hovered && (
                <span
                    onClick={onContextMenu}
                    style={{ fontSize: '16px', color: '#aaa', padding: '0 2px', lineHeight: 1 }}
                >
                    ···
                </span>
            )}
        </div>
    )
}

export default Sidebar