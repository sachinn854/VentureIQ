import { useRef, useCallback } from 'react'

export function useWebSocket({ onEvent }) {
  const wsRef = useRef(null)

  const connect = useCallback((runId) => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const host = window.location.host
    const ws = new WebSocket(`${protocol}://${host}/ws/${runId}`)

    ws.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data)
        onEvent(event)
      } catch { /* ignore malformed frames */ }
    }

    ws.onerror = () => {
      onEvent({ type: 'error', agent: 'connection', message: 'WebSocket connection failed.' })
    }

    ws.onclose = () => {
      onEvent({ type: 'done' })
    }

    wsRef.current = ws
  }, [onEvent])

  const disconnect = useCallback(() => {
    wsRef.current?.close()
    wsRef.current = null
  }, [])

  return { connect, disconnect }
}
