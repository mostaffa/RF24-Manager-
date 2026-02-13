import React, { useCallback, useEffect } from "react"
import Container from "@mui/material/Container"
import Grid from "@mui/material/Grid"
import Paper from "@mui/material/Paper"
import Typography from "@mui/material/Typography"
import { useAppDispatch } from "../../../../app/hooks"
import { useGetPermissionsQuery } from "../../../../features/user/permissionApiSlice"
import { permissionApiSlice } from "../../../../features/user/permissionApiSlice"

export default function Permissions() {
  const dispatch = useAppDispatch()
  const { data: permissions, error, isLoading, refetch } = useGetPermissionsQuery(undefined )

  const handleRefresh = useCallback(() => {
    refetch()
  }, [refetch])

  useEffect(() => {
    // Refetch permissions when the component mounts
    refetch()
  }, [refetch])

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid size={12}>
          <Paper sx={{ p: 2, display: "flex", flexDirection: "column" }}>
            <Typography variant="h6" gutterBottom>
              Permissions
            </Typography>
            {isLoading && <Typography>Loading permissions...</Typography>}
            {error && (
              <Typography color="error">
                Error loading permissions: {String(error)}
              </Typography>
            )}
            {permissions && (
              <ul>
                {permissions.map(permission => (
                  <li key={permission.id}>{permission.name}</li>
                ))}
              </ul>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  )
}

