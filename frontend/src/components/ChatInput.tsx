import { useState } from "react"
import { useSpeechRecognition } from "../hooks/useSpeechRecognition"

interface ChatInputProps {
    onSend: (message: string) => void
    loading: boolean
    isStreaming?: boolean
    onStop?: () => void
    onSearchToggle?: () => void
}

function ChatInput({ onSend, loading, isStreaming, onStop, onSearchToggle }: ChatInputProps) {
    const [message, setMessage] = useState('')

    const { isRecording, isSupported, toggleRecording } = useSpeechRecognition(
        (text) => setMessage(prev => prev.trim() ? `${prev.trim()} ${text}` : text)
    )

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
                    borderRadius: '24px', padding: '3px 3px 3px 6px'
                }}>
                    {onSearchToggle && (
                        <button
                            type="button"
                            onClick={onSearchToggle}
                            disabled={loading}
                            title="Generate travel package"
                            style={{
                                width: '32px', height: '32px', borderRadius: '50%',
                                background: 'transparent', border: 'none', cursor: 'pointer',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                flexShrink: 0, transition: 'background 0.2s'
                            }}
                            onMouseEnter={e => e.currentTarget.style.background = '#EEEDFE'}
                            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#7F77DD" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
                            </svg>
                        </button>
                    )}
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
                    {isSupported && (
                        <button
                            type="button"
                            onClick={toggleRecording}
                            disabled={loading}
                            aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
                            title={isRecording ? 'Stop recording' : 'Start voice input'}
                            style={{
                                width: '32px', height: '32px', borderRadius: '50%',
                                background: isRecording ? '#ff4d4f' : 'transparent',
                                border: 'none', cursor: 'pointer',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                flexShrink: 0, transition: 'background 0.2s'
                            }}
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                                stroke={isRecording ? 'white' : '#6c757d'} strokeWidth="1.5"
                                strokeLinecap="round" strokeLinejoin="round">
                                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                                <line x1="12" y1="19" x2="12" y2="23" />
                                <line x1="8" y1="23" x2="16" y2="23" />
                            </svg>
                        </button>
                    )}
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