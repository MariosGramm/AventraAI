import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ProgressBar } from 'react-bootstrap'
import { logout } from '../services/authService'

function LoggingOutPage() {
    const navigate = useNavigate()
    const [progress, setProgress] = useState(10)
    const [done, setDone] = useState(false)

    useEffect(() => {
        logout()

        const progressTimer = setInterval(() => {
            setProgress((prev) => Math.min(prev + 10, 100))
        }, 150)

        const doneTimer = setTimeout(() => setDone(true), 1600)
        const redirectTimer = setTimeout(() => navigate('/', { replace: true }), 3000)

        return () => {
            clearInterval(progressTimer)
            clearTimeout(doneTimer)
            clearTimeout(redirectTimer)
        }
    }, [navigate])

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(180deg, #EEEDFE 0%, #d4d0f8 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem'
        }}>
            <div style={{
                background: 'white',
                borderRadius: '16px',
                padding: '2.5rem 2rem',
                width: '100%',
                maxWidth: '360px',
                textAlign: 'center',
                boxShadow: '0 4px 24px rgba(127, 119, 221, 0.15)'
            }}>
                <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'center' }}>
                    {done ? (
                        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#7F77DD" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="12" cy="12" r="10" />
                            <path d="M8 12.5l2.5 2.5L16 9.5" />
                        </svg>
                    ) : (
                        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#7F77DD" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                            <polyline points="16 17 21 12 16 7" />
                            <line x1="21" y1="12" x2="9" y2="12" />
                        </svg>
                    )}
                </div>

                <h1 style={{ fontSize: '18px', fontWeight: 500, color: '#26215C', marginBottom: '1.25rem' }}>
                    {done ? 'You’ve been successfully logged out.' : 'Logging out...'}
                </h1>

                <ProgressBar
                    now={progress}
                    style={{ height: '6px' }}
                    variant="info"
                />
            </div>
        </div>
    )
}

export default LoggingOutPage

