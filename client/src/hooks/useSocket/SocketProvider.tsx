import React, { useState, useEffect, useRef } from "react"
import { io } from "socket.io-client"
import { useAppSelector, useAppDispatch } from "../../app/hooks"
import {
  selectUser,
  addPermission,
  removePermission,
} from "../../features/user/userSlice"
import SocketContext from "./SocketContext"
import type { ReactNode } from "react"
import type { Socket } from "socket.io-client"
import type { UserRead, RoleRead, PermissionRead } from "../../api"

type SocketProviderProps = {
  children: ReactNode
}

export type SocketMessage = {
  type:
    | "notification"
    | "error"
    | "user_created"
    | "user_updated"
    | "user_deleted"
    | "role_created"
    | "role_updated"
    | "role_deleted"
    | "role_permission_added"
    | "role_permission_removed"
  payload:
    | UserRead
    | RoleRead
    | PermissionRead
    | string
    | number
    | { role_id: number }
    | { user_id: number }
    | { role: RoleRead; permission: PermissionRead }
    | { message: string }
}

export const SocketProvider = ({ children }: SocketProviderProps) => {
  const dispatch = useAppDispatch()
  const WS_PATH = (import.meta.env.VITE_WS_PATH as string | undefined) ?? "/ws"
  //   const WS_URL = import.meta.env.VITE_WS_URL || window.location.origin;
  const user = useAppSelector(selectUser)
  const socketRef = useRef<Socket | null>(null)
  const [status, setStatus] = useState("disconnected")
  const [message, setMessage] = useState<SocketMessage | null>(null)

  useEffect(() => {
    // console.log("WebSocket Path:", WS_PATH);
    socketRef.current ??= io({
      withCredentials: true,
      autoConnect: true,
      path: WS_PATH,
      transports: ["websocket"],
    })
    if (!user) {
      // console.log("No user found, skipping socket connection.")
      // if (socketRef.current) {
      // console.log("Disconnecting socket due to no user.")
      if (socketRef.current.connected) {
        socketRef.current.disconnect()
      }
      socketRef.current = null
      // }
      return
    }
    const socket = socketRef.current
    // console.log("Socket connected:", socket.connected);
    socket.on("connect", () => {
      setStatus("connected")
      // console.log(`\u001b[32mSocket ID: ${socket.id ?? ""}\u001b[0m`)
      // socket.emit("join", { user: user });
    })
    socket.on("disconnect", () => {
      setStatus("disconnected")
      // console.log(`\u001b[31mSocket disconnected\u001b[0m`)
    })
    socket.on("reconnect_attempt", () => {
      setStatus("reconnecting")
      // console.log(`\u001b[33mSocket reconnect_attempt\u001b[0m`);
    })
    socket.on("msg", (message: SocketMessage) => {
      setMessage(message)
      // console.log(`\u001b[36mMessage received: ${JSON.stringify(message)}\u001b[0m`);
    })

    return () => {
      socket.off("connect")
      socket.off("disconnect")
      socket.off("connect_error")
      socket.off("reconnect_attempt")
      socket.off("msg")
      // socket?.disconnect();
      // socketRef.current = null;
      // console.log(`\u001b[31mSocket disconnected on cleanup\u001b[0m`);
    }
  }, [user, WS_PATH])

  useEffect(() => {
    if (user && socketRef.current) {
      if (message) {
        if (typeof message.payload === "object") {
          if (
            message.type === "role_permission_added" &&
            "role" in message.payload &&
            "permission" in message.payload
          ) {
            if (user.role?.id === message.payload.role.id) {
              const payload = message.payload as {
                role: RoleRead
                permission: PermissionRead
              }
              dispatch(addPermission(payload.permission.name))
            }
          } else if (
            message.type === "role_permission_removed" &&
            "role" in message.payload &&
            "permission" in message.payload
          ) {
            if (user.role?.id === message.payload.role.id) {
              const payload = message.payload as {
                role: RoleRead
                permission: PermissionRead
              }
              dispatch(removePermission(payload.permission.name))
            }
          }
        }
      }
    }
  }, [user, message, dispatch])

  const contextValue = React.useMemo(
    () => ({
      socket: socketRef.current,
      status,
      message,
      setMessage,
    }),
    [status, message],
  )

  return (
    <SocketContext.Provider value={contextValue}>
      {children}
    </SocketContext.Provider>
  )
}

export default SocketProvider
