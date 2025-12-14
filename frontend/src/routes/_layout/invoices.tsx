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
  useDisclosure,
} from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { InvoicesService } from "../../client"
import ActionsMenu from "../../components/Common/ActionsMenu"
import Navbar from "../../components/Common/Navbar"
import AddInvoice from "../../components/Invoices/AddInvoice"
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx"

const invoicesSearchSchema = z.object({
  page: z.number().catch(1),
})

export const Route = createFileRoute("/_layout/invoices")({
  component: Invoices,
  validateSearch: (search) => invoicesSearchSchema.parse(search),
})

const PER_PAGE = 10

function getInvoicesQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      InvoicesService.readInvoices({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["invoices", { page }],
  }
}

function InvoicesTable() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const { page } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })
  const setPage = (page: number) =>
    navigate({ search: (prev) => ({ ...prev, page }) })

  const {
    data: invoices,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getInvoicesQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const hasNextPage = !isPlaceholderData && invoices?.data.length === PER_PAGE
  const hasPreviousPage = page > 1

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(getInvoicesQueryOptions({ page: page + 1 }))
    }
  }, [page, queryClient, hasNextPage])

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>{t("invoices.invoiceNo")}</Th>
              <Th>{t("invoices.customer")}</Th>
              <Th>{t("invoices.status")}</Th>
              <Th>{t("invoices.total")}</Th>
              <Th>{t("invoices.issueDate")}</Th>
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
              {invoices?.data.map((invoice) => (
                <Tr key={invoice.id} opacity={isPlaceholderData ? 0.5 : 1}>
                  <Td>{invoice.invoice_no}</Td>
                  <Td>{invoice.contact.name}</Td>
                  <Td>{invoice.status}</Td>
                  <Td>{invoice.total_amount}</Td>
                  <Td>
                    {new Date(invoice.issue_date).toLocaleDateString()}
                  </Td>
                  <Td>
                    <ActionsMenu
                      type="Invoice"
                      value={invoice}
                      actions={[
                        {
                          label: t("invoices.downloadPdf"),
                          onClick: async () => {
                            const response =
                              await InvoicesService.downloadInvoicePdf({
                                id: invoice.id,
                              })
                            const blob = new Blob([response], {
                              type: "application/pdf",
                            })
                            const url = window.URL.createObjectURL(blob)
                            const a = document.createElement("a")
                            a.href = url
                            a.download = `invoice-${invoice.invoice_no}.pdf`
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

function Invoices() {
  const { t } = useTranslation()
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        {t("invoices.title")}
      </Heading>

      <Navbar type="Invoice" addModalAs={AddInvoice} />
      <InvoicesTable />
    </Container>
  )
}
