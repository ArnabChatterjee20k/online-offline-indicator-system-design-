import { io } from "socket.io-client";
const URL = import.meta.env.VITE_WS === 'production' ? undefined : 'http://localhost:8000';
export const socket = io(URL);