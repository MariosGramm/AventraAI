import { useState } from 'react'
import { Form } from 'react-bootstrap'

interface PasswordInputProps {
    value: string
    onChange: (value: string) => void
    placeholder?: string
    required?: boolean
    minLength?: number
}

function PasswordInput({ value, onChange, placeholder = '••••••••', required, minLength }: PasswordInputProps) {
    const [show, setShow] = useState(false)

    return (
        <div style={{ position: 'relative' }}>
            <Form.Control
                type={show ? 'text' : 'password'}
                placeholder={placeholder}
                value={value}
                onChange={e => onChange(e.target.value)}
                required={required}
                minLength={minLength}
            />
            <button
                type="button"
                onClick={() => setShow(prev => !prev)}
                style={{
                    position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)',
                    background: 'none', border: 'none', cursor: 'pointer',
                    padding: '2px', display: 'flex', alignItems: 'center'
                }}
                tabIndex={-1}
            >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6c757d" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                    {show && <line x1="1" y1="1" x2="23" y2="23" />}
                </svg>
            </button>
        </div>
    )
}

export default PasswordInput
