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
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { InvoicesService } from "../../client" // TODO: Replace with PurchasesService
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddPurchase from "../../components/Invoices/AddPurchase"
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx"

const purchasesSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/purchases")({
  component: Purchases,
  validateSearch: (search) => purchasesSearchSchema.parse(search),
})

const PER_PAGE = 10

function getPurchasesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      InvoicesService.readInvoices({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }), // TODO: Replace with PurchasesService
    queryKey: ["purchases", { page }],
  }
}

function PurchasesTable() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev: { page: number }) => ({ ...prev, page }) })

  const {
    data: purchases,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getPurchasesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

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
              <Th>{t("purchases.invoiceNo")}</Th>
              <Th>{t("purchases.supplier")}</Th>
              <Th>{t("purchases.status")}</Th>
              <Th>{t("purchases.total")}</Th>
              <Th>{t("purchases.issueDate")}</Th>
              <Th>{t("common.actions")}</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(6).fill(null).map((_, index) => (
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
                  <Td>{purchase.invoice_no}</Td>
                  <Td>{purchase.contact.name}</Td>
                  <Td>{purchase.status}</Td>
                  <Td>{purchase.total_amount}</Td>
                  <Td>
                    {new Date(purchase.issue_date).toLocaleDateString()}
                  </Td>
                  <Td>
                    <ActionsMenu
                      type="Purchase"
                      value={purchase}
                      actions={[
                        {
                          label: t("purchases.downloadPdf"),
                          onClick: async () => {
                            // TODO: Replace with PurchasesService.downloadPurchasePdf
                            const response =
                              await InvoicesService.downloadInvoicePdf({
                                id: purchase.id,
                              })
                            const blob = new Blob([response as BlobPart], {
                              type: "application/pdf",
                            })
                            const url = window.URL.createObjectURL(blob)
                            const a = document.createElement("a")
                            a.href = url
                            a.download = `purchase-${purchase.invoice_no}.pdf`
                            a.click()
                            window.URL.revokeObjectURL(url)
                          },
                        },
                      ]}
                    />
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
  const { t } = useTranslation()
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        {t("purchases.title")}
      </Heading>

      <Navbar type="Purchase" addModalAs={AddPurchase} />
      <PurchasesTable />
    </Container>
  )
}
