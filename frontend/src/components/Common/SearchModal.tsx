import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Input,
  InputGroup,
  InputLeftElement,
  Icon,
  Button,
  VStack,
  Text,
  Spinner,
  Box,
  Flex,
} from "@chakra-ui/react"
import { FaSearch } from "react-icons/fa"
import { useState, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"

interface SearchModalProps<T> {
  isOpen: boolean
  onClose: () => void
  title: string
  searchFun: (query: string) => Promise<T[]>
  onSelect: (item: T) => void
  displayFields: { key: keyof T; label?: string; format?: (value: any) => string }[]
  // Optional debounce delay for search input
  debounceDelay?: number
}

export default function SearchModal<T extends { id: any }>({
  isOpen,
  onClose,
  title,
  searchFun,
  onSelect,
  displayFields,
  debounceDelay = 300,
}: SearchModalProps<T>) {
  const [searchTerm, setSearchTerm] = useState("")
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("")

  // Debounce search term
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm)
    }, debounceDelay)
    return () => clearTimeout(handler)
  }, [searchTerm, debounceDelay])

  const { data, isLoading } = useQuery({
    queryKey: ["searchModal", debouncedSearchTerm],
    queryFn: () => searchFun(debouncedSearchTerm),
    enabled: isOpen && debouncedSearchTerm.length > 2, // Only search if modal is open and term is long enough
  })

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{title}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <InputGroup mb={4}>
            <InputLeftElement pointerEvents="none">
              <Icon as={FaSearch} color="gray.300" />
            </InputLeftElement>
            <Input
              placeholder="Search..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>

          {isLoading ? (
            <Flex justify="center" align="center" minH="100px">
              <Spinner />
            </Flex>
          ) : (
            <VStack align="stretch" spacing={2} maxHeight="300px" overflowY="auto">
              {data && data.length > 0 ? (
                data.map((item) => (
                  <Box
                    key={item.id}
                    p={3}
                    borderWidth="1px"
                    borderRadius="md"
                    _hover={{ bg: "gray.50", cursor: "pointer" }}
                    onClick={() => onSelect(item)}
                  >
                    {displayFields.map((field, idx) => (
                      <Text key={idx}>
                        {field.label && <Text as="span" fontWeight="bold">{field.label}: </Text>}
                        {field.format ? field.format(item[field.key]) : String(item[field.key])}
                      </Text>
                    ))}
                  </Box>
                ))
              ) : (
                <Text textAlign="center" color="gray.500">No results found.</Text>
              )}
            </VStack>
          )}
        </ModalBody>
        <ModalFooter>
          <Button onClick={onClose}>Close</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}