import { io } from 'socket.io-client'
import config from '@/config'

const socket = io(config.baseURL, {
    transports: [
        'websocket',
        'polling'
    ],
    auth: {
      token: localStorage.getItem('token')
    },
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000
})

export default socket