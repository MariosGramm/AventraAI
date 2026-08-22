import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ProgressBar } from 'react-bootstrap'
import { logout } from '../services/authService'

function LoggingOutPage() {
    const navigate = useNavigate()
    const [progress, setProgress] = useState(10)

    useEffect(() => {
        logout()

        const progressTimer = setInterval(() => {
            setProgress((prev) => Math.min(prev + 20, 100))
        }, 150)

        const redirectTimer = setTimeout(() => {
            navigate('/')
        }, 1000)

        return () => {
            clearInterval(progressTimer)
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
                <div style={{ fontSize: '36px', marginBottom: '1rem' }}>👋</div>

                <h1 style={{ fontSize: '18px', fontWeight: 500, color: '#26215C', marginBottom: '1.25rem' }}>
                    Logging out...
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
