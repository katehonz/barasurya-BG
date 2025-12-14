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

import { StoresService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddStore from "../../components/Stores/AddStore.tsx"
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx"

const storesSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/stores")({
  component: Stores,
  validateSearch: (search) => storesSearchSchema.parse(search),
})

const PER_PAGE = 5

function getStoresQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      StoresService.readStores({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["stores", { page }],
  }
}

function StoresTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev: {[key: string]: string}) => ({ ...prev, page }) })

  const {
    data: stores,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getStoresQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && stores?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getStoresQueryOptions({ page: page + 1 }))
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
              <Th>Address</Th>
              <Th>Latitude</Th>
              <Th>Longitude</Th>
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
              {stores?.data.map((store) => (
                <Tr key={store.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{store.id}</Td>
                  <Td isTruncated maxWidth="150px">
                    {store.name}
                  </Td>
                  <Td
                    color={!store.address ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {store.address || "N/A"}
                  </Td>
                  <Td
                    color={!store.latitude ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {store.latitude || "N/A"}
                  </Td>
                  <Td
                    color={!store.longitude ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {store.longitude || "N/A"}
                  </Td>
                  <Td>
                    <ActionsMenu type={"Store"} value={store} />
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

function Stores() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Stores Management
      </Heading>

      <Navbar type={"Store"} addModalAs={AddStore} />
      <StoresTable />
    </Container>
  )
}
