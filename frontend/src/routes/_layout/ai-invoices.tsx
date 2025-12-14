import { Container, Heading, Tabs, TabList, TabPanels, Tab, TabPanel } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"

import InvoiceUpload from "../../components/AIInvoices/InvoiceUpload"
import InvoiceReview from "../../components/AIInvoices/InvoiceReview"

export const Route = createFileRoute("/_layout/ai-invoices")({
  component: AIInvoices,
})

function AIInvoices() {
  const { t } = useTranslation()

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12} pb={6}>
        {t("aiInvoices.title")}
      </Heading>

      <Tabs colorScheme="blue" variant="enclosed">
        <TabList>
          <Tab>{t("aiInvoices.upload")}</Tab>
          <Tab>{t("aiInvoices.review")}</Tab>
        </TabList>

        <TabPanels>
          <TabPanel px={0}>
            <InvoiceUpload />
          </TabPanel>
          <TabPanel px={0}>
            <InvoiceReview />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Container>
  )
}
