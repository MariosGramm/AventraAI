import { useState } from 'react'

interface SearchFormProps {
    onSubmit: (data: SearchFormData) => void
    onClose: () => void
    loading: boolean
}

export interface SearchFormData {
    destination: string
    origin?: string
    date_from: string
    date_to: string
    budget?: number
    currency: string
    adults: number
    children: number
    trip_type?: string
}

function SearchForm({ onSubmit, onClose, loading }: SearchFormProps) {
    const [destination, setDestination] = useState('')
    const [origin, setOrigin] = useState('')
    const [dateFrom, setDateFrom] = useState('')
    const [dateTo, setDateTo] = useState('')
    const [budget, setBudget] = useState<'budget' | 'standard' | 'luxury' | ''>('')
    const [currency, setCurrency] = useState('EUR')
    const [adults, setAdults] = useState(2)
    const [children, setChildren] = useState(0)
    const [tripType, setTripType] = useState('')

    const handleSubmit = () => {
        if (!destination.trim() || !dateFrom || !dateTo) return
        const budgetMap = { budget: 500, standard: 1500, luxury: 4000 }
        onSubmit({
            destination: destination.trim(),
            origin: origin.trim() || undefined,
            date_from: new Date(dateFrom).toISOString(),
            date_to: new Date(dateTo).toISOString(),
            budget: budget ? budgetMap[budget] : undefined,
            currency,
            adults,
            children,
            trip_type: tripType || undefined,
        })
    }

    const inputStyle = {
        width: '100%', padding: '8px 12px', borderRadius: '8px',
        border: '1px solid #e0e0e0', fontSize: '13px', fontFamily: 'inherit',
        outline: 'none', boxSizing: 'border-box' as const
    }

    const labelStyle = { fontSize: '12px', color: '#6c757d', marginBottom: '4px', display: 'block' }

    return (
        <div style={{
            background: 'white', border: '1px solid #e8e6f0', borderRadius: '16px',
            padding: '20px', maxWidth: '680px', width: '100%', margin: '0 auto',
            boxShadow: '0 4px 24px rgba(127,119,221,0.1)',
            animation: 'fadeSlideUp 0.3s ease-out'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#26215C', margin: 0 }}>
                    Generate Travel Package
                </h3>
                <button onClick={onClose} style={{
                    background: 'none', border: 'none', cursor: 'pointer', fontSize: '18px', color: '#aaa', padding: '4px'
                }}>×</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ gridColumn: '1 / -1' }}>
                    <label style={labelStyle}>Destination *</label>
                    <input value={destination} onChange={e => setDestination(e.target.value)} placeholder="e.g. Prague, Tokyo, Paris" style={inputStyle} />
                </div>

                <div style={{ gridColumn: '1 / -1' }}>
                    <label style={labelStyle}>Departing from</label>
                    <input value={origin} onChange={e => setOrigin(e.target.value)} placeholder="e.g. Athens (optional)" style={inputStyle} />
                </div>

                <div>
                    <label style={labelStyle}>From *</label>
                    <input type="date" value={dateFrom} onChange={e => { setDateFrom(e.target.value); if (dateTo && e.target.value > dateTo) setDateTo('') }} min={new Date().toISOString().slice(0, 10)} style={inputStyle} />
                </div>
                <div>
                    <label style={labelStyle}>To *</label>
                    <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} min={dateFrom || new Date().toISOString().slice(0, 10)} max={dateFrom ? new Date(new Date(dateFrom).getTime() + 19 * 86400000).toISOString().slice(0, 10) : undefined} style={inputStyle} />
                </div>
                <div style={{ gridColumn: '1 / -1', fontSize: '11px', color: '#aaa', fontStyle: 'italic', marginTop: '-4px' }}>
                    * Itineraries can be generated for trips up to 20 days
                </div>

                <div style={{ gridColumn: '1 / -1' }}>
                    <label style={labelStyle}>Budget tier</label>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        {[
                            { value: 'budget' as const, label: 'Budget', range: '< 500€' },
                            { value: 'standard' as const, label: 'Standard', range: '500–2000€' },
                            { value: 'luxury' as const, label: 'Luxury', range: '2000€+' },
                        ].map(opt => (
                            <button key={opt.value} type="button" onClick={() => setBudget(budget === opt.value ? '' : opt.value)} style={{
                                flex: 1, padding: '10px', borderRadius: '8px', fontSize: '13px',
                                border: budget === opt.value ? '1.5px solid #7F77DD' : '1px solid #e0e0e0',
                                background: budget === opt.value ? '#f8f6ff' : 'white',
                                color: budget === opt.value ? '#534AB7' : '#6c757d',
                                cursor: 'pointer', transition: 'all 0.15s', textAlign: 'center'
                            }}>
                                <div style={{ fontWeight: 600 }}>{opt.label}</div>
                                <div style={{ fontSize: '12px', opacity: 0.7 }}>{opt.range}</div>
                            </button>
                        ))}
                    </div>
                </div>
                <div>
                    <label style={labelStyle}>Currency</label>
                    <select value={currency} onChange={e => setCurrency(e.target.value)} style={inputStyle}>
                        <option value="EUR">EUR</option>
                        <option value="USD">USD</option>
                        <option value="GBP">GBP</option>
                        <option value="JPY">JPY</option>
                        <option value="CHF">CHF</option>
                    </select>
                </div>

                <div>
                    <label style={labelStyle}>Adults</label>
                    <input type="number" min={1} max={20} value={adults} onChange={e => setAdults(parseInt(e.target.value) || 1)} style={inputStyle} />
                </div>
                <div>
                    <label style={labelStyle}>Children</label>
                    <input type="number" min={0} max={10} value={children} onChange={e => setChildren(parseInt(e.target.value) || 0)} style={inputStyle} />
                </div>

                <div style={{ gridColumn: '1 / -1' }}>
                    <label style={labelStyle}>Trip type</label>
                    <select value={tripType} onChange={e => setTripType(e.target.value)} style={inputStyle}>
                        <option value="">Any</option>
                        <option value="solo">Solo</option>
                        <option value="family">Family</option>
                        <option value="romantic">Romantic</option>
                        <option value="friends">Friends</option>
                    </select>
                </div>
            </div>

            <button
                onClick={handleSubmit}
                disabled={loading || !destination.trim() || !dateFrom || !dateTo}
                style={{
                    width: '100%', marginTop: '16px', padding: '10px',
                    background: destination.trim() && dateFrom && dateTo ? '#7F77DD' : '#e0e0e0',
                    color: 'white', border: 'none', borderRadius: '10px',
                    fontSize: '14px', fontWeight: 500, cursor: destination.trim() && dateFrom && dateTo ? 'pointer' : 'default',
                    transition: 'background 0.2s'
                }}
            >
                {loading ? 'Generating...' : 'Generate Itinerary'}
            </button>

            <style>{`
                @keyframes fadeSlideUp {
                    from { opacity: 0; transform: translateY(12px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            `}</style>
        </div>
    )
}

export default SearchForm
