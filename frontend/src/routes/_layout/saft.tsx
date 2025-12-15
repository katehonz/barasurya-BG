import { Button, Container, Heading, VStack, Text, useToast } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"
import { useState } from "react"

import { SaftService } from "../../client"

export const Route = createFileRoute("/_layout/saft")({
  component: Saft,
})

function Saft() {
  const { t } = useTranslation()
  const toast = useToast()
  const [isLoading, setIsLoading] = useState(false)

  const handleDownloadSaft = async () => {
    setIsLoading(true)
    try {
      const response = await SaftService.downloadSaft()
      const blob = new Blob([response as BlobPart], { type: "application/xml" })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = "SAF-T.xml"
      a.click()
      window.URL.revokeObjectURL(url)
      toast({
        title: t("saft.downloadSuccess"),
        status: "success",
        duration: 3000,
      })
    } catch (error) {
      toast({
        title: t("saft.downloadError"),
        status: "error",
        duration: 3000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        {t("saft.title")}
      </Heading>

      <Text mt={4} color="gray.600">
        {t("saft.description")}
      </Text>

      <VStack spacing={4} mt={8} align="start">
        <Button
          colorScheme="blue"
          onClick={handleDownloadSaft}
          isLoading={isLoading}
        >
          {t("saft.downloadSaft")}
        </Button>
      </VStack>
    </Container>
  )
}
