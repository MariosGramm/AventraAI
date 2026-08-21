import { Navbar as BsNavbar, Container, Button } from 'react-bootstrap'

function Navbar() {
    return (
        <BsNavbar bg="white" className="shadow-sm py-3">
            <Container>

                {/* Logo */}
                <BsNavbar.Brand href="/" style={{ color: '#7F77DD', fontWeight: 500 }}>
                    AventraAI
                </BsNavbar.Brand>

                {/* Buttons */}
                <div className="d-flex gap-2">
                    <Button variant="outline-secondary" size="sm">
                        Log in
                    </Button>
                    <Button size="sm" style={{ backgroundColor: '#7F77DD', border: 'none' }}>
                        Sign up
                    </Button>
                </div>

            </Container>
        </BsNavbar>
    )
}

export default Navbar