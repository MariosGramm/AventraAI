import { useNavigate } from 'react-router-dom'

function AuthLogo() {
    const navigate = useNavigate()

    return (
        <div
            onClick={() => navigate('/')}
            style={{ color: '#7F77DD', fontWeight: 500, marginBottom: '1rem', cursor: 'pointer' }}
        >
            AventraAI
        </div>
    )
}

export default AuthLogo
