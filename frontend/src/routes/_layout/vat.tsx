import { Button, Container, Heading, VStack } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"

import { VatService } from "../../client"

export const Route = createFileRoute("/_layout/vat")({
  component: Vat,
})

function Vat() {
  const { t } = useTranslation()

  const handleDownloadSalesRegister = async () => {
    const response = await VatService.downloadSalesRegister()
    const blob = new Blob([response], { type: "text/plain" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "PRODAGBI.TXT"
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const handleDownloadPurchaseRegister = async () => {
    const response = await VatService.downloadPurchaseRegister()
    const blob = new Blob([response], { type: "text/plain" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "POKUPKI.TXT"
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const handleDownloadVatDeclaration = async () => {
    const response = await VatService.downloadVatDeclaration()
    const blob = new Blob([response], { type: "text/plain" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "DEKLAR.TXT"
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        {t("vat.title")}
      </Heading>

      <VStack spacing={4} mt={8}>
        <Button onClick={handleDownloadSalesRegister}>
          {t("vat.downloadSalesRegister")}
        </Button>
        <Button onClick={handleDownloadPurchaseRegister}>
          {t("vat.downloadPurchaseRegister")}
        </Button>
        <Button onClick={handleDownloadVatDeclaration}>
          {t("vat.downloadVatDeclaration")}
        </Button>
      </VStack>
    </Container>
  )
}
