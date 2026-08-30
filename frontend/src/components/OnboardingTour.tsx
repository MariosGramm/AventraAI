import { useState } from 'react'

const STEPS = [
    {
        target: 'chat-input-area',
        title: 'Chat with your travel assistant',
        description: 'Ask anything about destinations, restaurants, attractions, or travel tips. Your AI assistant knows about hundreds of cities worldwide.',
        position: 'top' as const,
    },
    {
        target: 'search-toggle-btn',
        title: 'Generate travel itineraries',
        description: 'Tap the plane icon to create a detailed day-by-day travel package with flights, hotels, activities, and cost estimates.',
        position: 'top' as const,
    },
    {
        target: 'sidebar-area',
        title: 'Your conversations',
        description: 'All your chats are saved here. Pin your favorites and pick up where you left off anytime.',
        position: 'right' as const,
    },
]

interface OnboardingTourProps {
    onComplete: () => void
}

function OnboardingTour({ onComplete }: OnboardingTourProps) {
    const [step, setStep] = useState(0)
    const current = STEPS[step]

    const handleNext = () => {
        if (step < STEPS.length - 1) {
            setStep(step + 1)
        } else {
            onComplete()
        }
    }

    const getTooltipStyle = (): React.CSSProperties => {
        const el = document.getElementById(current.target)
        if (!el) return { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }

        const rect = el.getBoundingClientRect()
        const style: React.CSSProperties = { position: 'fixed', zIndex: 10001 }

        if (current.position === 'top') {
            style.bottom = window.innerHeight - rect.top + 16
            style.left = rect.left + rect.width / 2
            style.transform = 'translateX(-50%)'
        } else if (current.position === 'right') {
            style.top = rect.top + rect.height / 2
            style.left = rect.right + 16
            style.transform = 'translateY(-50%)'
        }

        return style
    }

    const getHighlightStyle = (): React.CSSProperties => {
        const el = document.getElementById(current.target)
        if (!el) return {}

        const rect = el.getBoundingClientRect()
        return {
            position: 'fixed',
            top: rect.top - 6,
            left: rect.left - 6,
            width: rect.width + 12,
            height: rect.height + 12,
            borderRadius: '16px',
            border: '2px solid #7F77DD',
            boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.45)',
            zIndex: 10000,
            pointerEvents: 'none' as const,
            transition: 'all 0.3s ease',
        }
    }

    return (
        <>
            <div style={getHighlightStyle()} />

            <div style={getTooltipStyle()}>
                <div style={{
                    background: 'white',
                    borderRadius: '14px',
                    padding: '20px 24px',
                    maxWidth: '320px',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
                }}>
                    <div style={{
                        fontSize: '10px', color: '#7F77DD', fontWeight: 600,
                        marginBottom: '6px', letterSpacing: '0.5px'
                    }}>
                        STEP {step + 1} OF {STEPS.length}
                    </div>
                    <div style={{
                        fontSize: '15px', fontWeight: 700, color: '#26215C',
                        marginBottom: '6px'
                    }}>
                        {current.title}
                    </div>
                    <div style={{
                        fontSize: '13px', color: '#666', lineHeight: 1.5,
                        marginBottom: '16px'
                    }}>
                        {current.description}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <button
                            onClick={onComplete}
                            style={{
                                background: 'none', border: 'none', color: '#aaa',
                                fontSize: '12px', cursor: 'pointer', padding: '4px 0'
                            }}
                        >
                            Skip tour
                        </button>
                        <button
                            onClick={handleNext}
                            style={{
                                background: '#7F77DD', color: 'white', border: 'none',
                                borderRadius: '10px', padding: '8px 20px', fontSize: '13px',
                                fontWeight: 600, cursor: 'pointer',
                            }}
                        >
                            {step < STEPS.length - 1 ? 'Next' : 'Got it!'}
                        </button>
                    </div>
                </div>
            </div>
        </>
    )
}

export default OnboardingTour
