import { useEffect, useRef, useState } from 'react'

interface Message {
    role: 'user' | 'assistant'
    content: string
    created_at: string
}

interface ChatMessagesProps {
    messages: Message[]
    loading: boolean
    streamingText: string | null
    onEdit?: (index: number, newContent: string) => void
    userInitials?: string
}

function ChatMessages({ messages, loading, streamingText, onEdit, userInitials = 'U' }: ChatMessagesProps) {
    const endRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, streamingText])

    return (
        <div style={{
            flex: 1, overflowY: 'auto' as const,
            padding: '24px 16px',
            display: 'flex', flexDirection: 'column',
            alignItems: 'center'
        }}>
            <div style={{
                width: '100%', maxWidth: '680px',
                display: 'flex', flexDirection: 'column', gap: '20px'
            }}>
                {messages.map((msg, i) => (
                    <MessageBubble key={i} msg={msg} index={i} onEdit={onEdit} userInitials={userInitials} />
                ))}

                {/* Streaming response */}
                {streamingText !== null && (
                    <div style={{ display: 'flex', gap: '12px', alignSelf: 'flex-start', maxWidth: '75%' }}>
                        <div style={{
                            width: '28px', height: '28px', borderRadius: '50%',
                            background: '#EEEDFE', display: 'flex',
                            alignItems: 'center', justifyContent: 'center', fontSize: '12px',
                            flexShrink: 0
                        }}>
                            🤖
                        </div>
                        <div style={{
                            padding: '10px 14px', borderRadius: '12px',
                            background: 'white', border: '0.5px solid #e0e0e0',
                            fontSize: '14px', lineHeight: 1.6, color: '#26215C',
                            whiteSpace: 'pre-wrap'
                        }}>
                            {streamingText}
                        </div>
                    </div>
                )}

                {/* Loading indicator */}
                {loading && (
                    <div style={{ display: 'flex', gap: '12px', alignSelf: 'flex-start' }}>
                        <div style={{
                            width: '28px', height: '28px', borderRadius: '50%',
                            background: '#EEEDFE', display: 'flex',
                            alignItems: 'center', justifyContent: 'center', fontSize: '12px'
                        }}>
                            🤖
                        </div>
                        <div style={{
                            padding: '10px 14px', borderRadius: '12px',
                            background: 'white', border: '0.5px solid #e0e0e0',
                            fontSize: '14px', color: '#6c757d'
                        }}>
                            Planning your trip...
                        </div>
                    </div>
                )}
                <div ref={endRef} />
            </div>
        </div>
    )
}

export default ChatMessages

function MessageBubble({ msg, index, onEdit, userInitials }: { msg: Message, index: number, onEdit?: (i: number, text: string) => void, userInitials: string }) {
    const [hovered, setHovered] = useState(false)
    const [editing, setEditing] = useState(false)
    const [editText, setEditText] = useState(msg.content)

    const submitEdit = () => {
        if (editText.trim() && onEdit) {
            onEdit(index, editText.trim())
        }
        setEditing(false)
    }

    const cancelEdit = () => {
        setEditText(msg.content)
        setEditing(false)
    }

    return (
        <div
            style={{
                display: 'flex', gap: '12px',
                maxWidth: '75%',
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                position: 'relative'
            }}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
        >
            <div style={{
                width: '28px', height: '28px', borderRadius: '50%',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '12px', flexShrink: 0,
                background: msg.role === 'user' ? '#534AB7' : '#EEEDFE',
                color: msg.role === 'user' ? 'white' : '#534AB7'
            }}>
                {msg.role === 'user' ? userInitials : '🤖'}
            </div>

            {editing ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
                    <textarea
                        value={editText}
                        onChange={e => setEditText(e.target.value)}
                        autoFocus
                        style={{
                            padding: '10px 14px', borderRadius: '12px',
                            fontSize: '14px', lineHeight: 1.6,
                            border: '1.5px solid #7F77DD', outline: 'none',
                            resize: 'none', fontFamily: 'inherit',
                            minHeight: '40px'
                        }}
                        onKeyDown={e => {
                            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitEdit() }
                            if (e.key === 'Escape') cancelEdit()
                        }}
                    />
                    <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                        <button onClick={cancelEdit} style={{
                            padding: '4px 12px', fontSize: '12px', borderRadius: '6px',
                            border: '0.5px solid #e0e0e0', background: 'white',
                            cursor: 'pointer', color: '#6c757d'
                        }}>Cancel</button>
                        <button onClick={submitEdit} style={{
                            padding: '4px 12px', fontSize: '12px', borderRadius: '6px',
                            border: 'none', background: '#7F77DD', color: 'white',
                            cursor: 'pointer'
                        }}>Send</button>
                    </div>
                </div>
            ) : (
                <div style={{
                    padding: '10px 14px', borderRadius: '12px',
                    fontSize: '14px', lineHeight: 1.6,
                    background: msg.role === 'user' ? '#7F77DD' : 'white',
                    color: msg.role === 'user' ? 'white' : '#26215C',
                    border: msg.role === 'assistant' ? '0.5px solid #e0e0e0' : 'none',
                    whiteSpace: 'pre-wrap'
                }}>
                    {msg.content}
                </div>
            )}

            {msg.role === 'user' && hovered && !editing && onEdit && (
                <button
                    onClick={() => setEditing(true)}
                    title="Edit & resend"
                    style={{
                        position: 'absolute', bottom: '-20px', right: '40px',
                        padding: '2px 8px', fontSize: '11px',
                        background: 'white', border: '0.5px solid #e0e0e0',
                        borderRadius: '4px', cursor: 'pointer', color: '#6c757d',
                        whiteSpace: 'nowrap'
                    }}
                >
                     Edit
                </button>
            )}
        </div>
    )
}