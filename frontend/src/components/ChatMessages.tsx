interface Message {
    role: 'user' | 'assistant'
    content: string
    created_at: string
}

interface ChatMessagesProps {
    messages: Message[]
    loading: boolean
}

function ChatMessages({ messages, loading }: ChatMessagesProps) {
    return (
        <div style={{
            flex: 1, overflowY: 'auto' as const,
            padding: '24px 48px',
            display: 'flex', flexDirection: 'column', gap: '20px'
        }}>
            {messages.map((msg, i) => (
                <div
                    key={i}
                    style={{
                        display: 'flex', gap: '12px',
                        maxWidth: '80%',
                        alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
                    }}
                >
                    {/* Avatar */}
                    <div style={{
                        width: '28px', height: '28px', borderRadius: '50%',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '12px', flexShrink: 0,
                        background: msg.role === 'user' ? '#534AB7' : '#EEEDFE',
                        color: msg.role === 'user' ? 'white' : '#534AB7'
                    }}>
                        {msg.role === 'user' ? 'U' : '✈️'}
                    </div>

                    {/* Bubble */}
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
                </div>
            ))}

            {/* Loading indicator */}
            {loading && (
                <div style={{ display: 'flex', gap: '12px', alignSelf: 'flex-start' }}>
                    <div style={{
                        width: '28px', height: '28px', borderRadius: '50%',
                        background: '#EEEDFE', display: 'flex',
                        alignItems: 'center', justifyContent: 'center', fontSize: '12px'
                    }}>
                        ✈️
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
        </div>
    )
}

export default ChatMessages