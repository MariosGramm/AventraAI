import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Form } from 'react-bootstrap'
import { useAuthContext } from '../context/AuthContext'
import UpgradeButton from '../components/UpgradeButton'
import client from '../services/client'

function ProfilePage() {
    const navigate = useNavigate()
    const { user, setUser } = useAuthContext()

    useEffect(() => {
        if (!localStorage.getItem('token')) navigate('/login', { replace: true })
    }, [])

    const [firstName, setFirstName] = useState(user?.first_name || '')
    const [lastName, setLastName] = useState(user?.last_name || '')
    const [loading, setLoading] = useState(false)
    const [success, setSuccess] = useState('')
    const [error, setError] = useState('')

    const getInitials = () => {
        if (!user) return '?'
        return `${user.first_name?.[0] || ''}${user.last_name?.[0] || ''}`.toUpperCase()
    }

    const handleUpdateProfile = async () => {
        setLoading(true)
        setError('')
        setSuccess('')
        try {
            const response = await client.patch('/users/me', {
                first_name: firstName,
                last_name: lastName
            })
            setUser(response.data)
            setSuccess('Profile updated successfully.')
        } catch (err) {
            setError('Failed to update profile.')
        } finally {
            setLoading(false)
        }
    }

    const handleLogout = () => {
        navigate('/logging-out')
    }

    return (
        <div style={{
            minHeight: '100vh',
            background: 'linear-gradient(180deg, #EEEDFE 0%, #d4d0f8 100%)',
            padding: '2rem'
        }}>
            {/* Back button */}
            <div style={{ maxWidth: '600px', margin: '0 auto 1rem' }}>
                <Button
                    variant="link"
                    style={{ color: '#7F77DD', textDecoration: 'none', padding: 0 }}
                    onClick={() => navigate('/chat')}
                >
                    ← Back to chat
                </Button>
            </div>

            <div style={{ maxWidth: '600px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>

                {/* Header */}
                <div style={{ background: 'white', borderRadius: '16px', padding: '2rem', textAlign: 'center' }}>
                    <div style={{
                        width: '64px', height: '64px', borderRadius: '50%',
                        background: '#EEEDFE', display: 'flex', alignItems: 'center',
                        justifyContent: 'center', fontSize: '22px', fontWeight: 500,
                        color: '#534AB7', margin: '0 auto 1rem'
                    }}>
                        {getInitials()}
                    </div>
                    <h1 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', margin: '0 0 4px' }}>
                        {user?.first_name} {user?.last_name}
                    </h1>
                    <p style={{ fontSize: '14px', color: '#6c757d', margin: 0 }}>
                        {user?.email}
                    </p>
                </div>

                {/* Personal Info */}
                <div style={{ background: 'white', borderRadius: '16px', padding: '1.5rem' }}>
                    <h2 style={{ fontSize: '16px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        Personal information
                    </h2>

                    {success && (
                        <div style={{ background: '#f0fff4', border: '0.5px solid #b2f5c8', borderRadius: '8px', padding: '10px 14px', fontSize: '13px', color: '#276749', marginBottom: '1rem' }}>
                            {success}
                        </div>
                    )}

                    {error && (
                        <div style={{ background: '#fff0f0', border: '0.5px solid #ffcccc', borderRadius: '8px', padding: '10px 14px', fontSize: '13px', color: '#cc0000', marginBottom: '1rem' }}>
                            {error}
                        </div>
                    )}

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                        <Form.Group>
                            <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>First name</Form.Label>
                            <Form.Control
                                type="text"
                                value={firstName}
                                onChange={e => setFirstName(e.target.value)}
                            />
                        </Form.Group>
                        <Form.Group>
                            <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>Last name</Form.Label>
                            <Form.Control
                                type="text"
                                value={lastName}
                                onChange={e => setLastName(e.target.value)}
                            />
                        </Form.Group>
                    </div>

                    <Form.Group className="mb-3">
                        <Form.Label style={{ fontSize: '13px', color: '#6c757d' }}>Email</Form.Label>
                        <Form.Control
                            type="email"
                            value={user?.email || ''}
                            disabled
                            style={{ background: '#f8f8ff', color: '#aaa' }}
                        />
                    </Form.Group>

                    <Button
                        onClick={handleUpdateProfile}
                        disabled={loading}
                        style={{ backgroundColor: '#7F77DD', border: 'none' }}
                    >
                        {loading ? 'Saving...' : 'Save changes'}
                    </Button>
                </div>

                {/* Subscription */}
                <div style={{ background: 'white', borderRadius: '16px', padding: '1.5rem' }}>
                    <h2 style={{ fontSize: '16px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        Subscription
                    </h2>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <div>
                            <div style={{ fontSize: '14px', fontWeight: 500, color: '#26215C' }}>
                                {user?.subscription_tier === 'paid' ? 'Pro plan' : 'Free plan'}
                            </div>
                            <div style={{ fontSize: '13px', color: '#6c757d' }}>
                                {user?.subscription_tier === 'paid'
                                    ? 'Unlimited searches'
                                    : '3 searches / month'
                                }
                            </div>
                        </div>
                        <span style={{
                            padding: '4px 12px', borderRadius: '99px', fontSize: '12px',
                            background: user?.subscription_tier === 'paid' ? '#EEEDFE' : '#f0f0f0',
                            color: user?.subscription_tier === 'paid' ? '#534AB7' : '#6c757d'
                        }}>
                            {user?.subscription_tier === 'paid' ? 'Pro' : 'Free'}
                        </span>
                    </div>

                    {user?.subscription_tier !== 'paid' && (
                        <UpgradeButton style={{ width: '100%' }} />
                    )}
                </div>

                {/* Danger Zone */}
                <div style={{ background: 'white', borderRadius: '16px', padding: '1.5rem' }}>
                    <Button
                        variant="outline-danger"
                        style={{ width: '100%' }}
                        onClick={handleLogout}
                    >
                        Log out
                    </Button>
                </div>

            </div>
        </div>
    )
}

export default ProfilePage