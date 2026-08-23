import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, register } from '../services/authService'
import { useAuthContext } from "../context/AuthContext.tsx"
import client from "../services/client.ts"

export function useAuth() {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const navigate = useNavigate()
    const { setUser } = useAuthContext()

    const handleLogin = async (email: string, password: string) => {
        setLoading(true)
        setError('')
        try {
            const data = await login(email, password)
            localStorage.setItem('token', data.access_token)
            const userResponse = await client.get('/users/me')
            setUser(userResponse.data)
            navigate('/chat')
        } catch (err) {
            setError('Invalid email or password')
        } finally {
            setLoading(false)
        }
    }

    const handleRegister = async (
        firstName: string,
        lastName: string,
        email: string,
        password: string
    ) => {
        setLoading(true)
        setError('')
        try {
            await register(firstName, lastName, email, password)
            const data = await login(email, password)
            localStorage.setItem('token', data.access_token)
            const userResponse = await client.get('/users/me')
            setUser(userResponse.data)
            navigate('/register-success')
        } catch (err) {
            setError('Something went wrong. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return { handleLogin, handleRegister, loading, error }
}