import { Navbar as BsNavbar, Container, Button } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated } from '../services/authService'
import StartPlanningButton from './StartPlanningButton.tsx'

function Navbar() {
    const navigate = useNavigate()
    const loggedIn = isAuthenticated()

    const handleLogout = () => {
        navigate('/logging-out')
    }

    return (
        <BsNavbar bg="white" className="shadow-sm py-3">
            <Container>

                {/* Logo */}
                <BsNavbar.Brand href="/" style={{ color: '#7F77DD', fontWeight: 500 }}>
                     AventraAI
                </BsNavbar.Brand>

                {/* Buttons */}
                <div className="d-flex gap-2">
                    {loggedIn ? (
                        <>
                            <Button variant="outline-secondary" size="sm" onClick={handleLogout}>
                                Log out
                            </Button>
                            <StartPlanningButton style={{ fontSize: '14px', padding: '0.25rem 0.75rem' }} />
                        </>
                    ) : (
                        <>
                            <Button variant="outline-secondary" size="sm" onClick={() => navigate('/login')}>
                                Log in
                            </Button>
                            <Button size="sm" style={{ backgroundColor: '#7F77DD', border: 'none' }} onClick={() => navigate('/register')}>
                                Sign up
                            </Button>
                        </>
                    )}
                </div>

            </Container>
        </BsNavbar>
    )
}

export default Navbar