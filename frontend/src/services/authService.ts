import client from './client'

export const login = async (email: string, password: string) => {
    const body = new URLSearchParams()
    body.append('username', email)
    body.append('password', password)

    const response = await client.post('/login/access-token', body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    return response.data
}

export const register = async (
    firstName: string,
    lastName: string,
    email: string,
    password: string
) => {
    const response = await client.post('/users/signup', {
        first_name: firstName,
        last_name: lastName,
        email,
        password
    })
    return response.data
}

export const isAuthenticated = () => {
    return Boolean(localStorage.getItem('token'))
}

export const logout = () => {
    localStorage.removeItem('token')
}