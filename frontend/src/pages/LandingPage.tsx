import { useState, useEffect } from "react";
import {Button, Col, Container, Row} from "react-bootstrap";
import { useNavigate } from 'react-router-dom'
import Navbar from "../components/Navbar.tsx";
import UpgradeButton from "../components/UpgradeButton.tsx";

const CITY_SETS = [
    [
        { city: 'Tokyo', tag: 'Culture & Tech', top: '12%', left: '6%', rotate: '-5deg' },
        { city: 'Santorini', tag: 'Islands & Sun', top: '18%', right: '5%', rotate: '4deg' },
        { city: 'Paris', tag: 'Romance & Art', top: '65%', left: '3%', rotate: '3deg' },
        { city: 'New York', tag: 'City & Nightlife', top: '60%', right: '4%', rotate: '-3deg' },
    ],
    [
        { city: 'Barcelona', tag: 'Beach & Culture', top: '14%', left: '5%', rotate: '-4deg' },
        { city: 'Bali', tag: 'Wellness & Nature', top: '20%', right: '6%', rotate: '5deg' },
        { city: 'London', tag: 'History & Pubs', top: '62%', left: '4%', rotate: '2deg' },
        { city: 'Dubai', tag: 'Luxury & Adventure', top: '58%', right: '5%', rotate: '-4deg' },
    ],
    [
        { city: 'Prague', tag: 'Architecture & Beer', top: '10%', left: '7%', rotate: '-6deg' },
        { city: 'Marrakech', tag: 'Souks & Spice', top: '16%', right: '4%', rotate: '3deg' },
        { city: 'Lisbon', tag: 'Trams & Pastéis', top: '66%', left: '2%', rotate: '5deg' },
        { city: 'Sydney', tag: 'Coast & Wildlife', top: '62%', right: '3%', rotate: '-5deg' },
    ],
    [
        { city: 'Amsterdam', tag: 'Canals & Art', top: '13%', left: '4%', rotate: '-3deg' },
        { city: 'Kyoto', tag: 'Temples & Gardens', top: '19%', right: '7%', rotate: '6deg' },
        { city: 'Rome', tag: 'Ruins & Gelato', top: '63%', left: '5%', rotate: '4deg' },
        { city: 'Cape Town', tag: 'Mountains & Wine', top: '59%', right: '6%', rotate: '-4deg' },
    ],
    [
        { city: 'Vienna', tag: 'Music & Coffee', top: '11%', left: '6%', rotate: '-5deg' },
        { city: 'Reykjavik', tag: 'Northern Lights', top: '17%', right: '5%', rotate: '4deg' },
        { city: 'Bangkok', tag: 'Street Food & Temples', top: '64%', left: '3%', rotate: '3deg' },
        { city: 'Buenos Aires', tag: 'Tango & Steak', top: '61%', right: '4%', rotate: '-3deg' },
    ],
    [
        { city: 'Istanbul', tag: 'East meets West', top: '12%', left: '5%', rotate: '-4deg' },
        { city: 'Havana', tag: 'Vintage & Rhythm', top: '20%', right: '6%', rotate: '5deg' },
        { city: 'Seoul', tag: 'K-Culture & BBQ', top: '65%', left: '4%', rotate: '2deg' },
        { city: 'Amalfi', tag: 'Cliffs & Lemons', top: '60%', right: '5%', rotate: '-5deg' },
    ],
]


