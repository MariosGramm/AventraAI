import {Button, Col, Container, Row} from "react-bootstrap";
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
            {/* Features Section */}
            <div style={{ padding: '4rem 0', background: '#f8f8ff' }}>
                <Container>
                    <h2 style={{ textAlign: 'center', fontSize: '28px', fontWeight: 500, marginBottom: '0.5rem' }}>
                        Everything you need to travel smarter
                    </h2>
                    <p style={{ textAlign: 'center', color: '#6c757d', marginBottom: '3rem' }}>
                        Powered by AI, real-time data, and local expertise
                    </p>

                    <Row>
                        {[
                            { icon: '🤖', title: 'AI travel agent', desc: 'Chat naturally and get personalized travel packages tailored to your style.' },
                            { icon: '🌤️', title: 'Real-time weather', desc: 'Get accurate forecasts for your travel dates so you can pack right.' },
                            { icon: '🏨', title: 'Hotel prices', desc: 'Compare live hotel prices across Booking.com, Airbnb and more.' },
                            { icon: '📍', title: 'Local attractions', desc: 'Discover the best restaurants, sights and experiences at your destination.' },
                        ].map((feature, index) => (
                            <Col key={index} md={3} sm={6} className="mb-4">
                                <div style={{
                                    background: 'white',
                                    border: '0.5px solid #e0e0e0',
                                    borderRadius: '12px',
                                    padding: '1.25rem',
                                    height: '100%'
                                }}>
                                    <div style={{
                                        width: '40px',
                                        height: '40px',
                                        background: '#EEEDFE',
                                        borderRadius: '8px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        marginBottom: '12px',
                                        fontSize: '20px'
                                    }}>
                                        {feature.icon}
                                    </div>
                                    <h3 style={{ fontSize: '15px', fontWeight: 500, marginBottom: '6px' }}>
                                        {feature.title}
                                    </h3>
                                    <p style={{ fontSize: '13px', color: '#6c757d', lineHeight: 1.6, margin: 0 }}>
                                        {feature.desc}
                                    </p>
                                </div>
                            </Col>
                        ))}
                    </Row>
                </Container>
            </div>

            {/* Pricing Section */}
            <div style={{ padding: '4rem 0', background: 'white' }}>
                <Container>
                    <h2 style={{ textAlign: 'center', fontSize: '28px', fontWeight: 500, marginBottom: '0.5rem' }}>
                        Simple, transparent pricing
                    </h2>
                    <p style={{ textAlign: 'center', color: '#6c757d', marginBottom: '3rem' }}>
                        Start for free. Upgrade when you're ready.
                    </p>

                    <Row className="justify-content-center">

                        {/* Free Plan */}
                        <Col md={4} className="mb-4">
                            <div style={{
                                border: '0.5px solid #e0e0e0',
                                borderRadius: '12px',
                                padding: '1.5rem',
                                height: '100%'
                            }}>
                                <h3 style={{ fontSize: '16px', fontWeight: 500 }}>Free</h3>
                                <p style={{ fontSize: '13px', color: '#6c757d' }}>Perfect for trying it out</p>
                                <div style={{ fontSize: '32px', fontWeight: 500, margin: '0.5rem 0' }}>
                                    €0 <span style={{ fontSize: '15px', fontWeight: 400, color: '#6c757d' }}>/ month</span>
                                </div>
                                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1.5rem' }}>
                                    {[
                                        '3 travel packages / month',
                                        'AI chat assistant',
                                        'Weather forecasts',
                                        'Hotel suggestions'
                                    ].map((feature, index) => (
                                        <li key={index} style={{ fontSize: '13px', color: '#6c757d', padding: '4px 0' }}>
                                            ✓ {feature}
                                        </li>
                                    ))}
                                </ul>
                                <Button variant="outline-secondary" style={{ width: '100%' }}>
                                    Get started
                                </Button>
                            </div>
                        </Col>

                        {/* Pro Plan */}
                        <Col md={4} className="mb-4">
                            <div style={{
                                border: '2px solid #7F77DD',
                                borderRadius: '12px',
                                padding: '1.5rem',
                                height: '100%'
                            }}>
                    <span style={{
                        display: 'inline-block',
                        background: '#EEEDFE',
                        color: '#534AB7',
                        borderRadius: '99px',
                        padding: '2px 10px',
                        fontSize: '12px',
                        marginBottom: '8px'
                    }}>
                        Most popular
                    </span>
                                <h3 style={{ fontSize: '16px', fontWeight: 500 }}>Pro</h3>
                                <p style={{ fontSize: '13px', color: '#6c757d' }}>For frequent travelers</p>
                                <div style={{ fontSize: '32px', fontWeight: 500, margin: '0.5rem 0' }}>
                                    €5.99 <span style={{ fontSize: '15px', fontWeight: 400, color: '#6c757d' }}>/ month</span>
                                </div>
                                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1.5rem' }}>
                                    {[
                                        'Unlimited packages',
                                        'Better AI Model',
                                        'Priority support',
                                        'Everything in Free'
                                    ].map((feature, index) => (
                                        <li key={index} style={{ fontSize: '13px', color: '#6c757d', padding: '4px 0' }}>
                                            ✓ {feature}
                                        </li>
                                    ))}
                                </ul>
                                <Button style={{ width: '100%', backgroundColor: '#7F77DD', border: 'none' }}>
                                    Upgrade to Pro
                                </Button>
                            </div>
                        </Col>

                    </Row>
                </Container>
            </div>

            {/* Footer */}
            <footer style={{
                padding: '2rem 0',
                borderTop: '0.5px solid #e0e0e0',
                textAlign: 'center',
                color: '#6c757d',
                fontSize: '13px'
            }}>
                <Container>
                    <p style={{ margin: 0 }}>
                        © 2026 AventraAI ·
                        <a href="/privacy" style={{ color: '#7F77DD', textDecoration: 'none', margin: '0 8px' }}>Privacy</a> ·
                        <a href="/terms" style={{ color: '#7F77DD', textDecoration: 'none', margin: '0 8px' }}>Terms</a>
                    </p>
                </Container>
            </footer>
        </>
    )
}

export default LandingPage;