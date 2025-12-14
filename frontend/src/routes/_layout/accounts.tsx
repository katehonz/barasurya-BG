import {
  Badge,
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

import { AccountsService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddAccount from "../../components/Accounts/AddAccount"
import { PaginationFooter } from "../../components/Common/PaginationFooter"

const accountsSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/accounts")({
  component: Accounts,
  validateSearch: (search) => accountsSearchSchema.parse(search),
})

const PER_PAGE = 15

function getAccountsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      AccountsService.readAccounts({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["accounts", { page }],
  }
}

function formatCurrency(value: string | number | undefined | null): string {
  if (value === undefined || value === null) return "0.00 лв."
  const numValue = typeof value === "string" ? parseFloat(value) : value
  return new Intl.NumberFormat("bg-BG", {
    style: "currency",
    currency: "BGN",
  }).format(numValue)
}

function getAccountTypeBadge(type: string | undefined) {
  const types: Record<string, { label: string; color: string }> = {
    asset: { label: "Актив", color: "blue" },
    liability: { label: "Пасив", color: "orange" },
    equity: { label: "Капитал", color: "purple" },
    revenue: { label: "Приход", color: "green" },
    expense: { label: "Разход", color: "red" },
  }
  const info = type ? types[type] : null
  return info ? (
    <Badge colorScheme={info.color}>{info.label}</Badge>
  ) : (
    <Badge>{type}</Badge>
  )
}

function AccountsTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev: { [key: string]: string }) => ({ ...prev, page }) })

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
              <Th>Код</Th>
              <Th>Наименование</Th>
              <Th>Тип</Th>
              <Th isNumeric>Нач. салдо</Th>
              <Th>Дебитна</Th>
              <Th>Статус</Th>
              <Th>Действия</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(7).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {accounts?.data.length === 0 ? (
                <Tr>
                  <Td colSpan={7}>
                    <Text textAlign="center" py={4} color="gray.500">
                      Няма намерени сметки
                    </Text>
                  </Td>
                </Tr>
              ) : (
                accounts?.data.map((account) => (
                  <Tr key={account.id} opacity={isPlaceholderData ? 0.5 : 1}>
                    <Td>
                      <Text fontWeight="bold" fontFamily="mono">
                        {account.code}
                      </Text>
                    </Td>
                    <Td>
                      <Text isTruncated maxWidth="200px" title={account.name}>
                        {account.name}
                      </Text>
                    </Td>
                    <Td>{getAccountTypeBadge(account.account_type)}</Td>
                    <Td isNumeric>{formatCurrency(account.opening_balance)}</Td>
                    <Td>
                      {account.is_debit_account ? (
                        <Badge colorScheme="cyan">Дт</Badge>
                      ) : (
                        <Badge colorScheme="pink">Кт</Badge>
                      )}
                    </Td>
                    <Td>
                      {account.is_active ? (
                        <Badge colorScheme="green">Активна</Badge>
                      ) : (
                        <Badge colorScheme="gray">Неактивна</Badge>
                      )}
                    </Td>
                    <Td>
                      <ActionsMenu type={"Account"} value={account} />
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

function Accounts() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Сметкоплан
      </Heading>

      <Navbar type={"Account"} addModalAs={AddAccount} />
      <AccountsTable />
    </Container>
  )
}
