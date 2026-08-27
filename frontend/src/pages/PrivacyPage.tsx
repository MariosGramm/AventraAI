import { Container } from 'react-bootstrap'
import Navbar from '../components/Navbar'

function PrivacyPage() {
    return (
        <div>
            <Navbar />
            <Container style={{ maxWidth: '800px', padding: '4rem 1rem' }}>

                <h1 style={{ fontSize: '32px', fontWeight: 500, color: '#26215C', marginBottom: '0.5rem' }}>
                    Privacy Policy
                </h1>
                <p style={{ color: '#6c757d', fontSize: '14px', marginBottom: '3rem' }}>
                    Last updated: August 2026
                </p>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        1. Information We Collect
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        When you use AventraAI, we collect the following information:
                    </p>
                    <ul style={{ color: '#6c757d', lineHeight: 2 }}>
                        <li><strong>Account information:</strong> your name and email address when you register.</li>
                        <li><strong>Travel preferences:</strong> destinations, dates, budget, and trip type you provide when searching.</li>
                        <li><strong>Location data:</strong> your approximate city of origin, only when you choose to share it for flight search purposes. We do not store your precise location.</li>
                        <li><strong>Usage data:</strong> how you interact with the app, including chat messages and search history.</li>
                        <li><strong>Payment information:</strong> processed securely by Stripe. We do not store your card details.</li>
                    </ul>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        2. How We Use Your Information
                    </h2>
                    <ul style={{ color: '#6c757d', lineHeight: 2 }}>
                        <li>To provide personalized AI-powered travel recommendations.</li>
                        <li>To process your subscription payments.</li>
                        <li>To improve our AI models and service quality.</li>
                        <li>To send you service-related emails (e.g. account confirmation).</li>
                        <li>To enforce our Terms of Service and prevent misuse.</li>
                    </ul>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        3. Third-Party Services
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        AventraAI uses the following third-party services to operate:
                    </p>
                    <ul style={{ color: '#6c757d', lineHeight: 2 }}>
                        <li><strong>OpenAI:</strong> powers our AI travel agent. Your messages may be processed by OpenAI's API.</li>
                        <li><strong>Google:</strong> used for sign-in (OAuth2) and location services.</li>
                        <li><strong>Stripe:</strong> handles all payment processing securely.</li>
                        <li><strong>Resend:</strong> used to send transactional emails.</li>
                        <li><strong>StayingAPI:</strong> provides real-time hotel pricing data.</li>
                        <li><strong>Open-Meteo:</strong> provides weather forecast data.</li>
                    </ul>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        Each of these services has its own privacy policy. We encourage you to review them.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        4. Cookies
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        We use only essential cookies necessary for authentication and session management.
                        We do not use advertising or tracking cookies.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        5. Your Rights (GDPR)
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        If you are located in the European Union, you have the following rights:
                    </p>
                    <ul style={{ color: '#6c757d', lineHeight: 2 }}>
                        <li><strong>Access:</strong> request a copy of your personal data.</li>
                        <li><strong>Rectification:</strong> correct inaccurate personal data.</li>
                        <li><strong>Erasure:</strong> request deletion of your account and data.</li>
                        <li><strong>Portability:</strong> receive your data in a machine-readable format.</li>
                        <li><strong>Objection:</strong> object to the processing of your data.</li>
                    </ul>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        To exercise any of these rights, please contact us at the email below.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        6. Data Retention
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        We retain your personal data for as long as your account is active.
                        If you delete your account, we will delete your personal data within 30 days,
                        except where we are required to retain it by law.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        7. Contact
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        If you have any questions about this Privacy Policy or wish to exercise your rights,
                        please contact us at:
                        <br />
                        <a href="mailto:privacy@aventraai.com" style={{ color: '#7F77DD' }}>
                            privacy@aventraai.com
                        </a>
                    </p>
                </section>

            </Container>

            <footer style={{ padding: '2rem 0', borderTop: '0.5px solid #e0e0e0', textAlign: 'center', color: '#6c757d', fontSize: '13px' }}>
                <Container>
                    <p style={{ margin: 0 }}>
                        © 2026 AventraAI ·
                        <a href="/privacy" style={{ color: '#7F77DD', textDecoration: 'none', margin: '0 8px' }}>Privacy</a> ·
                        <a href="/terms" style={{ color: '#7F77DD', textDecoration: 'none', margin: '0 8px' }}>Terms</a>
                    </p>
                </Container>
            </footer>
        </div>
    )
}

export default PrivacyPage
