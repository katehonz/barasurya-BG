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

import { SalesService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddSale from "../../components/Sales/AddSale"
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx"

const salesSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/sales")({
  component: Sales,
  validateSearch: (search) => salesSearchSchema.parse(search),
})

const PER_PAGE = 5

function getSalesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      SalesService.readSales({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["sales", { page }],
  }
}

function SalesTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev: {[key: string]: string}) => ({ ...prev, page }) })

  const {
    data: sales,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getSalesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  // debug
  useEffect(() => {
    console.log("Sales:", sales)
  }, [sales])

  const hasNextPage = !isPlaceholderData && sales?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getSalesQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>ID</Th>
              <Th>Date Sale</Th>
              <Th>Amount</Th>
              <Th>Description</Th>
              <Th>Customer Name</Th>
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
              {sales?.data.map((sale) => (
                <Tr key={sale.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{sale.id}</Td>
                  <Td
                    color={!sale.date_sale ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {sale.date_sale || "N/A"}
                  </Td>
                  <Td
                    color={!sale.amount ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {sale.amount || "N/A"}
                  </Td>
                  <Td
                    color={!sale.description ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {sale.description || "N/A"}
                  </Td>
                  <Td
                    color={!sale.customer_name ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {sale.customer_name || "N/A"}
                  </Td>
                  <Td
                    color={!sale.store_name ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {sale.store_name || "N/A"}
                  </Td>
                  <Td
                    color={!sale.date_created ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {sale.date_created || "N/A"}
                  </Td>
                  <Td
                    color={!sale.date_updated ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {sale.date_updated || "N/A"}
                  </Td>
                  <Td>
                    <ActionsMenu type={"Sale"} value={sale} />
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

function Sales() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Sales Management
      </Heading>

      <Navbar type={"Sale"} addModalAs={AddSale} />
      <SalesTable />
    </Container>
  )
}
