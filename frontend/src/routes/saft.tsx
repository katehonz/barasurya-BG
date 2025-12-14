
import {
  Button,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Select,
  VStack,
  useToast,
} from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

import { Card } from "../components/Common/Card";

export const Route = createFileRoute("/saft")({
  component: Saft,
});

function Saft() {
  const [reportType, setReportType] = useState("monthly");
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  const handleDownload = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        report_type: reportType,
        year: year.toString(),
      });
      if (reportType === "monthly" && month) {
        params.append("month", month.toString());
      }
      const response = await fetch(`/api/v1/saft?${params.toString()}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (!response.ok) {
        throw new Error("Failed to download SAF-T file");
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `saft_${reportType}.xml`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download SAF-T file.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <VStack spacing={8} p={8}>
      <Heading>SAF-T Export</Heading>
      <Card>
        <VStack spacing={4}>
          <FormControl>
            <FormLabel>Report Type</FormLabel>
            <Select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
            >
              <option value="monthly">Monthly</option>
              <option value="annual">Annual</option>
              <option value="on_demand">On Demand</option>
            </Select>
          </FormControl>
          <FormControl>
            <FormLabel>Year</FormLabel>
            <Input
              type="number"
              value={year}
              onChange={(e) => setYear(parseInt(e.target.value))}
            />
          </FormControl>
          {reportType === "monthly" && (
            <FormControl>
              <FormLabel>Month</FormLabel>
              <Input
                type="number"
                value={month}
                onChange={(e) => setMonth(parseInt(e.target.value))}
              />
            </FormControl>
          )}
          <Button
            colorScheme="blue"
            onClick={handleDownload}
            isLoading={isLoading}
          >
            Download
          </Button>
        </VStack>
      </Card>
    </VStack>
  );
}
