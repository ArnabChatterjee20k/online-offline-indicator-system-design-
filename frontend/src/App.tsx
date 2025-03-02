import { createContext, useContext, useState, useEffect, useRef } from "react";
import { io, Socket } from "socket.io-client";

interface User {
  id: string;
  name: string;
  color: string;
  last_seen: string;
}

interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  fooEvents: any[];
  userList: User[];
  error: string | null;
  nameRef: React.RefObject<string>;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

// API URL
const API_URL = "http://localhost:8000/users";

export function SocketProvider({ children }: { children: React.ReactNode }) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [fooEvents, setFooEvents] = useState<any[]>([]);
  const [userList, setUserList] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const nameRef = useRef<string>("");

  useEffect(() => {
    const newSocket = io("http://localhost:8000", {
      autoConnect: false,
    });

    setSocket(newSocket);

    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
    }
    function setOnlineUser(value: string) {
      setFooEvents((prev) => [...prev, value]);
    
      setUserList((users) =>
        users.map((user) =>
          user.name === value ? { ...user, last_seen: "online" } : user
        )
      );
    }
    
    function setOfflineUser(value: string) {
      setFooEvents((prev) => [...prev, value]);
    
      setUserList((users) =>
        users.map((user) =>
          // @ts-ignore
          user.name === value["name"] ? { ...user, last_seen: value["timestamp"] } : user
        )
      );
    }

    newSocket.on("connect", onConnect);
    newSocket.on("disconnect", onDisconnect);
    newSocket.on("online", setOnlineUser);
    newSocket.on("offline", setOfflineUser);

    const interval = setInterval(() => {
      if (newSocket.connected) {
        newSocket.emit("heartbeat", { timestamp: Date.now() });
      }
    }, 300);

    return () => {
      clearInterval(interval);
      newSocket.disconnect();
      newSocket.off("connect", onConnect);
      newSocket.off("disconnect", onDisconnect);
      newSocket.off("online", setOnlineUser);
      newSocket.off("offline", setOfflineUser);
    };
  }, []);

  useEffect(() => {
    async function fetchUsers() {
      if (!nameRef.current) return;
      try {
        const response = await fetch(`${API_URL}?name=${encodeURIComponent(nameRef.current)}`);
        if (!response.ok) throw new Error("Failed to fetch users");
        const data = await response.json();
        setUserList(data);
      } catch (err) {
        setError((err as Error).message);
      }
    }

    fetchUsers();
  }, [nameRef.current]);

  return (
    <SocketContext.Provider value={{ socket, isConnected, fooEvents, userList, error, nameRef }}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error("useSocket must be used within a SocketProvider");
  }
  return context;
}

// Usage inside App.tsx
function App() {
  return (
    <SocketProvider>
      <MainComponent />
    </SocketProvider>
  );
}

function MainComponent() {
  const { isConnected, error, userList, nameRef } = useSocket();

  return (
    <section className="p-7">
      <div className="mb-3">
        <input
          type="text"
          placeholder="Enter your name..."
          defaultValue={nameRef.current}
          onChange={(e) => (nameRef.current = e.target.value)}
          className="border px-2 py-1 rounded"
        />
      </div>

      <ConnectionController />

      {error && <p className="text-red-500">Error: {error}</p>}

      <p className="text-black">{isConnected ? "Connected" : "Disconnected"}</p>

      <h2 className="text-lg font-semibold mt-3">User List</h2>
      <ul className="list-disc pl-4">
        {userList.map((user) => (
          <li key={user.id} style={{ color: user.color }}>
            {user.name} (Last Seen: {user.last_seen})
          </li>
        ))}
      </ul>
    </section>
  );
}

function ConnectionController() {
  const { socket, isConnected, nameRef } = useSocket();

  async function connect() {
    if (!nameRef.current) {
      alert("Please enter your name before connecting.");
      return;
    }
    try {
      const response = await fetch(`${API_URL}?name=${encodeURIComponent(nameRef.current)}`);
      if (!response.ok) throw new Error("Failed to fetch users");
      await response.json();
      if (socket) {
        socket.io.opts.query = { name: nameRef.current };
        socket.connect();
      }
    } catch (err) {
      alert((err as Error).message);
    }
  }

  function disconnect() {
    if (socket) {
      console.log("Disconnecting...");
      socket.disconnect();
    }
  }

  return (
    <div className="flex gap-2 mt-3">
      <button
        onClick={connect}
        disabled={isConnected}
        className="border-2 px-3 py-1 rounded cursor-pointer hover:bg-slate-200 disabled:bg-slate-600"
      >
        Connect
      </button>
      <button
        onClick={disconnect}
        disabled={!isConnected}
        className="border-2 px-3 py-1 rounded cursor-pointer hover:bg-slate-200 disabled:bg-slate-600"
      >
        Disconnect
      </button>
    </div>
  );
}

export default App;
