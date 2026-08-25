import { useCallback, useEffect, useRef, useState } from 'react'

interface SpeechRecognitionAlternativeLike {
    transcript: string
}

interface SpeechRecognitionResultLike {
    isFinal: boolean
    length: number
    [index: number]: SpeechRecognitionAlternativeLike
}

interface SpeechRecognitionEventLike extends Event {
    results: ArrayLike<SpeechRecognitionResultLike>
}

interface SpeechRecognitionLike extends EventTarget {
    lang: string
    continuous: boolean
    interimResults: boolean
    start: () => void
    stop: () => void
    onresult: ((event: SpeechRecognitionEventLike) => void) | null
    onerror: (() => void) | null
    onend: (() => void) | null
}

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike

function getSpeechRecognitionConstructor(): SpeechRecognitionConstructor | null {
    const w = window as unknown as {
        SpeechRecognition?: SpeechRecognitionConstructor
        webkitSpeechRecognition?: SpeechRecognitionConstructor
    }
    return w.SpeechRecognition || w.webkitSpeechRecognition || null
}

export function useSpeechRecognition(onTranscript: (text: string) => void) {
    const [isRecording, setIsRecording] = useState(false)
    const [isSupported] = useState(() => getSpeechRecognitionConstructor() !== null)
    const recognitionRef = useRef<SpeechRecognitionLike | null>(null)
    const transcriptRef = useRef('')

    useEffect(() => () => recognitionRef.current?.stop(), [])

    const toggleRecording = useCallback(() => {
        if (isRecording) {
            recognitionRef.current?.stop()
            return
        }

        const SpeechRecognitionCtor = getSpeechRecognitionConstructor()
        if (!SpeechRecognitionCtor) return

        const recognition = new SpeechRecognitionCtor()
        recognition.lang = 'en-US'
        recognition.continuous = true
        recognition.interimResults = false

        transcriptRef.current = ''

        recognition.onresult = (event) => {
            let finalText = ''
            for (let i = 0; i < event.results.length; i++) {
                const result = event.results[i]
                if (result.isFinal) finalText += result[0].transcript
            }
            transcriptRef.current = finalText
        }

        recognition.onerror = () => setIsRecording(false)

        recognition.onend = () => {
            setIsRecording(false)
            if (transcriptRef.current.trim()) onTranscript(transcriptRef.current.trim())
        }

        recognitionRef.current = recognition
        recognition.start()
        setIsRecording(true)
    }, [isRecording, onTranscript])

    return { isRecording, isSupported, toggleRecording }
}
