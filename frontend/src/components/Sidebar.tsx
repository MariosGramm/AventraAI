import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthContext } from '../context/AuthContext'
import client from '../services/client'

interface ChatSession {
    id: string
    title: string
    created_at: string
    pinned?: boolean
}

interface SidebarProps {
    onNewChat: () => void
    currentSessionId: string | null
    onSelectChat: (sessionId: string) => void
    refreshTrigger: number
}

function Sidebar({ onNewChat, currentSessionId, onSelectChat, refreshTrigger }: SidebarProps) {
    const navigate = useNavigate()
    const { user, logout } = useAuthContext()
    const [search, setSearch] = useState('')
    const [sessions, setSessions] = useState<ChatSession[]>([])
    const [pinned, setPinned] = useState<ChatSession[]>([])
    const [contextMenu, setContextMenu] = useState<{ sessionId: string, x: number, y: number } | null>(null)

    // Παίρνεις initials από το όνομα
    const getInitials = () => {
        if (!user) return '?'
        return `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase()
    }

    // Φόρτωσε chat sessions από backend
    const loadSessions = async () => {
        try {
            const response = await client.get('/chat/sessions')
            const allSessions: ChatSession[] = response.data.chat_sessions || []
            setPinned(allSessions.filter(s => s.pinned))
            setSessions(allSessions.filter(s => !s.pinned))
        } catch (err) {
            console.error('Failed to load sessions', err)
        }
    }

    useEffect(() => {
        loadSessions()
    }, [refreshTrigger])

    // Filter by search
    const filtered = sessions.filter(s =>
        s.title.toLowerCase().includes(search.toLowerCase())
    )

    // Context menu actions
    const handlePin = async (sessionId: string) => {
        // TODO: implement pin API call
        setContextMenu(null)
        loadSessions()
    }

    const handleRename = async (sessionId: string) => {
        const newTitle = prompt('Enter new name:')
        if (!newTitle) return
        // TODO: implement rename API call
        setContextMenu(null)
        loadSessions()
    }

    const handleDelete = async (sessionId: string) => {
        // TODO: implement delete API call
        setContextMenu(null)
        loadSessions()
    }

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <div
            style={{ width: '240px', background: '#f8f8ff', borderRight: '0.5px solid #e0e0e0', display: 'flex', flexDirection: 'column', height: '100vh', flexShrink: 0 }}
            onClick={() => setContextMenu(null)}
        >
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
            <div style={{ padding: '8px 12px' }}>
                <input
                    type="text"
                    placeholder="Search chats..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    style={{ width: '100%', padding: '6px 10px', border: '0.5px solid #e0e0e0', borderRadius: '8px', background: 'white', fontSize: '13px', boxSizing: 'border-box' as const, outline: 'none' }}
                />
            </div>

            {/* Pinned */}
            {pinned.length > 0 && (
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
                        />
                    ))}
                </div>
            )}

            {pinned.length > 0 && <div style={{ height: '0.5px', background: '#e0e0e0', margin: '4px 12px' }} />}

            {/* Recent */}
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
                    />
                ))}
            </div>

            {/* Context Menu */}
            {contextMenu && (
                <div style={{
                    position: 'fixed', top: contextMenu.y, left: contextMenu.x,
                    background: 'white', border: '0.5px solid #e0e0e0', borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)', zIndex: 1000, minWidth: '140px'
                }}>
                    {[
                        { label: '✏️ Rename', action: () => handleRename(contextMenu.sessionId) },
                        { label: '📌 Pin', action: () => handlePin(contextMenu.sessionId) },
                        { label: '🗑️ Delete', action: () => handleDelete(contextMenu.sessionId) },
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
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px', borderRadius: '8px', cursor: 'pointer' }}
                     onClick={handleLogout}
                >
                    <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#EEEDFE', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 500, color: '#534AB7', flexShrink: 0 }}>
                        {getInitials()}
                    </div>
                    <div style={{ flex: 1, overflow: 'hidden' }}>
                        <div style={{ fontSize: '13px', fontWeight: 500, color: '#26215C', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {user ? `${user.first_name} ${user.last_name}` : ''}
                        </div>
                        <div style={{ fontSize: '11px', color: '#aaa' }}>
                            {user?.subscription_tier === 'paid' ? 'Pro · Unlimited searches' : 'Free plan'}
                        </div>
                    </div>
                    <span style={{ fontSize: '13px', color: '#aaa' }}>→</span>
                </div>
            </div>
        </div>
    )
}

// ChatItem component
interface ChatItemProps {
    session: ChatSession
    isActive: boolean
    onSelect: () => void
    onContextMenu: (e: React.MouseEvent) => void
    isPinned?: boolean
}

function ChatItem({ session, isActive, onSelect, onContextMenu, isPinned }: ChatItemProps) {
    const [hovered, setHovered] = useState(false)

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
                : <span style={{ fontSize: '13px' }}>💬</span>
            }
            <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {session.title}
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