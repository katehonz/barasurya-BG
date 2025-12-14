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
  Text,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { z } from "zod"

import { StoresService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddStore from "../../components/Stores/AddStore"
import { PaginationFooter } from "../../components/Common/PaginationFooter"

const storesSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/stores")({
  component: Stores,
  validateSearch: (search) => storesSearchSchema.parse(search),
})

const PER_PAGE = 10

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
    navigate({ search: (prev: { [key: string]: string }) => ({ ...prev, page }) })

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
              <Th>Наименование</Th>
              <Th>Адрес</Th>
              <Th>Действия</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(3).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {stores?.data.length === 0 ? (
                <Tr>
                  <Td colSpan={3}>
                    <Text textAlign="center" py={4} color="gray.500">
                      Няма намерени складове
                    </Text>
                  </Td>
                </Tr>
              ) : (
                stores?.data.map((store) => (
                  <Tr key={store.id} opacity={isPlaceholderData ? 0.5 : 1}>
                    <Td>
                      <Text fontWeight="medium">{store.name}</Text>
                    </Td>
                    <Td>
                      <Text color={!store.address ? "gray.400" : "inherit"}>
                        {store.address || "-"}
                      </Text>
                    </Td>
                    <Td>
                      <ActionsMenu type={"Store"} value={store} />
                    </Td>
                  </Tr>
                ))
              )}
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
        Складове
      </Heading>

      <Navbar type={"Store"} addModalAs={AddStore} />
      <StoresTable />
    </Container>
  )
}
