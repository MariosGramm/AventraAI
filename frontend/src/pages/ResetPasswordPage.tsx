import { useState } from 'react'
import { Form, Button } from 'react-bootstrap'
import { Link, useSearchParams } from 'react-router-dom'
import client from '../services/client'

function ResetPasswordPage() {
    const [searchParams] = useSearchParams()
    const token = searchParams.get('token') || ''

    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const [loading, setLoading] = useState(false)
    const [success, setSuccess] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async () => {
        setError('')
        if (password.length < 8) {
            setError('Password must be at least 8 characters.')
            return
        }
        if (password !== confirmPassword) {
            setError('Passwords do not match.')
            return
        }
        setLoading(true)
        try {
            await client.post('/login/reset-password/', { token, new_password: password })
            setSuccess(true)
        } catch (err: any) {
            const detail = err?.response?.data?.detail
            setError(typeof detail === 'string' ? detail : 'Failed to reset password. The link may be expired.')
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
                        {success ? 'Password reset!' : 'Set new password'}
                    </h1>
                    <p style={{ fontSize: '13px', color: '#534AB7', margin: 0 }}>
                        {success ? 'You can now sign in with your new password' : 'Choose a new password for your account'}
                    </p>
                </div>

                {/* Body */}
                <div style={{ padding: '1.5rem' }}>
                    {success ? (
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '36px', marginBottom: '1rem' }}>✅</div>
                            <Link to="/login">
                                <Button style={{ width: '100%', backgroundColor: '#7F77DD', border: 'none' }}>
                                    Go to sign in
                                </Button>
                            </Link>
                        </div>
                    ) : !token ? (
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '36px', marginBottom: '1rem' }}>⚠️</div>
                            <p style={{ fontSize: '14px', color: '#cc0000', marginBottom: '1rem' }}>
                                Invalid or missing reset link.
                            </p>
                            <Link to="/forgot-password" style={{ fontSize: '13px', color: '#7F77DD', textDecoration: 'none' }}>
                                Request a new link →
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
                                    <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>New password</Form.Label>
                                    <div style={{ position: 'relative' }}>
                                        <Form.Control
                                            type={showPassword ? 'text' : 'password'}
                                            placeholder="••••••••"
                                            value={password}
                                            onChange={e => setPassword(e.target.value)}
                                            required
                                            minLength={8}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(prev => !prev)}
                                            style={{
                                                position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)',
                                                background: 'none', border: 'none', cursor: 'pointer',
                                                padding: '2px', display: 'flex', alignItems: 'center'
                                            }}
                                            tabIndex={-1}
                                        >
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6c757d" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                                                <circle cx="12" cy="12" r="3" />
                                                {showPassword && <line x1="1" y1="1" x2="23" y2="23" />}
                                            </svg>
                                        </button>
                                    </div>
                                </Form.Group>

                                <Form.Group className="mb-3">
                                    <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>Confirm password</Form.Label>
                                    <Form.Control
                                        type={showPassword ? 'text' : 'password'}
                                        placeholder="••••••••"
                                        value={confirmPassword}
                                        onChange={e => setConfirmPassword(e.target.value)}
                                        required
                                        minLength={8}
                                    />
                                </Form.Group>

                                <Button
                                    type="button"
                                    onClick={handleSubmit}
                                    disabled={loading || !password || !confirmPassword}
                                    style={{ width: '100%', backgroundColor: '#7F77DD', border: 'none' }}
                                >
                                    {loading ? 'Resetting...' : 'Reset password'}
                                </Button>
                            </Form>

                            <div style={{ textAlign: 'center', fontSize: '13px', color: '#6c757d', marginTop: '1rem' }}>
                                <Link to="/login" style={{ color: '#7F77DD', textDecoration: 'none' }}>
                                    ← Back to sign in
                                </Link>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}

export default ResetPasswordPage
