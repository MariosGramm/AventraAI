import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Form, Modal } from 'react-bootstrap'
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

    useEffect(() => {
        if (user) {
            setFirstName(user.first_name || '')
            setLastName(user.last_name || '')
        }
    }, [user])
    const [cancelLoading, setCancelLoading] = useState(false)
    const [cancelError, setCancelError] = useState('')
    const [showCancelConfirm, setShowCancelConfirm] = useState(false)

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

    const handleCancelSubscription = async () => {
        setCancelLoading(true)
        setCancelError('')
        try {
            const response = await client.post('/payments/cancel-subscription')
            setUser({
                ...user!,
                subscription_cancel_at_period_end: true,
                subscription_current_period_end: response.data.current_period_end,
            })
            setShowCancelConfirm(false)
        } catch (err: any) {
            const detail = err?.response?.data?.detail
            setCancelError(typeof detail === 'string' ? detail : 'Failed to cancel subscription. Please try again.')
            setShowCancelConfirm(false)
        } finally {
            setCancelLoading(false)
        }
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
                                    ? `${Math.max(0, 20 - (user?.monthly_searches_used || 0))}/20 itineraries left · ${Math.max(0, 500 - (user?.monthly_messages_used || 0))}/500 messages left`
                                    : `${Math.max(0, 3 - (user?.monthly_searches_used || 0))}/3 itineraries left · ${Math.max(0, 50 - (user?.monthly_messages_used || 0))}/50 messages left`
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

                    {user?.subscription_tier === 'paid' && user.subscription_cancel_at_period_end && (
                        <div style={{ background: '#fff8e6', border: '0.5px solid #ffe4a3', borderRadius: '8px', padding: '10px 14px', fontSize: '13px', color: '#8a6300', marginBottom: '1rem' }}>
                            Your Pro plan is canceled and will remain active until{' '}
                            {user.subscription_current_period_end
                                ? new Date(user.subscription_current_period_end).toLocaleDateString()
                                : 'the end of the billing period'}.
                        </div>
                    )}

                    {cancelError && (
                        <div style={{ background: '#fff0f0', border: '0.5px solid #ffcccc', borderRadius: '8px', padding: '10px 14px', fontSize: '13px', color: '#cc0000', marginBottom: '1rem' }}>
                            {cancelError}
                        </div>
                    )}

                    {user?.subscription_tier !== 'paid' && (
                        <UpgradeButton style={{ width: '100%' }} />
                    )}

                    {user?.subscription_tier === 'paid' && !user.subscription_cancel_at_period_end && (
                        <Button
                            variant="outline-danger"
                            style={{ width: '100%' }}
                            onClick={() => setShowCancelConfirm(true)}
                            disabled={cancelLoading}
                        >
                            {cancelLoading ? 'Canceling...' : 'Cancel Pro subscription'}
                        </Button>
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

            <Modal show={showCancelConfirm} onHide={() => setShowCancelConfirm(false)} centered>
                <Modal.Header closeButton>
                    <Modal.Title style={{ fontSize: '18px', color: '#26215C' }}>Cancel subscription</Modal.Title>
                </Modal.Header>
                <Modal.Body style={{ color: '#6c757d', fontSize: '14px', lineHeight: 1.6 }}>
                    Are you sure you want to cancel your subscription? You'll keep Pro access until the end of your current billing period, and won't be charged again.
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="outline-secondary" onClick={() => setShowCancelConfirm(false)} disabled={cancelLoading}>
                        Keep subscription
                    </Button>
                    <Button variant="danger" onClick={handleCancelSubscription} disabled={cancelLoading}>
                        {cancelLoading ? 'Canceling...' : 'Yes, cancel'}
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    )
}

export default ProfilePage