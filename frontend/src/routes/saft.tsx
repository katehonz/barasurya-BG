import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Select,
  VStack,
  useToast,
} from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"

export const Route = createFileRoute("/saft")({
  component: Saft,
})

function Saft() {
  const [reportType, setReportType] = useState("monthly")
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [isLoading, setIsLoading] = useState(false)
  const toast = useToast()

  const handleDownload = async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams({
        report_type: reportType,
        year: year.toString(),
      })
      if (reportType === "monthly" && month) {
        params.append("month", month.toString())
      }
      const response = await fetch(`/api/v1/saft?${params.toString()}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      if (!response.ok) {
        throw new Error("Failed to download SAF-T file")
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `saft_${reportType}_${year}${reportType === "monthly" ? "_" + month : ""}.xml`
      document.body.appendChild(a)
      a.click()
      a.remove()
      toast({
        title: "Успех",
        description: "SAF-T файлът е изтеглен успешно.",
        status: "success",
        duration: 5000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: "Грешка",
        description: "Неуспешно изтегляне на SAF-T файл.",
        status: "error",
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const months = [
    { value: 1, label: "Януари" },
    { value: 2, label: "Февруари" },
    { value: 3, label: "Март" },
    { value: 4, label: "Април" },
    { value: 5, label: "Май" },
    { value: 6, label: "Юни" },
    { value: 7, label: "Юли" },
    { value: 8, label: "Август" },
    { value: 9, label: "Септември" },
    { value: 10, label: "Октомври" },
    { value: 11, label: "Ноември" },
    { value: 12, label: "Декември" },
  ]

  return (
    <Container maxW="container.md" py={8}>
      <VStack spacing={8} align="stretch">
        <Heading size="lg" textAlign="center">
          SAF-T Експорт
        </Heading>

        <Box
          p={6}
          borderWidth="1px"
          borderRadius="lg"
          bg="white"
          _dark={{ bg: "gray.800" }}
          shadow="sm"
        >
          <VStack spacing={4}>
            <FormControl>
              <FormLabel>Тип на справката</FormLabel>
              <Select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
              >
                <option value="monthly">Месечна</option>
                <option value="annual">Годишна</option>
                <option value="on_demand">По заявка</option>
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel>Година</FormLabel>
              <Input
                type="number"
                value={year}
                onChange={(e) => setYear(parseInt(e.target.value))}
                min={2020}
                max={2030}
              />
            </FormControl>

            {reportType === "monthly" && (
              <FormControl>
                <FormLabel>Месец</FormLabel>
                <Select
                  value={month}
                  onChange={(e) => setMonth(parseInt(e.target.value))}
                >
                  {months.map((m) => (
                    <option key={m.value} value={m.value}>
                      {m.label}
                    </option>
                  ))}
                </Select>
              </FormControl>
            )}

            <Button
              colorScheme="blue"
              onClick={handleDownload}
              isLoading={isLoading}
              loadingText="Изтегляне..."
              width="full"
              mt={4}
            >
              Изтегли SAF-T файл
            </Button>
          </VStack>
        </Box>
      </VStack>
    </Container>
  )
}
