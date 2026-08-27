import { Container } from 'react-bootstrap'
import Navbar from '../components/Navbar'

function TermsPage() {
    return (
        <div>
            <Navbar />
            <Container style={{ maxWidth: '800px', padding: '4rem 1rem' }}>

                <h1 style={{ fontSize: '32px', fontWeight: 500, color: '#26215C', marginBottom: '0.5rem' }}>
                    Terms of Service
                </h1>
                <p style={{ color: '#6c757d', fontSize: '14px', marginBottom: '3rem' }}>
                    Last updated: August 2026
                </p>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        1. Acceptance of Terms
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        By accessing or using AventraAI, you agree to be bound by these Terms of Service. 
                        If you do not agree to these terms, please do not use our service.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        2. Description of Service
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        AventraAI is an AI-powered travel planning assistant that helps users discover destinations, 
                        create personalized travel packages, and find accommodation options. 
                        The service uses artificial intelligence to generate travel recommendations based on user input.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        3. Free and Paid Tiers
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        AventraAI offers two subscription tiers:
                    </p>
                    <ul style={{ color: '#6c757d', lineHeight: 2 }}>
                        <li>
                            <strong>Free tier:</strong> limited to 3 travel packages per month. 
                            Access to AI chat assistant, weather forecasts, and hotel suggestions.
                        </li>
                        <li>
                            <strong>Pro tier (€5.99/month):</strong> unlimited travel packages, 
                            access to higher quality AI model, and priority support.
                        </li>
                    </ul>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        Subscriptions are billed monthly and can be cancelled at any time. 
                        Cancellation takes effect at the end of the current billing period.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        4. Prohibited Uses
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        You agree not to use AventraAI to:
                    </p>
                    <ul style={{ color: '#6c757d', lineHeight: 2 }}>
                        <li>Attempt to reverse engineer, hack, or disrupt the service.</li>
                        <li>Use the service for any illegal or unauthorized purpose.</li>
                        <li>Scrape or collect data from the service without permission.</li>
                        <li>Share your account credentials with third parties.</li>
                        <li>Generate content that is harmful, offensive, or misleading.</li>
                        <li>Attempt to circumvent the free tier limitations.</li>
                    </ul>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        5. AI Accuracy Disclaimer
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        AventraAI uses artificial intelligence to generate travel recommendations. 
                        While we strive for accuracy, AI-generated content may contain errors, 
                        outdated information, or inaccuracies. We strongly recommend:
                    </p>
                    <ul style={{ color: '#6c757d', lineHeight: 2 }}>
                        <li>Verifying all travel information (visa requirements, prices, opening hours) independently.</li>
                        <li>Checking hotel and flight prices directly with providers before booking.</li>
                        <li>Not relying solely on AI recommendations for critical travel decisions.</li>
                    </ul>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        AventraAI is not responsible for any loss or inconvenience arising from 
                        reliance on AI-generated travel recommendations.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        6. Intellectual Property
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        All content, features, and functionality of AventraAI — including but not limited to 
                        text, graphics, logos, and software — are the exclusive property of AventraAI 
                        and are protected by applicable intellectual property laws.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        7. Limitation of Liability
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        To the maximum extent permitted by law, AventraAI shall not be liable for any 
                        indirect, incidental, special, or consequential damages arising from your use 
                        of the service, including but not limited to travel losses, booking errors, 
                        or reliance on AI-generated content.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        8. Changes to Terms
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        We reserve the right to modify these Terms of Service at any time. 
                        We will notify you of significant changes via email or through the app. 
                        Continued use of the service after changes constitutes acceptance of the new terms.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ fontSize: '20px', fontWeight: 500, color: '#26215C', marginBottom: '1rem' }}>
                        9. Contact
                    </h2>
                    <p style={{ color: '#6c757d', lineHeight: 1.8 }}>
                        If you have any questions about these Terms of Service, please contact us at:
                        <br />
                        <a href="mailto:legal@aventraai.com" style={{ color: '#7F77DD' }}>
                            legal@aventraai.com
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

export default TermsPage
