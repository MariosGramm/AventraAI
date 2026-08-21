import { useState } from 'react'
import { Form, Button } from 'react-bootstrap'
import { useNavigate, Link } from 'react-router-dom'

function RegisterPage() {
    const navigate = useNavigate()

    const [firstName, setFirstName] = useState('')
    const [lastName, setLastName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            // TODO: implement register API call
            navigate('/chat')
        } catch (err) {
            setError('Something went wrong. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    const handleGoogleLogin = () => {
        // TODO: implement Google login
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
                        Create account
                    </h1>
                    <p style={{ fontSize: '13px', color: '#534AB7', margin: 0 }}>
                        Start planning your next adventure
                    </p>
                </div>

                {/* Body */}
                <div style={{ padding: '1.5rem' }}>

                    {/* Google Button */}
                    <Button
                        variant="outline-secondary"
                        style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '1rem' }}
                        onClick={handleGoogleLogin}
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        Continue with Google
                    </Button>

                    {/* Divider */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: '1rem 0' }}>
                        <div style={{ flex: 1, height: '0.5px', background: '#e0e0e0' }} />
                        <span style={{ fontSize: '12px', color: '#6c757d' }}>or</span>
                        <div style={{ flex: 1, height: '0.5px', background: '#e0e0e0' }} />
                    </div>

                    {/* Error */}
                    {error && (
                        <div style={{ background: '#fff0f0', border: '0.5px solid #ffcccc', borderRadius: '8px', padding: '10px 14px', fontSize: '13px', color: '#cc0000', marginBottom: '1rem' }}>
                            {error}
                        </div>
                    )}

                    {/* Form */}
                    <Form onSubmit={handleSubmit}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                            <Form.Group className="mb-3">
                                <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>First name</Form.Label>
                                <Form.Control
                                    type="text"
                                    placeholder="John"
                                    value={firstName}
                                    onChange={e => setFirstName(e.target.value)}
                                    required
                                />
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>Last name</Form.Label>
                                <Form.Control
                                    type="text"
                                    placeholder="Doe"
                                    value={lastName}
                                    onChange={e => setLastName(e.target.value)}
                                    required
                                />
                            </Form.Group>
                        </div>

                        <Form.Group className="mb-3">
                            <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>Email</Form.Label>
                            <Form.Control
                                type="email"
                                placeholder="johndoe@email.com"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                required
                            />
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>Password</Form.Label>
                            <Form.Control
                                type="password"
                                placeholder="••••••••"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                required
                                minLength={8}
                            />
                        </Form.Group>

                        <Button
                            type="submit"
                            style={{ width: '100%', backgroundColor: '#7F77DD', border: 'none' }}
                            disabled={loading}
                        >
                            {loading ? 'Creating account...' : 'Create account'}
                        </Button>
                    </Form>

                    <div style={{ textAlign: 'center', fontSize: '13px', color: '#6c757d', marginTop: '1rem' }}>
                        Already have an account?{' '}
                        <Link to="/login" style={{ color: '#7F77DD', textDecoration: 'none' }}>
                            Sign in
                        </Link>
                    </div>

                    <div style={{ textAlign: 'center', fontSize: '11px', color: '#6c757d', marginTop: '0.5rem' }}>
                        By signing up you agree to our{' '}
                        <Link to="/terms" style={{ color: '#7F77DD', textDecoration: 'none' }}>Terms</Link>
                        {' '}and{' '}
                        <Link to="/privacy" style={{ color: '#7F77DD', textDecoration: 'none' }}>Privacy Policy</Link>
                    </div>

                </div>
            </div>
        </div>
    )
}

export default RegisterPage