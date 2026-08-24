import { useState } from "react"

interface ChatInputProps {
    onSend: (message: string) => void
    loading: boolean
    isStreaming?: boolean
    onStop?: () => void
}

function ChatInput({ onSend, loading, isStreaming, onStop }: ChatInputProps) {
    const [message, setMessage] = useState('')

    const handleSend = () => {
        if (!message.trim() || loading) return
        onSend(message)
        setMessage('')
    }

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div style={{ padding: '6px 0 12px', background: 'white', display: 'flex', justifyContent: 'center' }}>
            <div style={{ width: '100%', maxWidth: '680px', padding: '0 16px' }}>
                <div style={{
                    display: 'flex', alignItems: 'center', gap: '8px',
                    background: '#f8f8ff', border: '1px solid #e8e6f0',
                    borderRadius: '24px', padding: '3px 3px 3px 16px'
                }}>
                    <textarea
                        rows={1}
                        placeholder="Ask me anything about your trip..."
                        value={message}
                        onChange={e => setMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={loading}
                        style={{
                            flex: 1, border: 'none', background: 'transparent',
                            fontSize: '14px', resize: 'none', outline: 'none',
                            maxHeight: '120px', lineHeight: '1.5', fontFamily: 'inherit',
                            padding: '2px 0', margin: 0
                        }}
                    />
                    <button
                        onClick={isStreaming ? onStop : handleSend}
                        disabled={!isStreaming && (!message.trim() || loading)}
                        aria-label={isStreaming ? 'Stop generating' : 'Send message'}
                        style={{
                            width: '32px', height: '32px', borderRadius: '50%',
                            background: isStreaming ? '#6c757d'
                                : message.trim() && !loading ? '#7F77DD' : '#e0e0e0',
                            border: 'none', cursor: isStreaming || message.trim() ? 'pointer' : 'default',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            flexShrink: 0, transition: 'background 0.2s'
                        }}
                    >
                        <span style={{ color: 'white', fontSize: isStreaming ? '12px' : '16px' }}>
                            {isStreaming ? '■' : '↑'}
                        </span>
                    </button>
                </div>
            </div>
        </div>
    )
}

export default ChatInput