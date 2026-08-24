import { useState } from 'react'
import { Form, Button } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import client from '../services/client'

function ForgotPasswordPage() {
    const [email, setEmail] = useState('')
    const [loading, setLoading] = useState(false)
    const [sent, setSent] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async () => {
        if (!email.trim()) return
        setLoading(true)
        setError('')
        try {
            await client.post(`/login/password-recovery/${encodeURIComponent(email)}`)
            setSent(true)
        } catch {
            setSent(true)
        } finally {
            setLoading(false)
        }
    }

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
                overflow: 'hidden',
                width: '100%',
                maxWidth: '420px',
                boxShadow: '0 4px 24px rgba(127, 119, 221, 0.15)'
            }}>
                {/* Header */}
                <div style={{
                    background: 'linear-gradient(180deg, #EEEDFE 0%, #d4d0f8 100%)',
                    padding: '2rem',
                    textAlign: 'center'
                }}>
                    <div style={{ color: '#7F77DD', fontWeight: 500, marginBottom: '1rem' }}>
                        AventraAI
                    </div>
                    <h1 style={{ fontSize: '22px', fontWeight: 500, color: '#26215C', margin: '0 0 4px' }}>
                        Reset your password
                    </h1>
                    <p style={{ fontSize: '13px', color: '#534AB7', margin: 0 }}>
                        We'll send you a recovery link
                    </p>
                </div>

                {/* Body */}
                <div style={{ padding: '1.5rem' }}>
                    {sent ? (
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '36px', marginBottom: '1rem' }}>📧</div>
                            <p style={{ fontSize: '14px', color: '#26215C', marginBottom: '0.5rem', fontWeight: 500 }}>
                                Check your email
                            </p>
                            <p style={{ fontSize: '13px', color: '#6c757d', marginBottom: '1.5rem' }}>
                                If an account exists for <strong>{email}</strong>, we've sent a password reset link.
                            </p>
                            <Link to="/login" style={{ fontSize: '13px', color: '#7F77DD', textDecoration: 'none' }}>
                                ← Back to sign in
                            </Link>
                        </div>
                    ) : (
                        <>
                            {error && (
                                <div style={{ background: '#fff0f0', border: '0.5px solid #ffcccc', borderRadius: '8px', padding: '10px 14px', fontSize: '13px', color: '#cc0000', marginBottom: '1rem' }}>
                                    {error}
                                </div>
                            )}

                            <Form>
                                <Form.Group className="mb-3">
                                    <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>Email address</Form.Label>
                                    <Form.Control
                                        type="email"
                                        placeholder="johndoe@email.com"
                                        value={email}
                                        onChange={e => setEmail(e.target.value)}
                                        onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleSubmit() } }}
                                        required
                                    />
                                </Form.Group>

                                <Button
                                    type="button"
                                    onClick={handleSubmit}
                                    disabled={loading || !email.trim()}
                                    style={{ width: '100%', backgroundColor: '#7F77DD', border: 'none' }}
                                >
                                    {loading ? 'Sending...' : 'Send recovery link'}
                                </Button>
                            </Form>

                            <div style={{ textAlign: 'center', fontSize: '13px', color: '#6c757d', marginTop: '1rem' }}>
                                Remember your password?{' '}
                                <Link to="/login" style={{ color: '#7F77DD', textDecoration: 'none' }}>
                                    Sign in
                                </Link>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}

export default ForgotPasswordPage
