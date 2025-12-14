import { useState } from "react"
import {
  Box,
  Button,
  Container,
  Flex,
  Heading,
  HStack,
  Input,
  Select,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useColorModeValue,
  useDisclosure,
  VStack,
  Badge,
  IconButton,
  Tooltip,
  Alert,
  AlertIcon,
  Spinner,
} from "@chakra-ui/react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { FiPlus, FiEdit, FiTrash2, FiRefreshCw } from "react-icons/fi"

import AddContraagent from "../../components/Contraagents/AddContraagent"
import EditContraagent from "../../components/Contraagents/EditContraagent"
import type { ContraagentPublic } from "../../client"
import { ContraagentsService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

export const Route = createFileRoute("/_layout/contraagents")({
  component: Contraagents,
})

function Contraagents() {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    isOpen: isAddOpen,
    onOpen: onAddOpen,
    onClose: onAddClose,
  } = useDisclosure()
  const {
    isOpen: isEditOpen,
    onOpen: onEditOpen,
    onClose: onEditClose,
  } = useDisclosure()
  const [selectedContraagent, setSelectedContraagent] = useState<ContraagentPublic | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [filterCustomer, setFilterCustomer] = useState<string>("all")
  const [filterSupplier, setFilterSupplier] = useState<string>("all")
  const [filterActive, setFilterActive] = useState<string>("all")
  const [currentPage, setCurrentPage] = useState(0)
  const itemsPerPage = 20

  // Fetch contraagents
  const {
    data: contraagentsData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["contraagents", currentPage, searchTerm, filterCustomer, filterSupplier, filterActive],
    queryFn: () =>
      ContraagentsService.readContraagents({
        skip: currentPage * itemsPerPage,
        limit: itemsPerPage,
        search: searchTerm || undefined,
        isCustomer: filterCustomer === "all" ? undefined : filterCustomer === "true",
        isSupplier: filterSupplier === "all" ? undefined : filterSupplier === "true",
        isActive: filterActive === "all" ? undefined : filterActive === "true",
      }),
  })

  // Delete contraagent mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      ContraagentsService.deleteContraagent({ id }),
    onSuccess: () => {
      showToast("Success!", "Contraagent deleted successfully.", "success")
      queryClient.invalidateQueries({ queryKey: ["contraagents"] })
    },
    onError: (err: any) => {
      handleError(err, showToast)
    },
  })

  const handleEdit = (contraagent: ContraagentPublic) => {
    setSelectedContraagent(contraagent)
    onEditOpen()
  }

  const handleDelete = (id: string) => {
    if (window.confirm("Are you sure you want to delete this contraagent?")) {
      deleteMutation.mutate(id)
    }
  }

  const handleSearch = (value: string) => {
    setSearchTerm(value)
    setCurrentPage(0) // Reset to first page on search
  }

  const handleFilterChange = (filterType: string, value: string) => {
    switch (filterType) {
      case "customer":
        setFilterCustomer(value)
        break
      case "supplier":
        setFilterSupplier(value)
        break
      case "active":
        setFilterActive(value)
        break
    }
    setCurrentPage(0) // Reset to first page on filter change
  }

  const totalPages = contraagentsData ? Math.ceil(contraagentsData.count / itemsPerPage) : 0

  const tableBg = useColorModeValue("white", "gray.800")
  const headerBg = useColorModeValue("gray.50", "gray.700")

  if (error) {
    return (
      <Container maxW="full">
        <Alert status="error">
          <AlertIcon />
          Failed to load contraagents. Please try again.
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxW="full">
      <Box
        bg={tableBg}
        rounded="md"
        shadow="base"
        w="full"
        p={6}
        mb={6}
      >
        <Flex justify="space-between" align="center" mb={6}>
          <Heading size="lg">Contraagents</Heading>
          <HStack>
            <Button
              leftIcon={<FiRefreshCw />}
              onClick={() => refetch()}
              isLoading={isLoading}
              variant="outline"
            >
              Refresh
            </Button>
            <Button
              leftIcon={<FiPlus />}
              onClick={onAddOpen}
              colorScheme="teal"
            >
              Add Contraagent
            </Button>
          </HStack>
        </Flex>

        {/* Search and Filters */}
        <VStack spacing={4} mb={6} align="stretch">
          <Input
            placeholder="Search by name, VAT number, registration number, or email..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            size="md"
          />
          
          <HStack spacing={4}>
            <Select
              value={filterCustomer}
              onChange={(e) => handleFilterChange("customer", e.target.value)}
              placeholder="Filter by Customer"
              w="200px"
            >
              <option value="all">All</option>
              <option value="true">Customers Only</option>
              <option value="false">Non-Customers</option>
            </Select>

            <Select
              value={filterSupplier}
              onChange={(e) => handleFilterChange("supplier", e.target.value)}
              placeholder="Filter by Supplier"
              w="200px"
            >
              <option value="all">All</option>
              <option value="true">Suppliers Only</option>
              <option value="false">Non-Suppliers</option>
            </Select>

            <Select
              value={filterActive}
              onChange={(e) => handleFilterChange("active", e.target.value)}
              placeholder="Filter by Status"
              w="200px"
            >
              <option value="all">All</option>
              <option value="true">Active Only</option>
              <option value="false">Inactive Only</option>
            </Select>
          </HStack>
        </VStack>

        {/* Results Summary */}
        {contraagentsData && (
          <Text mb={4} color="gray.600">
            Showing {contraagentsData.data.length} of {contraagentsData.count} contraagents
          </Text>
        )}

        {/* Table */}
        {isLoading ? (
          <Flex justify="center" py={8}>
            <Spinner size="xl" />
          </Flex>
        ) : (
          <Box overflowX="auto">
            <Table variant="simple">
              <Thead bg={headerBg}>
                <Tr>
                  <Th>Name</Th>
                  <Th>Type</Th>
                  <Th>VAT Number</Th>
                  <Th>Registration</Th>
                  <Th>Email</Th>
                  <Th>Phone</Th>
                  <Th>City</Th>
                  <Th>Status</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {contraagentsData?.data?.map((contraagent) => (
                  <Tr key={contraagent.id}>
                    <Td>
                      <VStack align="start" spacing={0}>
                        <Text fontWeight="medium">{contraagent.name}</Text>
                        {contraagent.website && (
                          <Text fontSize="sm" color="gray.500">
                            {contraagent.website}
                          </Text>
                        )}
                      </VStack>
                    </Td>
                    <Td>
                      <HStack spacing={1}>
                        {contraagent.is_customer && (
                          <Badge colorScheme="blue" size="sm">Customer</Badge>
                        )}
                        {contraagent.is_supplier && (
                          <Badge colorScheme="green" size="sm">Supplier</Badge>
                        )}
                        {contraagent.is_company && (
                          <Badge colorScheme="gray" size="sm">Company</Badge>
                        )}
                      </HStack>
                    </Td>
                    <Td>
                      <Text fontFamily="mono" fontSize="sm">
                        {contraagent.vat_number || "-"}
                      </Text>
                    </Td>
                    <Td>
                      <Text fontFamily="mono" fontSize="sm">
                        {contraagent.registration_number || "-"}
                      </Text>
                    </Td>
                    <Td>
                      <Text fontSize="sm">{contraagent.email || "-"}</Text>
                    </Td>
                    <Td>
                      <Text fontSize="sm">{contraagent.phone || "-"}</Text>
                    </Td>
                    <Td>
                      <Text fontSize="sm">{contraagent.city || "-"}</Text>
                    </Td>
                    <Td>
                      <Badge
                        colorScheme={contraagent.is_active ? "green" : "red"}
                        size="sm"
                      >
                        {contraagent.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </Td>
                    <Td>
                      <HStack spacing={2}>
                        <Tooltip label="Edit">
                          <IconButton
                            aria-label="Edit"
                            icon={<FiEdit />}
                            size="sm"
                            variant="ghost"
                            colorScheme="blue"
                            onClick={() => handleEdit(contraagent)}
                          />
                        </Tooltip>
                        <Tooltip label="Delete">
                          <IconButton
                            aria-label="Delete"
                            icon={<FiTrash2 />}
                            size="sm"
                            variant="ghost"
                            colorScheme="red"
                            onClick={() => handleDelete(contraagent.id)}
                            isLoading={deleteMutation.isPending}
                          />
                        </Tooltip>
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>

            {/* Pagination */}
            {totalPages > 1 && (
              <Flex justify="center" mt={6} gap={2}>
                <Button
                  onClick={() => setCurrentPage((prev) => Math.max(0, prev - 1))}
                  isDisabled={currentPage === 0}
                  variant="outline"
                >
                  Previous
                </Button>
                <Text alignSelf="center">
                  Page {currentPage + 1} of {totalPages}
                </Text>
                <Button
                  onClick={() => setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1))}
                  isDisabled={currentPage === totalPages - 1}
                  variant="outline"
                >
                  Next
                </Button>
              </Flex>
            )}
          </Box>
        )}
      </Box>

      {/* Add Modal */}
      <AddContraagent isOpen={isAddOpen} onClose={onAddClose} />

      {/* Edit Modal */}
      {selectedContraagent && (
        <EditContraagent
          isOpen={isEditOpen}
          onClose={onEditClose}
          contraagent={selectedContraagent}
        />
      )}
    </Container>
  )
}