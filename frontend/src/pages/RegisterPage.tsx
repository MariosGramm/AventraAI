import { useState } from 'react'
import { Form, Button } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import GoogleLoginButton from "../components/GoogleLoginButton.tsx";
import PasswordInput from "../components/PasswordInput.tsx";
import AuthLogo from "../components/AuthLogo.tsx";
import {useAuth} from "../hooks/useAuth.ts";

function RegisterPage() {
    const [firstName, setFirstName] = useState('')
    const [lastName, setLastName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    const { handleRegister, loading, error } = useAuth()


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
                    <AuthLogo />
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
                            <PasswordInput value={password} onChange={setPassword} required minLength={8} />
                        </Form.Group>

                        <Button
                            type="button"
                            onClick={() => handleRegister(firstName, lastName, email, password)}
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