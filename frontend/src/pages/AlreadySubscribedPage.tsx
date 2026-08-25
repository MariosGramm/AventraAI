import { useEffect, useState } from 'react'
import client from '../services/client'
import StartPlanningButton from '../components/StartPlanningButton.tsx'

interface CurrentUser {
    first_name: string
    last_name: string
    email: string
}

function AlreadySubscribedPage() {
    const [user, setUser] = useState<CurrentUser | null>(null)

    useEffect(() => {
        client.get('/users/me')
            .then((response) => setUser(response.data))
            .catch(() => setUser(null))
    }, [])

    const accountLabel = user ? `${user.first_name} ${user.last_name} (${user.email})` : 'Your account'

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
                padding: '3rem 2rem',
                width: '100%',
                maxWidth: '420px',
                textAlign: 'center',
                boxShadow: '0 4px 24px rgba(127, 119, 221, 0.15)'
            }}>
                <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'center' }}>
                    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#7F77DD" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10" />
                        <path d="M8 12.5l2.5 2.5L16 9.5" />
                    </svg>
                </div>

                <h1 style={{ fontSize: '24px', fontWeight: 500, color: '#26215C', marginBottom: '0.5rem' }}>
                    You're already on Pro
                </h1>

                <p style={{ color: '#6c757d', lineHeight: 1.8, marginBottom: '2rem' }}>
                    Account <strong>{accountLabel}</strong> is already on the Pro plan.
                </p>

                <StartPlanningButton style={{ width: '100%' }} />
            </div>
        </div>
    )
}

export default AlreadySubscribedPage
