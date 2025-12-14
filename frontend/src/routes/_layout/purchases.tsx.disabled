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

import { PurchasesService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddPurchase from "../../components/Purchases/AddPurchase"
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx"

const purchasesSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/purchases")({
  component: Purchases,
  validateSearch: (search) => purchasesSearchSchema.parse(search),
})

const PER_PAGE = 5

function getPurchasesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      PurchasesService.readPurchases({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["purchases", { page }],
  }
}

function PurchasesTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev: {[key: string]: string}) => ({ ...prev, page }) })

  const {
    data: purchases,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getPurchasesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  // debug
  useEffect(() => {
    console.log("Purchases:", purchases)
  }, [purchases])

  const hasNextPage = !isPlaceholderData && purchases?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getPurchasesQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>ID</Th>
              <Th>Date Purchase</Th>
              <Th>Amount</Th>
              <Th>Description</Th>
              <Th>Supplier Name</Th>
              <Th>Store Name</Th>
              <Th>Date Created</Th>
              <Th>Date Updated</Th>
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
              {purchases?.data.map((purchase) => (
                <Tr key={purchase.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{purchase.id}</Td>
                  <Td
                    color={!purchase.date_purchase ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {purchase.date_purchase || "N/A"}
                  </Td>
                  <Td
                    color={!purchase.amount ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {purchase.amount || "N/A"}
                  </Td>
                  <Td
                    color={!purchase.description ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {purchase.description || "N/A"}
                  </Td>
                  <Td
                    color={!purchase.supplier_name ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {purchase.supplier_name || "N/A"}
                  </Td>
                  <Td
                    color={!purchase.store_name ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {purchase.store_name || "N/A"}
                  </Td>
                  <Td
                    color={!purchase.date_created ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {purchase.date_created || "N/A"}
                  </Td>
                  <Td
                    color={!purchase.date_updated ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {purchase.date_updated || "N/A"}
                  </Td>
                  <Td>
                    <ActionsMenu type={"Purchase"} value={purchase} />
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

function Purchases() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Purchases Management
      </Heading>

      <Navbar type={"Purchase"} addModalAs={AddPurchase} />
      <PurchasesTable />
    </Container>
  )
}
