import { useState } from 'react'
import { Form, Button } from 'react-bootstrap'
import { Link, useNavigate } from 'react-router-dom'
import GoogleLoginButton from "../components/GoogleLoginButton.tsx"
import { useAuth } from "../hooks/useAuth.ts"

function LoginPage() {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [showPassword, setShowPassword] = useState(false)
    const { handleLogin, loading, error } = useAuth()
    const navigate = useNavigate()

    return (
        <>
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
                        <div onClick={() => navigate('/')} style={{ color: '#7F77DD', fontWeight: 500, marginBottom: '1rem', cursor: 'pointer' }}>
                             AventraAI
                        </div>
                        <h1 style={{ fontSize: '22px', fontWeight: 500, color: '#26215C', margin: '0 0 4px' }}>
                            Welcome back
                        </h1>
                        <p style={{ fontSize: '13px', color: '#534AB7', margin: 0 }}>
                            Sign in to your account
                        </p>
                    </div>

                    {/* Body */}
                    <div style={{ padding: '1.5rem' }}>

                        <GoogleLoginButton onError={(msg) => console.error(msg)} />

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
                        <Form>
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

                            <Form.Group className="mb-2">
                                <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>Password</Form.Label>
                                <div style={{ position: 'relative' }}>
                                    <Form.Control
                                        type={showPassword ? 'text' : 'password'}
                                        placeholder="••••••••"
                                        value={password}
                                        onChange={e => setPassword(e.target.value)}
                                        required
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

                            <div style={{ textAlign: 'right', marginBottom: '1rem' }}>
                                <Link to="/forgot-password" style={{ fontSize: '12px', color: '#7F77DD', textDecoration: 'none' }}>
                                    Forgot password?
                                </Link>
                            </div>

                            <Button
                                type="button"
                                onClick={() => handleLogin(email, password)}
                                disabled={loading}
                                style={{ width: '100%', backgroundColor: '#7F77DD', border: 'none' }}
                            >
                                {loading ? 'Signing in...' : 'Sign in'}
                            </Button>
                        </Form>

                        <div style={{ textAlign: 'center', fontSize: '13px', color: '#6c757d', marginTop: '1rem' }}>
                            Don't have an account?{' '}
                            <Link to="/register" style={{ color: '#7F77DD', textDecoration: 'none' }}>
                                Sign up
                            </Link>
                        </div>

                    </div>
                </div>
            </div>
        </>
    )
}

export default LoginPage