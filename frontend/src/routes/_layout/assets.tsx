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

const PER_PAGE = 5

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
              <Th>ID</Th>
              <Th>Code</Th>
              <Th>Name</Th>
              <Th>Acquisition Date</Th>
              <Th>Acquisition Cost</Th>
              <Th>Status</Th>
              <Th>Actions</Th>
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
              {assets?.data.map((asset) => (
                <Tr key={asset.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{asset.id}</Td>
                  <Td>{asset.code}</Td>
                  <Td isTruncated maxWidth="150px">
                    {asset.name}
                  </Td>
                  <Td>{asset.acquisition_date}</Td>
                  <Td>{asset.acquisition_cost}</Td>
                  <Td>{asset.status}</Td>
                  <Td>
                    <ActionsMenu type={"Asset"} value={asset} />
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

function Assets() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Assets Management
      </Heading>

      <Navbar type={"Asset"} addModalAs={AddAsset} />
      <AssetsTable />
    </Container>
  )
}
