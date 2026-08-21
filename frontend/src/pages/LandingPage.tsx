import {Button, Container } from "react-bootstrap";
import Navbar from "../components/Navbar.tsx";


function LandingPage() {

    return (
        <>
            {/* Top Navbar */}
            <Navbar />

            {/* Hero Section */}
            <div
                style={{
                    position: 'relative',
                    overflow: 'hidden',
                    background: 'linear-gradient(180deg, #EEEDFE 0%, #d4d0f8 100%)',
                    padding: '5rem 0 4rem',
                    textAlign: 'center'
                }}
            >
                {/* Sun */}
                <div style={{
                    position: 'absolute',
                    width: '70px',
                    height: '70px',
                    background: '#FAEEDA',
                    borderRadius: '50%',
                    right: '60px',
                    top: '24px',
                    animation: 'pulse 3s ease-in-out infinite'
                }} />

                {/* Clouds */}
                <div style={{ position: 'absolute', background: 'white', borderRadius: '50px', opacity: 0.75, width: '110px', height: '38px', left: '5%', top: '18%', animation: 'float 5s ease-in-out infinite' }} />
                <div style={{ position: 'absolute', background: 'white', borderRadius: '50px', opacity: 0.75, width: '75px', height: '26px', left: '28%', top: '35%', animation: 'float 6s ease-in-out infinite 0.8s' }} />
                <div style={{ position: 'absolute', background: 'white', borderRadius: '50px', opacity: 0.75, width: '130px', height: '42px', left: '58%', top: '12%', animation: 'float 7s ease-in-out infinite 1.5s' }} />
                <div style={{ position: 'absolute', background: 'white', borderRadius: '50px', opacity: 0.75, width: '60px', height: '22px', left: '80%', top: '55%', animation: 'float 4.5s ease-in-out infinite 0.3s' }} />
                <div style={{ position: 'absolute', background: 'white', borderRadius: '50px', opacity: 0.75, width: '90px', height: '30px', left: '15%', top: '68%', animation: 'float 5.5s ease-in-out infinite 1s' }} />

                {/* Airplane */}
                <div style={{
                    position: 'absolute',
                    fontSize: '28px',
                    animation: 'fly 12s linear infinite',
                    top: '40px'
                }}>
                    ✈️
                </div>

                {/* Content */}
                <Container style={{ position: 'relative', zIndex: 2 }}>
        <span style={{
            display: 'inline-block',
            background: 'rgba(255,255,255,0.8)',
            color: '#534AB7',
            border: '0.5px solid #AFA9EC',
            borderRadius: '99px',
            padding: '4px 14px',
            fontSize: '13px',
            marginBottom: '1.5rem'
        }}>
            AI-powered travel planning
        </span>

                    <h1 style={{ fontSize: '42px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        Your next adventure,<br />planned by AI
                    </h1>

                    <p style={{ fontSize: '18px', color: '#534AB7', maxWidth: '560px', margin: '0 auto 2rem', lineHeight: 1.7 }}>
                        Tell AventraAI where you want to go. Get personalized travel packages with hotels, activities, and real-time weather — in seconds.
                    </p>

                    <Button size="lg" style={{ backgroundColor: '#7F77DD', border: 'none', padding: '12px 32px' }}>
                        Try it out
                    </Button>
                </Container>
            </div>

            {/* Features Section */}

            {/* Pricing Section */}

            {/* Footer */}
        </>
    )
}

export default LandingPage;