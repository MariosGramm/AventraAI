interface WelcomeScreenProps {
    onSuggestion: (text: string) => void
}

function WelcomeScreen({ onSuggestion }: WelcomeScreenProps) {
    const suggestions = [
        '🏖️ Beach escape',
        '🏙️ City adventure',
        '🏔️ Mountain retreat',
        '🎭 Cultural tour'
    ]

    return (
        <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            justifyContent: 'center', flex: 1, padding: '40px 20px', textAlign: 'center'
        }}>
            <div style={{ fontSize: '36px', marginBottom: '16px' }}>✈️</div>
            <h2 style={{ fontSize: '22px', fontWeight: 500, color: '#26215C', margin: '0 0 8px' }}>
                Where do you want to go?
            </h2>
            <p style={{ fontSize: '14px', color: '#6c757d', margin: '0 0 24px' }}>
                Tell me your dream destination and I'll plan the perfect trip for you.
            </p>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
                {suggestions.map((s, i) => (
                    <button
                        key={i}
                        onClick={() => onSuggestion(s)}
                        style={{
                            padding: '8px 14px', border: '0.5px solid #e0e0e0',
                            borderRadius: '99px', fontSize: '13px', color: '#6c757d',
                            cursor: 'pointer', background: 'white'
                        }}
                    >
                        {s}
                    </button>
                ))}
            </div>
        </div>
    )
}

export default WelcomeScreen