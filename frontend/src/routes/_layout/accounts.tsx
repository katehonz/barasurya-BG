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

import { AccountsService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddAccount from "../../components/Accounts/AddAccount.tsx"
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx"

const accountsSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/accounts")({
  component: Accounts,
  validateSearch: (search) => accountsSearchSchema.parse(search),
})

const PER_PAGE = 5

function getAccountsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      AccountsService.readAccounts({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["accounts", { page }],
  }
}

function AccountsTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev: {[key: string]: string}) => ({ ...prev, page }) })

  const {
    data: accounts,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getAccountsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && accounts?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getAccountsQueryOptions({ page: page + 1 }))
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
              <Th>Balance</Th>
              <Th>Description</Th>
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
              {accounts?.data.map((account) => (
                <Tr key={account.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{account.id}</Td>
                  <Td isTruncated maxWidth="150px">
                    {account.name}
                  </Td>
                  <Td
                    color={!account.balance ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {account.balance || "N/A"}
                  </Td>
                  <Td
                    color={!account.description ? "ui.dim" : "inherit"}
                    isTruncated
                    maxWidth="150px"
                  >
                    {account.description || "N/A"}
                  </Td>
                  <Td>
                    <ActionsMenu type={"Account"} value={account} />
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

function Accounts() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Accounts Management
      </Heading>

      <Navbar type={"Account"} addModalAs={AddAccount} />
      <AccountsTable />
    </Container>
  )
}
