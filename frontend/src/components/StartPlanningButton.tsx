import { useNavigate } from 'react-router-dom'
import { Button } from 'react-bootstrap'

interface StartPlanningButtonProps {
    label?: string
    style?: React.CSSProperties
}

function StartPlanningButton({ label = 'Start Planning →', style }: StartPlanningButtonProps) {
    const navigate = useNavigate()

    return (
        <Button
            style={{ backgroundColor: '#7F77DD', border: 'none', ...style }}
            onClick={() => navigate('/chat')}
        >
            {label}
        </Button>
    )
}

export default StartPlanningButton
