import {
  Badge,
  Box,
  Container,
  Heading,
  SkeletonText,
  Stat,
  StatGroup,
  StatLabel,
  StatNumber,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { z } from "zod"

import { AssetsService } from "../../client"
import AddAsset from "../../components/Assets/AddAsset"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import { PaginationFooter } from "../../components/Common/PaginationFooter"

const assetsSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/assets")({
  component: Assets,
  validateSearch: (search) => assetsSearchSchema.parse(search),
})

const PER_PAGE = 10

function getAssetsQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      AssetsService.listAssets({
        skip: (page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
    queryKey: ["assets", { page }],
  }
}

function formatCurrency(value: number | undefined | null): string {
  if (value === undefined || value === null) return "-"
  return new Intl.NumberFormat("bg-BG", {
    style: "currency",
    currency: "BGN",
  }).format(value)
}

function getStatusBadge(status: string | undefined) {
  switch (status) {
    case "active":
      return <Badge colorScheme="green">Активен</Badge>
    case "disposed":
      return <Badge colorScheme="red">Изведен</Badge>
    case "suspended":
      return <Badge colorScheme="yellow">Спрян</Badge>
    default:
      return <Badge>{status}</Badge>
  }
}

function getCategoryLabel(category: string | null | undefined): string {
  const categories: Record<string, string> = {
    computers: "Компютри",
    furniture: "Мебели",
    vehicles: "Транспорт",
    machinery: "Машини",
    buildings: "Сгради",
    land: "Земя",
    software: "Софтуер",
    other: "Други",
  }
  return category ? categories[category] || category : "-"
}

function AssetsStatistics() {
  const { data: stats, isPending } = useQuery({
    queryKey: ["assets-statistics"],
    queryFn: () => AssetsService.getAssetStatistics(),
  })

  if (isPending) {
    return <SkeletonText noOfLines={2} />
  }

  const statsData = stats as {
    total_count?: number;
    active_count?: number;
    disposed_count?: number;
    total_acquisition_cost?: string;
    total_book_value?: string;
  } | undefined

  return (
    <Box mb={6} p={4} bg="gray.50" borderRadius="md" _dark={{ bg: "gray.700" }}>
      <StatGroup>
        <Stat>
          <StatLabel>Общо активи</StatLabel>
          <StatNumber>{statsData?.total_count || 0}</StatNumber>
        </Stat>
        <Stat>
          <StatLabel>Активни</StatLabel>
          <StatNumber color="green.500">{statsData?.active_count || 0}</StatNumber>
        </Stat>
        <Stat>
          <StatLabel>Изведени</StatLabel>
          <StatNumber color="red.500">{statsData?.disposed_count || 0}</StatNumber>
        </Stat>
        <Stat>
          <StatLabel>Обща стойност</StatLabel>
          <StatNumber fontSize="lg">
            {formatCurrency(parseFloat(statsData?.total_acquisition_cost || "0"))}
          </StatNumber>
        </Stat>
        <Stat>
          <StatLabel>Балансова стойност</StatLabel>
          <StatNumber fontSize="lg">
            {formatCurrency(parseFloat(statsData?.total_book_value || "0"))}
          </StatNumber>
        </Stat>
      </StatGroup>
    </Box>
  )
}

function AssetsTable() {
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const {
    data: assets,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getAssetsQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && assets?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getAssetsQueryOptions({ page: page + 1 }))
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
              <Th>Категория</Th>
              <Th>Инв. номер</Th>
              <Th isNumeric>Първ. стойност</Th>
              <Th>Дата придоб.</Th>
              <Th>Статус</Th>
              <Th>Действия</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(8).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {assets?.data.length === 0 ? (
                <Tr>
                  <Td colSpan={8}>
                    <Text textAlign="center" py={4} color="gray.500">
                      Няма намерени дълготрайни активи
                    </Text>
                  </Td>
                </Tr>
              ) : (
                assets?.data.map((asset) => (
                  <Tr key={asset.id} opacity={isPlaceholderData ? 0.5 : 1}>
                    <Td>
                      <Text fontWeight="medium">{asset.code}</Text>
                    </Td>
                    <Td>
                      <Text isTruncated maxWidth="200px" title={asset.name}>
                        {asset.name}
                      </Text>
                    </Td>
                    <Td>{getCategoryLabel(asset.category)}</Td>
                    <Td>{asset.inventory_number || "-"}</Td>
                    <Td isNumeric>{formatCurrency(asset.acquisition_cost)}</Td>
                    <Td>{asset.acquisition_date}</Td>
                    <Td>{getStatusBadge(asset.status)}</Td>
                    <Td>
                      <ActionsMenu type={"Asset"} value={asset} />
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

function Assets() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Дълготрайни материални активи
      </Heading>

      <AssetsStatistics />
      <Navbar type={"Asset"} addModalAs={AddAsset} />
      <AssetsTable />
    </Container>
  )
}
