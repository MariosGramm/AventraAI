import { createContext, useContext, useState, useEffect } from 'react'
import client from '../services/client'

interface User {
    id: string
    email: string
    first_name: string
    last_name: string
    subscription_tier: 'free' | 'paid'
    monthly_searches_used: number
    subscription_cancel_at_period_end: boolean
    subscription_current_period_end: string | null
}

interface AuthContextType {
    user: User | null
    setUser: (user: User | null) => void
    logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)

    useEffect(() => {
        const token = localStorage.getItem('token')
        if (token) {
            client.get('/users/me')
                .then(res => setUser(res.data))
                .catch(() => {
                    localStorage.removeItem('token')
                    setUser(null)
                })
        }
    }, [])

    const logout = () => {
        localStorage.removeItem('token')
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, setUser, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuthContext() {
    const context = useContext(AuthContext)
    if (!context) throw new Error('useAuthContext must be used within AuthProvider')
    return context
}