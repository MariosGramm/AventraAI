import StartPlanningButton from '../components/StartPlanningButton.tsx'

function UpgradeSuccessPage() {

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
                <div style={{ fontSize: '48px', marginBottom: '1rem' }}>🎉</div>

                <h1 style={{ fontSize: '24px', fontWeight: 500, color: '#26215C', marginBottom: '0.5rem' }}>
                    You have successfully upgraded!
                </h1>

                <p style={{ color: '#6c757d', lineHeight: 1.8, marginBottom: '0.5rem' }}>
                    Thank you for subscribing to AventraAI Pro.
                </p>

                <p style={{ color: '#6c757d', fontSize: '13px', marginBottom: '2rem' }}>
                    We sent a confirmation email to your inbox.
                </p>

                <div style={{
                    background: '#EEEDFE',
                    borderRadius: '12px',
                    padding: '1rem',
                    marginBottom: '2rem'
                }}>
                    <p style={{ color: '#534AB7', fontSize: '13px', margin: 0 }}>
                        You now have unlimited access to AI-powered travel planning. Let's plan your next adventure!
                    </p>
                </div>

                <StartPlanningButton style={{ width: '100%' }} />
            </div>
        </div>
    )
}

export default UpgradeSuccessPage
