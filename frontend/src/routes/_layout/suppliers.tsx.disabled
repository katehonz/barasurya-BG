import {
  Container,
  Heading,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { z } from "zod"

import { SuppliersService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddSupplier from "../../components/Suppliers/AddSupplier.tsx"
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx"

const suppliersSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/suppliers")({
  component: Suppliers,
  validateSearch: (search) => suppliersSearchSchema.parse(search),
})

const PER_PAGE = 5

function getSuppliersQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      SuppliersService.readSuppliers({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["suppliers", { page }],
  }
}

function SuppliersTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev: {[key: string]: string}) => ({ ...prev, page }) })

  const {
    data: suppliers,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getSuppliersQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && suppliers?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getSuppliersQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>ID</Th>
              <Th>Name</Th>
              <Th>Phone</Th>
              <Th>Address</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(4).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {suppliers?.data.map((supplier) => (
                <Tr key={supplier.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{supplier.id}</Td>
                  <Td isTruncated maxWidth="150px">
                    {supplier.name}
                  </Td>
                  <Td
                    color={!supplier.phone ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {supplier.phone || "N/A"}
                  </Td>
                  <Td
                    color={!supplier.address ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {supplier.address || "N/A"}
                  </Td>
                  <Td>
                    <ActionsMenu type={"Supplier"} value={supplier} />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      <PaginationFooter
        page={page}
        onChangePage={setPage}
        hasNextPage={hasNextPage}
        hasPreviousPage={hasPreviousPage}
      />
    </>
  )
}

function Suppliers() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Suppliers Management
      </Heading>

      <Navbar type={"Supplier"} addModalAs={AddSupplier} />
      <SuppliersTable />
    </Container>
  )
}