function LandingPage() {
    const navigate = useNavigate()
    const [cityIndex, setCityIndex] = useState(0)
    const [fading, setFading] = useState(false)

    useEffect(() => {
        const interval = setInterval(() => {
            setFading(true)
            setTimeout(() => {
                setCityIndex(prev => (prev + 1) % CITY_SETS.length)
                setFading(false)
            }, 400)
        }, 10000)
        return () => clearInterval(interval)
    }, [])

    const cities = CITY_SETS[cityIndex]

    return (
        <>
            {/* Top Navbar */}
            <Navbar />

            {/* Hero Section */}
            <div
                style={{
                    position: 'relative',
                    overflow: 'hidden',
                    background: 'linear-gradient(135deg, #EEEDFE 0%, #d4d0f8 40%, #c4bef5 100%)',
                    padding: '6rem 0 5rem',
                    textAlign: 'center',
                    minHeight: '600px'
                }}
            >
                {/* Animated gradient orbs */}
                <div style={{
                    position: 'absolute', width: '400px', height: '400px',
                    background: 'radial-gradient(circle, rgba(127,119,221,0.3) 0%, transparent 70%)',
                    borderRadius: '50%', top: '-100px', left: '-100px',
                    animation: 'orbFloat 8s ease-in-out infinite'
                }} />
                <div style={{
                    position: 'absolute', width: '350px', height: '350px',
                    background: 'radial-gradient(circle, rgba(83,74,183,0.2) 0%, transparent 70%)',
                    borderRadius: '50%', bottom: '-80px', right: '-60px',
                    animation: 'orbFloat 10s ease-in-out infinite reverse'
                }} />
                <div style={{
                    position: 'absolute', width: '200px', height: '200px',
                    background: 'radial-gradient(circle, rgba(175,169,236,0.25) 0%, transparent 70%)',
                    borderRadius: '50%', top: '30%', right: '15%',
                    animation: 'orbFloat 6s ease-in-out infinite 1s'
                }} />

                {/* Floating destination cards — rotate every 10s */}
                {cities.map((card, i) => (
                    <div key={`${cityIndex}-${i}`}
                        onClick={() => navigate('/chat?guest=true')}
                        style={{
                            position: 'absolute',
                            top: card.top, left: (card as any).left, right: (card as any).right,
                            background: 'rgba(255,255,255,0.85)',
                            backdropFilter: 'blur(10px)',
                            borderRadius: '14px',
                            padding: '14px 20px',
                            boxShadow: '0 8px 32px rgba(127,119,221,0.12)',
                            border: '1px solid rgba(255,255,255,0.6)',
                            animation: `cardFloat 5s ease-in-out infinite ${i * 0.6}s`,
                            transform: `rotate(${card.rotate})`,
                            zIndex: 1,
                            cursor: 'pointer',
                            opacity: fading ? 0 : 1,
                            transition: 'opacity 0.4s ease, transform 0.2s ease, box-shadow 0.2s ease',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.transform = `rotate(${card.rotate}) scale(1.08)`; e.currentTarget.style.boxShadow = '0 12px 40px rgba(127,119,221,0.22)' }}
                        onMouseLeave={e => { e.currentTarget.style.transform = `rotate(${card.rotate}) scale(1)`; e.currentTarget.style.boxShadow = '0 8px 32px rgba(127,119,221,0.12)' }}
                    >
                        <div style={{ fontSize: '14px', fontWeight: 600, color: '#26215C', marginBottom: '2px' }}>{card.city}</div>
                        <div style={{ fontSize: '11px', color: '#7F77DD', fontWeight: 500 }}>{card.tag}</div>
                    </div>
                ))}

                {/* Decorative dots grid */}
                <div style={{
                    position: 'absolute', top: '40%', left: '12%', opacity: 0.15,
                    display: 'grid', gridTemplateColumns: 'repeat(5, 8px)', gap: '10px'
                }}>
                    {Array.from({ length: 15 }).map((_, i) => (
                        <div key={i} style={{ width: '4px', height: '4px', borderRadius: '50%', background: '#534AB7' }} />
                    ))}
                </div>
                <div style={{
                    position: 'absolute', bottom: '15%', right: '10%', opacity: 0.15,
                    display: 'grid', gridTemplateColumns: 'repeat(4, 8px)', gap: '10px'
                }}>
                    {Array.from({ length: 12 }).map((_, i) => (
                        <div key={i} style={{ width: '4px', height: '4px', borderRadius: '50%', background: '#534AB7' }} />
                    ))}
                </div>

                {/* Content */}
                <Container style={{ position: 'relative', zIndex: 2 }}>
                    <div style={{
                        display: 'inline-flex', alignItems: 'center', gap: '8px',
                        background: 'rgba(255,255,255,0.7)',
                        backdropFilter: 'blur(8px)',
                        color: '#534AB7',
                        border: '1px solid rgba(175,169,236,0.4)',
                        borderRadius: '99px',
                        padding: '6px 18px',
                        fontSize: '13px',
                        marginBottom: '2rem',
                        animation: 'fadeSlideUp 0.8s ease-out'
                    }}>
                        <span style={{
                            width: '6px', height: '6px', borderRadius: '50%',
                            background: '#7F77DD', display: 'inline-block',
                            animation: 'pulse 2s ease-in-out infinite'
                        }} />
                        AI-powered travel planning
                    </div>

                    <h1 style={{
                        fontSize: '52px', fontWeight: 600, color: '#26215C',
                        marginBottom: '1.25rem', lineHeight: 1.15,
                        animation: 'fadeSlideUp 0.8s ease-out 0.15s both'
                    }}>
                        Your next adventure,<br />
                        <span style={{
                            background: 'linear-gradient(135deg, #7F77DD, #534AB7)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent'
                        }}>planned by AI</span>
                    </h1>

                    <p style={{
                        fontSize: '18px', color: '#534AB7', maxWidth: '560px',
                        margin: '0 auto 2.5rem', lineHeight: 1.7, opacity: 0.85,
                        animation: 'fadeSlideUp 0.8s ease-out 0.3s both'
                    }}>
                        Tell AventraAI where you want to go. Get personalized travel packages with hotels, activities, and real-time weather — in seconds.
                    </p>

                    <div style={{ animation: 'fadeSlideUp 0.8s ease-out 0.45s both' }}>
                        <Button size="lg" style={{
                            backgroundColor: '#7F77DD', border: 'none',
                            padding: '14px 40px', fontSize: '16px', fontWeight: 500,
                            borderRadius: '12px',
                            boxShadow: '0 4px 20px rgba(127,119,221,0.35)',
                            transition: 'transform 0.2s, box-shadow 0.2s'
                        }}
                        onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 30px rgba(127,119,221,0.45)' }}
                        onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 20px rgba(127,119,221,0.35)' }}
                        onClick={() => navigate('/chat?guest=true')}>
                            Try it out →
                        </Button>
                    </div>
                </Container>

                {/* CSS Animations */}
                <style>{`
                    @keyframes orbFloat {
                        0%, 100% { transform: translate(0, 0) scale(1); }
                        33% { transform: translate(30px, -20px) scale(1.05); }
                        66% { transform: translate(-20px, 15px) scale(0.95); }
                    }
                    @keyframes cardFloat {
                        0%, 100% { transform: translateY(0) rotate(var(--r, 0deg)); }
                        50% { transform: translateY(-12px) rotate(var(--r, 0deg)); }
                    }
                    @keyframes fadeSlideUp {
                        from { opacity: 0; transform: translateY(24px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    @keyframes pulse {
                        0%, 100% { opacity: 1; transform: scale(1); }
                        50% { opacity: 0.6; transform: scale(1.15); }
                    }
                `}</style>
            </div>

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
                                <UpgradeButton style={{ width: '100%' }} />
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