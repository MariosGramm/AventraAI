import {useState} from "react";

interface ChatInputProps {
    onSend: (message: string) => void
    loading: boolean
}

function ChatInput({ onSend, loading }: ChatInputProps) {
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
        <div style={{ padding: '16px 48px 20px', borderTop: '0.5px solid #e0e0e0', background: 'white' }}>
            <div style={{
                display: 'flex', alignItems: 'flex-end', gap: '8px',
                background: 'white', border: '0.5px solid #e0e0e0',
                borderRadius: '12px', padding: '10px 12px'
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
                        maxHeight: '120px', lineHeight: '1.5', fontFamily: 'inherit'
                    }}
                />
                <button
                    onClick={handleSend}
                    disabled={!message.trim() || loading}
                    aria-label="Send message"
                    style={{
                        width: '32px', height: '32px', borderRadius: '8px',
                        background: message.trim() && !loading ? '#7F77DD' : '#e0e0e0',
                        border: 'none', cursor: message.trim() ? 'pointer' : 'default',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0, transition: 'background 0.2s'
                    }}
                >
                    <span style={{ color: 'white', fontSize: '16px' }}>↑</span>
                </button>
            </div>
        </div>
    )
}

export default ChatInput