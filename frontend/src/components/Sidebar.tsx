import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

interface SidebarProps {
    onNewChat: () => void
}

function Sidebar({ onNewChat }: SidebarProps) {
    const navigate = useNavigate()
    const [search, setSearch] = useState('')

    return (
        <div style={{
            width: '240px',
            background: 'var(--surface-1, #f8f8ff)',
            borderRight: '0.5px solid #e0e0e0',
            display: 'flex',
            flexDirection: 'column',
            flexShrink: 0,
            height: '100vh'
        }}>
            {/* Logo */}
            <div style={{ padding: '16px 12px 8px' }}>
                <div
                    onClick={() => navigate('/')}
                    style={{ fontSize: '14px', fontWeight: 500, color: '#7F77DD', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '12px', cursor: 'pointer' }}
                >
                     AventraAI
                </div>

                {/* New Chat Button */}
                <button
                    onClick={onNewChat}
                    style={{
                        width: '100%', padding: '8px 12px', border: '0.5px solid #e0e0e0',
                        borderRadius: '8px', background: 'transparent', cursor: 'pointer',
                        fontSize: '13px', color: '#6c757d', display: 'flex', alignItems: 'center', gap: '8px'
                    }}
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
                    style={{
                        width: '100%', padding: '6px 10px', border: '0.5px solid #e0e0e0',
                        borderRadius: '8px', background: 'white', fontSize: '13px',
                        boxSizing: 'border-box' as const, outline: 'none'
                    }}
                />
            </div>

            {/* Pinned */}
            <div style={{ padding: '4px 12px' }}>
                <div style={{ fontSize: '11px', color: '#aaa', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
                    Pinned
                </div>
                {['Prague September trip', 'Tokyo winter plan'].map((chat, i) => (
                    <div key={i} style={{
                        padding: '8px 10px', borderRadius: '8px', cursor: 'pointer',
                        fontSize: '13px', color: '#534AB7', display: 'flex',
                        alignItems: 'center', gap: '8px', marginBottom: '2px',
                        background: i === 0 ? '#EEEDFE' : 'transparent'
                    }}>
                        <div style={{ width: '6px', height: '6px', background: '#7F77DD', borderRadius: '50%', flexShrink: 0 }} />
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{chat}</span>
                    </div>
                ))}
            </div>

            <div style={{ height: '0.5px', background: '#e0e0e0', margin: '4px 12px' }} />

            {/* Recent Chats */}
            <div style={{ padding: '4px 12px', flex: 1, overflowY: 'auto' as const }}>
                <div style={{ fontSize: '11px', color: '#aaa', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
                    Recent
                </div>
                {['Rome weekend getaway', 'Barcelona food tour', 'Paris honeymoon ideas', 'Budget trip to Lisbon'].map((chat, i) => (
                    <div key={i} style={{
                        padding: '8px 10px', borderRadius: '8px', cursor: 'pointer',
                        fontSize: '13px', color: '#6c757d', display: 'flex',
                        alignItems: 'center', gap: '8px', marginBottom: '2px'
                    }}>
                        💬
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{chat}</span>
                    </div>
                ))}
            </div>

            {/* Profile */}
            <div style={{ padding: '12px', borderTop: '0.5px solid #e0e0e0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px', borderRadius: '8px', cursor: 'pointer' }}>
                    <div style={{
                        width: '32px', height: '32px', borderRadius: '50%', background: '#EEEDFE',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '13px', fontWeight: 500, color: '#534AB7', flexShrink: 0
                    }}>
                        MG
                    </div>
                    <div style={{ flex: 1, overflow: 'hidden' }}>
                        <div style={{ fontSize: '13px', fontWeight: 500, color: '#26215C', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>Mario G.</div>
                        <div style={{ fontSize: '11px', color: '#aaa' }}>Free plan · 2/3 searches</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Sidebar