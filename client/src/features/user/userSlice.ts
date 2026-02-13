import type { PayloadAction } from "@reduxjs/toolkit"
import { createAppSlice } from "../../app/createAppSlice"
import type { UserOut } from "../../api"

type UserState = {
  user: UserOut | null
}

const initialState: UserState = {
  user: null,
}

export const userSlice = createAppSlice({
  name: "user",
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<UserOut | null>) => {
      state.user = action.payload
    },
    clearUser: state => {
      state.user = null
    },
  },
  selectors: {
    selectUser: state => state.user?.user,
  },
})

export const { setUser, clearUser } = userSlice.actions
export const { selectUser } = userSlice.selectors

export default userSlice.reducer
