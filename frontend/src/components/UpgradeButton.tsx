import { useState } from 'react'
import { Button } from 'react-bootstrap'
import client from '../services/client'

interface UpgradeButtonProps {
    variant?: 'primary' | 'outline'
    size?: 'sm' | 'lg'
    label?: string
    style?: React.CSSProperties
}

function UpgradeButton({
                           variant = 'primary',
                           size,
                           label = 'Upgrade to Pro',
                           style
                       }: UpgradeButtonProps) {
    const [loading, setLoading] = useState(false)

    const handleUpgrade = async () => {
        setLoading(true)
        try {
            const response = await client.post('/payments/create-checkout-session')
            window.location.href = response.data.checkout_url
        } catch (err) {
            console.error('Failed to create checkout session')
        } finally {
            setLoading(false)
        }
    }

    return (
        <Button
            size={size}
            onClick={handleUpgrade}
            disabled={loading}
            style={
                variant === 'primary'
                    ? { backgroundColor: '#7F77DD', border: 'none', ...style }
                    : { color: '#7F77DD', borderColor: '#7F77DD', ...style }
            }
            variant={variant === 'outline' ? 'outline-primary' : undefined}
        >
            {loading ? 'Loading...' : `${label}`}
        </Button>
    )
}

export default UpgradeButton