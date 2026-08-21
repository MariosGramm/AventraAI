import client from './client'

export const login = async (email: string, password: string) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await client.post('/login/access-token', formData, {
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