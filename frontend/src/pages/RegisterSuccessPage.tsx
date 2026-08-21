import { useNavigate } from 'react-router-dom'
import { Button } from 'react-bootstrap'

function RegisterSuccessPage() {
    const navigate = useNavigate()

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
                <div style={{ fontSize: '48px', marginBottom: '1rem' }}>✈️</div>

                <h1 style={{ fontSize: '24px', fontWeight: 500, color: '#26215C', marginBottom: '0.5rem' }}>
                    Welcome to AventraAI!
                </h1>

                <p style={{ color: '#6c757d', lineHeight: 1.8, marginBottom: '0.5rem' }}>
                    Your account has been created successfully.
                </p>

                <p style={{ color: '#6c757d', fontSize: '13px', marginBottom: '2rem' }}>
                    We sent a welcome email to your inbox.
                </p>

                <div style={{
                    background: '#EEEDFE',
                    borderRadius: '12px',
                    padding: '1rem',
                    marginBottom: '2rem'
                }}>
                    <p style={{ color: '#534AB7', fontSize: '13px', margin: 0 }}>
                        Start chatting with your AI travel agent and plan your next adventure!
                    </p>
                </div>

                <Button
                    style={{ width: '100%', backgroundColor: '#7F77DD', border: 'none' }}
                    onClick={() => navigate('/chat')}
                >
                    Start Planning →
                </Button>
            </div>
        </div>
    )
}

export default RegisterSuccessPage