import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState, useCallback } from "react"

import type { ApiError, OrganizationCreate } from "../client"
import { OrganizationsService } from "../client"
import useCustomToast from "./useCustomToast"

const useOrganization = () => {
  const showToast = useCustomToast()
  const queryClient = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)

  // Fetch all organizations the user belongs to
  const {
    data: organizationsData,
    isLoading: isLoadingOrganizations,
    error: organizationsError,
  } = useQuery({
    queryKey: ["organizations"],
    queryFn: () => OrganizationsService.readOrganizations(),
    enabled: !!localStorage.getItem("access_token"),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const organizations = organizationsData?.data || []

  // Get current organization from user data
  const currentUser = queryClient.getQueryData<any>(["currentUser"])
  const currentOrganizationId = currentUser?.current_organization_id

  const currentOrganization = organizations.find(
    (org) => org.id === currentOrganizationId
  )

  // Switch organization mutation
  const switchMutation = useMutation({
    mutationFn: (organizationId: string) =>
      OrganizationsService.switchOrganization({ id: organizationId }),
    onSuccess: (data) => {
      // Invalidate all queries to refresh data for new organization
      queryClient.invalidateQueries()
      showToast(
        "Организация сменена",
        `Превключихте към ${data.name}`,
        "success"
      )
    },
    onError: (_error: ApiError) => {
      showToast(
        "Грешка",
        "Неуспешна смяна на организация",
        "error"
      )
    },
  })

  // Create organization mutation
  const createMutation = useMutation({
    mutationFn: (data: OrganizationCreate) =>
      OrganizationsService.createOrganization({ requestBody: data }),
    onMutate: () => {
      setIsCreating(true)
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["organizations"] })
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      showToast(
        "Организация създадена",
        `${data.name} е създадена успешно`,
        "success"
      )
    },
    onError: (_error: ApiError) => {
      showToast(
        "Грешка",
        "Неуспешно създаване на организация",
        "error"
      )
    },
    onSettled: () => {
      setIsCreating(false)
    },
  })

  // Helper to switch organization
  const switchTo = useCallback((organizationId: string) => {
    if (organizationId !== currentOrganizationId) {
      switchMutation.mutate(organizationId)
    }
  }, [currentOrganizationId, switchMutation])

  // Helper to create organization
  const create = useCallback((data: OrganizationCreate) => {
    createMutation.mutate(data)
  }, [createMutation])

  return {
    // Data
    organizations,
    currentOrganization,
    currentOrganizationId,

    // Loading states
    isLoadingOrganizations,
    isSwitching: switchMutation.isPending,
    isCreating,

    // Errors
    organizationsError,

    // Actions
    switchTo,
    create,

    // Check if user has organizations
    hasOrganizations: organizations.length > 0,
    needsOrganization: !isLoadingOrganizations && !currentOrganizationId,
  }
}

export default useOrganization
