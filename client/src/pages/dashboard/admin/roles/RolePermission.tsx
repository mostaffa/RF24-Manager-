import React, { useCallback, useEffect, useState } from "react"
import { useGetRolePermissionsQuery } from "../../../../features/user/rolesApiSlice"
import { useGetPermissionsQuery } from "../../../../features/user/permissionApiSlice"
import type { PermissionRead } from "../../../../api"
import { RolesService } from "../../../../api"
import Grid from "@mui/material/Grid"
import Paper from "@mui/material/Paper"
import Typography from "@mui/material/Typography"
import Button from "@mui/material/Button"
import ButtonGroup from "@mui/material/ButtonGroup"
import IconButton from "@mui/material/IconButton"
import FormControl from "@mui/material/FormControl"
import InputLabel from "@mui/material/InputLabel"
import Checkbox from "@mui/material/Checkbox"
import Loader from "../../../../components/ui/loader/Loader"
import ListItemText from "@mui/material/ListItemText"
import Select, { SelectChangeEvent } from "@mui/material/Select"
import MenuItem from "@mui/material/MenuItem"
import useNotifications from "../../../../hooks/useNotifications/useNotifications"
// import { C } from "vitest/dist/chunks/reporters.d.BFLkQcL6.js"
import useSocket from "../../../../hooks/useSocket/useSocket"


const groupPermissionsHelper = (permissions: PermissionRead[]) => {
    const grouped: Record<string, PermissionRead[]> = {}
    permissions.forEach(permission => {
      const [group] = permission.name.split(":")
      if (!grouped[group]) {
        grouped[group] = []
      }
      grouped[group].push(permission)
    })
    return grouped
  }

const RolePermission: React.FC<{ roleId: number }> = ({ roleId }) => {
  const {message} = useSocket()
  const notifications = useNotifications()
  const { data: rolePermissions, isLoading: isRolePermissionsLoading } =
    useGetRolePermissionsQuery(roleId)
  const { data: allPermissions, isLoading: isAllPermissionsLoading } =
    useGetPermissionsQuery(undefined)
  const [groupedPermissions, setGroupedPermissions] = useState<
    Record<string, PermissionRead[]>
  >({})

  const handleChange = useCallback(
    async(event: boolean, permission: PermissionRead) => {
      const permissionId = permission.id
      try {
        if(event) {
          await RolesService.assignPermissionToRoleApiV1RolesRoleIdPermissionsPermissionIdPost({
            roleId: roleId,
            permissionId: permissionId, // Example permission ID to assign, replace with actual logic
           })
        } else {
          await RolesService.removePermissionFromRoleApiV1RolesRoleIdPermissionsPermissionIdDelete({
            roleId: roleId,
            permissionId: permissionId, // Example permission ID to remove, replace with actual logic
           })
        }
    //     if(event.target.checked) {
    //   await RolesService.assignPermissionToRoleApiV1RolesRoleIdPermissionsPermissionIdPost({
    //     roleId: roleId,
    //     permissionId: permissionId, // Example permission ID to assign, replace with actual logic
    //    })
    //     } else {
    //       await RolesService.removePermissionFromRoleApiV1RolesRoleIdPermissionsPermissionIdDelete({
    //         roleId: roleId,
    //         permissionId: permissionId, // Example permission ID to remove, replace with actual logic
    //        })
    //     }
    console.log("event", event)
      console.log("Toggled permission:", permission)
       notifications.show("Permission toggled successfully", {
        severity: "success",
        autoHideDuration: 3000,
      })
        } catch (error) {
            console.error("Error toggling permission:", error)
            notifications.show("Failed to toggle permission", {
                severity: "error",
                autoHideDuration: 5000,
            })
        }
    },
    [roleId, notifications],
  )

   const handleViewPermissions = useCallback(
     (roleId: number) => {
       // Logic to view permissions for the role
       
       console.log("View permissions for role ID:", roleId)
       // You can navigate to a new page or open a dialog to show permissions
     },
     [],
   )

  useEffect(() => {
    if (allPermissions) {
      const grouped = groupPermissionsHelper(allPermissions)
      setGroupedPermissions(grouped)
    }
  }, [allPermissions])

  if (isRolePermissionsLoading || isAllPermissionsLoading) {
    return <Loader />
  }

  return (
    <Grid  maxWidth={"xl"} p={1}>
      <Grid  >
          {/* <Typography variant="h6">Permissions</Typography> */}
        <Grid  sx={{ p: 1 }} container spacing={1}>
            {Object.entries(groupedPermissions).map(([group, permissions]) => (
              <Grid component={Paper} elevation={3} key={group} >
                <Grid size={12} sx={{ mt: 1, p:1 }}>
                    <Typography variant="subtitle1">{group}</Typography>
                </Grid>
                <Grid size={12} container spacing={1} sx={{ pl: 1, pr: 1, pb: 2 }}>
                    {permissions.map(permission => (
                    <Grid key={permission.id}  sx={{ p: 0 }} flexDirection={"row"} display={"flex"} alignItems={"center"} alignContent={"center"} justifyContent={"center"} >
                        <InputLabel id={`permission-${permission.id}-label`}>
                        {permission.name.split(":")[1]} {/* Display action part of permission */}
                        </InputLabel>
                        <Checkbox
                        
                        checked={
                            rolePermissions?.some(
                            rp => rp.id === permission.id,
                            ) || false
                        }
                        onChange={(e) => {
                            void (async () => {
                                await handleChange(e.target.checked, permission)
                                 // Optimistically update UI
                                //  if (e.target.checked) {
                                //     setGroupedPermissions(prev => {
                                //         const updatedRolePermissions = prev[group]?.some(p => p.id === permission.id)
                                //         if (updatedRolePermissions) return prev
                                //         return {
                                //             ...prev,
                                //             [group]: [...(prev[group] || []), permission],
                                //         }
                                //     })
                                //  } else {
                                //     setGroupedPermissions(prev => {
                                //         return {
                                //             ...prev,
                                //             [group]: prev[group]?.filter(p => p.id !== permission.id) || [],
                                //         }
                                //     })
                                //  }
                            })()
                        }}
                        />
                        {/* <ListItemText primary={permission.name} /> */}
                    </Grid>
                    ))}
                </Grid>
              </Grid>
            ))}
        </Grid>
      </Grid>
    </Grid>
  )
}

export default RolePermission