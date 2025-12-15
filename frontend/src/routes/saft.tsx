import {
  Box,
  Button,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
} from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
// import { Api } from "../client/sdk.gen"; // TODO: Add SAFT service to SDK

export const Route = createFileRoute("/saft")({
  component: SaftComponent,
});

function SaftComponent() {
  // TODO: Re-enable when SAFT service is implemented
  const safts: { id: string }[] = [];

  // const mutation = useMutation({
  //   mutationFn: (newSaft: any) => Api.createSaft(newSaft),
  //   onSuccess: () => {
  //     queryClient.invalidateQueries({ queryKey: ["safts"] });
  //   },
  // });

  const handleCreateSaft = () => {
    // TODO: Implement when SAFT service is ready
    console.log("SAFT creation not implemented yet");
  };

  return (
    <Box>
      <Heading mb={4}>SAF-T</Heading>
      <Button onClick={handleCreateSaft} mb={4}>
        Create SAF-T Report
      </Button>
      <TableContainer>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>ID</Th>
              <Th>Created At</Th>
            </Tr>
          </Thead>
          <Tbody>
            {safts?.map((saft: { id: string }) => (
              <Tr key={saft.id}>
                <Td>{saft.id}</Td>
                <Td>{/* TODO: Add created at date */}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    </Box>
  );
}