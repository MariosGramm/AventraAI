import client from '../services/client'

interface TravelPackage {
    id: string
    tier: string
    estimated_cost_min: number
    estimated_cost_max: number
    currency: string
    transportation: string | null
    flight_info: string | null
    travel_tips: string[] | null
    weather_summary: string | null
    itinerary: {
        id: string
        day_number: number
        description: string
        estimated_daily_cost: number | null
        activities: {
            id: string
            type: string
            title: string
            estimated_cost: number | null
            average_duration_hours: number | null
            part_of_day: string
        }[]
    }[]
    accommodations: {
        id: string
        name: string
        type: string
        area: string | null
        cost_per_night: number | null
        rating: number | null
    }[]
}

interface TravelPackageCardProps {
    pkg: TravelPackage
    searchSessionId: string
    destination: string
    dateFrom?: string
    dateTo?: string
}

function TravelPackageCard({ pkg, searchSessionId, destination, dateFrom, dateTo }: TravelPackageCardProps) {
    const tierColors: Record<string, string> = {
        budget: '#28a745',
        standard: '#7F77DD',
        mid: '#7F77DD',
        luxury: '#d4a017',
    }

    const handleDownloadPdf = async () => {
        try {
            const response = await client.get(`/travel/searches/${searchSessionId}/pdf`, {
                responseType: 'blob'
            })
            const url = window.URL.createObjectURL(new Blob([response.data]))
            const link = document.createElement('a')
            link.href = url
            link.download = `${destination.replace(/\s+/g, '_')}_itinerary.pdf`
            link.click()
            window.URL.revokeObjectURL(url)
        } catch {
            alert('Failed to generate PDF')
        }
    }

    return (
        <div style={{
            background: 'white', border: '1px solid #e8e6f0', borderRadius: '16px',
            padding: '20px', maxWidth: '620px', width: '100%'
        }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div>
                    <span style={{
                        display: 'inline-block', padding: '3px 10px', borderRadius: '99px',
                        fontSize: '11px', fontWeight: 600, textTransform: 'uppercase',
                        background: `${tierColors[pkg.tier] || '#7F77DD'}15`,
                        color: tierColors[pkg.tier] || '#7F77DD'
                    }}>
                        {pkg.tier}
                    </span>
                    <div style={{ fontSize: '14px', fontWeight: 600, color: '#26215C', marginTop: '4px' }}>
                        {destination}
                    </div>
                    {dateFrom && dateTo && (
                        <div style={{ fontSize: '11px', color: '#6c757d', marginTop: '2px' }}>
                            {new Date(dateFrom).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} → {new Date(dateTo).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                        </div>
                    )}
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#26215C' }}>
                        {pkg.estimated_cost_min}–{pkg.estimated_cost_max} {pkg.currency}
                    </div>
                    <div style={{ fontSize: '11px', color: '#aaa' }}>estimated total</div>
                </div>
            </div>

            {/* Weather */}
            {pkg.weather_summary && (
                <div style={{ padding: '10px 14px', background: '#f8f8ff', borderRadius: '10px', fontSize: '13px', color: '#534AB7', marginBottom: '14px' }}>
                    ☀ {pkg.weather_summary}
                </div>
            )}

            {/* Itinerary */}
            <div style={{ marginBottom: '14px' }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#26215C', marginBottom: '8px' }}>Itinerary</div>
                {pkg.itinerary.map(day => (
                    <div key={day.id} style={{ marginBottom: '10px', paddingLeft: '12px', borderLeft: '2px solid #EEEDFE' }}>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: '#534AB7' }}>Day {day.day_number}</div>
                        <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>{day.description}</div>
                        {day.activities.map(act => (
                            <div key={act.id} style={{ fontSize: '12px', color: '#26215C', padding: '2px 0', display: 'flex', gap: '6px' }}>
                                <span style={{ color: '#aaa' }}>
                                    {act.part_of_day === 'morning' ? '🌅' : act.part_of_day === 'afternoon' ? '☀️' : '🌙'}
                                </span>
                                {act.title}
                            </div>
                        ))}
                    </div>
                ))}
            </div>

            {/* Accommodation link */}
            {pkg.booking_info && (() => {
                const url = pkg.booking_info.match(/https?:\/\/[^\s]+/)?.[0]
                return url ? (
                    <div style={{ fontSize: '12px', marginBottom: '8px' }}>
                        <a href={url} target="_blank" rel="noopener noreferrer"
                           style={{ color: '#534AB7', textDecoration: 'none', fontWeight: 500 }}
                           onMouseEnter={e => e.currentTarget.style.textDecoration = 'underline'}
                           onMouseLeave={e => e.currentTarget.style.textDecoration = 'none'}
                        >Browse available hotels →</a>
                    </div>
                ) : null
            })()}

            {/* Transportation */}
            {pkg.transportation && (
                <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '8px' }}>
                    <strong>Transportation:</strong> {pkg.transportation}
                </div>
            )}

            {/* Flight info */}
            {pkg.flight_info && (() => {
                const url = pkg.flight_info.match(/https?:\/\/[^\s]+/)?.[0]
                return url ? (
                    <div style={{ fontSize: '12px', marginBottom: '8px' }}>
                        <a href={url} target="_blank" rel="noopener noreferrer"
                           style={{ color: '#534AB7', textDecoration: 'none', fontWeight: 500 }}
                           onMouseEnter={e => e.currentTarget.style.textDecoration = 'underline'}
                           onMouseLeave={e => e.currentTarget.style.textDecoration = 'none'}
                        >Browse available flights →</a>
                    </div>
                ) : null
            })()}

            {/* Tips */}
            {pkg.travel_tips && pkg.travel_tips.length > 0 && (
                <div style={{ marginBottom: '14px' }}>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#26215C', marginBottom: '4px' }}>Tips</div>
                    {pkg.travel_tips.map((tip, i) => (
                        <div key={i} style={{ fontSize: '12px', color: '#6c757d', padding: '2px 0' }}>• {tip}</div>
                    ))}
                </div>
            )}

            {/* PDF Button */}
            <button onClick={handleDownloadPdf} style={{
                width: '100%', padding: '10px', borderRadius: '10px',
                background: '#f8f8ff', border: '1px solid #e8e6f0',
                color: '#534AB7', fontSize: '13px', fontWeight: 500,
                cursor: 'pointer', display: 'flex', alignItems: 'center',
                justifyContent: 'center', gap: '6px', transition: 'background 0.2s'
            }}
            onMouseEnter={e => e.currentTarget.style.background = '#EEEDFE'}
            onMouseLeave={e => e.currentTarget.style.background = '#f8f8ff'}
            >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#534AB7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Download PDF
            </button>
        </div>
    )
}

export default TravelPackageCard
